// AUREON OS — macOS Power Service Implementation
// macos_power_service.mm  (Objective-C++)
//
// IOKit battery, IOPMSleepSystem, CoreServices power management.
// Required frameworks: IOKit, CoreFoundation, AppKit.
// Entitlements required: com.apple.security.device.usb (for IOKit)

#include "macos_power_service.h"

#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>
#import <IOKit/IOKitLib.h>
#import <IOKit/ps/IOPowerSources.h>
#import <IOKit/ps/IOPSKeys.h>
#import <IOKit/pwr_mgt/IOPMLib.h>
#import <IOKit/pwr_mgt/IOPM.h>

#include <chrono>

namespace aureon::platform::macos {

// ─────────────────────────────────────────────────────────────────────────────
// Construction
// ─────────────────────────────────────────────────────────────────────────────

MacOSPowerService::MacOSPowerService() {
    startMonitoring();
}

MacOSPowerService::~MacOSPowerService() {
    stopMonitoring();
}

// ─────────────────────────────────────────────────────────────────────────────
// Battery
// ─────────────────────────────────────────────────────────────────────────────

BatteryInfo MacOSPowerService::getBatteryInfo() const {
    @autoreleasepool {
        BatteryInfo info{};
        info.batteryLevel = -1;

        CFTypeRef psInfo = IOPSCopyPowerSourcesInfo();
        if (!psInfo) return info;

        CFArrayRef sources = IOPSCopyPowerSourcesList(psInfo);
        if (!sources) { CFRelease(psInfo); return info; }

        CFIndex count = CFArrayGetCount(sources);
        for (CFIndex i = 0; i < count; ++i) {
            CFTypeRef src = CFArrayGetValueAtIndex(sources, i);
            CFDictionaryRef dict = IOPSGetPowerSourceDescription(psInfo, src);
            if (!dict) continue;

            // Type check — only battery sources
            CFStringRef type = (CFStringRef)CFDictionaryGetValue(dict, CFSTR(kIOPSTypeKey));
            if (!type || CFStringCompare(type, CFSTR(kIOPSInternalBatteryType), 0) != kCFCompareEqualTo)
                continue;

            // Capacity
            CFNumberRef curCap = (CFNumberRef)CFDictionaryGetValue(dict, CFSTR(kIOPSCurrentCapacityKey));
            CFNumberRef maxCap = (CFNumberRef)CFDictionaryGetValue(dict, CFSTR(kIOPSMaxCapacityKey));
            int cur = 0, max = 100;
            if (curCap) CFNumberGetValue(curCap, kCFNumberIntType, &cur);
            if (maxCap) CFNumberGetValue(maxCap, kCFNumberIntType, &max);
            info.level = max > 0 ? (cur * 100 / max) : 0;

            // Charging state
            CFStringRef state = (CFStringRef)CFDictionaryGetValue(dict, CFSTR(kIOPSPowerSourceStateKey));
            info.isPluggedIn  = (state &&
                CFStringCompare(state, CFSTR(kIOPSACPowerValue), 0) == kCFCompareEqualTo);

            CFBooleanRef charging = (CFBooleanRef)CFDictionaryGetValue(dict, CFSTR(kIOPSIsChargingKey));
            info.isCharging = (charging && CFBooleanGetValue(charging));

            // Time remaining
            CFNumberRef timeToEmpty = (CFNumberRef)CFDictionaryGetValue(dict, CFSTR(kIOPSTimeToEmptyKey));
            CFNumberRef timeToFull  = (CFNumberRef)CFDictionaryGetValue(dict, CFSTR(kIOPSTimeToFullChargeKey));
            int tte = -1, ttf = -1;
            if (timeToEmpty) CFNumberGetValue(timeToEmpty, kCFNumberIntType, &tte);
            if (timeToFull)  CFNumberGetValue(timeToFull,  kCFNumberIntType, &ttf);
            info.timeToEmptyMinutes = tte;
            info.timeToFullMinutes  = ttf;

            // Health
            CFStringRef health = (CFStringRef)CFDictionaryGetValue(dict, CFSTR(kIOPSBatteryHealthKey));
            if (health) {
                char buf[64];
                CFStringGetCString(health, buf, sizeof(buf), kCFStringEncodingUTF8);
                info.health = buf;
            } else {
                info.health = "Good";
            }

            break; // primary battery found
        }

        CFRelease(sources);
        CFRelease(psInfo);

        {
            std::lock_guard<std::mutex> lk(m_mutex);
            m_cachedBattery = info;
        }
        return info;
    }
}

bool MacOSPowerService::hasBattery() const {
    @autoreleasepool {
        CFTypeRef psInfo = IOPSCopyPowerSourcesInfo();
        if (!psInfo) return false;
        CFArrayRef sources = IOPSCopyPowerSourcesList(psInfo);
        bool found = sources && CFArrayGetCount(sources) > 0;
        if (sources) CFRelease(sources);
        CFRelease(psInfo);
        return found;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Power Mode
// ─────────────────────────────────────────────────────────────────────────────

PowerMode MacOSPowerService::getPowerMode() const {
    // macOS 12+ exposes Low Power Mode via NSProcessInfo
    if (@available(macOS 12.0, *)) {
        return [[NSProcessInfo processInfo] isLowPowerModeEnabled]
               ? PowerMode::PowerSaver
               : PowerMode::Balanced;
    }
    return PowerMode::Balanced;
}

bool MacOSPowerService::setPowerMode(PowerMode mode) {
    // Setting Low Power Mode programmatically requires private entitlements on macOS.
    // This is a placeholder; in a shipping product use the Energy Saver preference pane API.
    (void)mode;
    return false;
}

// ─────────────────────────────────────────────────────────────────────────────
// System Actions
// ─────────────────────────────────────────────────────────────────────────────

bool MacOSPowerService::sleep() {
    // IOPMSleepSystem — preferred public API
    io_connect_t powerPort = IO_OBJECT_NULL;
    io_service_t service = IOServiceGetMatchingService(kIOMainPortDefault,
                               IOServiceMatching("IOPMrootDomain"));
    if (!service) return false;
    IOReturn ret = IOServiceOpen(service, mach_task_self(), 0, &powerPort);
    IOObjectRelease(service);
    if (ret != kIOReturnSuccess) return false;
    ret = IOPMSleepSystem(powerPort);
    IOServiceClose(powerPort);
    return ret == kIOReturnSuccess;
}

bool MacOSPowerService::displaySleep() {
    // Dim the display immediately using IOKit
    io_registry_entry_t service =
        IORegistryEntryFromPath(kIOMainPortDefault, "IOService:/IOResources/IODisplayWrangler");
    if (service == MACH_PORT_NULL) return false;
    IOReturn ret = IORegistryEntrySetCFProperty(service, CFSTR("IORequestIdle"), kCFBooleanTrue);
    IOObjectRelease(service);
    return ret == kIOReturnSuccess;
}

bool MacOSPowerService::shutdown() {
    return system("osascript -e 'tell application \"System Events\" to shut down'") == 0;
}

bool MacOSPowerService::restart() {
    return system("osascript -e 'tell application \"System Events\" to restart'") == 0;
}

bool MacOSPowerService::logOut() {
    return system("osascript -e 'tell application \"System Events\" to log out'") == 0;
}

bool MacOSPowerService::lockScreen() {
    return system("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend") == 0;
}

// ─────────────────────────────────────────────────────────────────────────────
// Sleep timeouts via pmset
// ─────────────────────────────────────────────────────────────────────────────

int MacOSPowerService::getDisplaySleepTimeout() const {
    FILE *f = popen("pmset -g | awk '/displaysleep/ {print $2}'", "r");
    if (!f) return -1;
    int val = -1; fscanf(f, "%d", &val); pclose(f);
    return val * 60; // minutes → seconds
}

bool MacOSPowerService::setDisplaySleepTimeout(int seconds) {
    int minutes = seconds / 60;
    char cmd[64]; snprintf(cmd, sizeof(cmd), "pmset displaysleep %d", minutes);
    return system(cmd) == 0;
}

int MacOSPowerService::getSystemSleepTimeout() const {
    FILE *f = popen("pmset -g | awk '/^[ \\t]*sleep/ {print $2}'", "r");
    if (!f) return -1;
    int val = -1; fscanf(f, "%d", &val); pclose(f);
    return val * 60;
}

bool MacOSPowerService::setSystemSleepTimeout(int seconds) {
    int minutes = seconds / 60;
    char cmd[64]; snprintf(cmd, sizeof(cmd), "pmset sleep %d", minutes);
    return system(cmd) == 0;
}

// ─────────────────────────────────────────────────────────────────────────────
// Callbacks / Monitor
// ─────────────────────────────────────────────────────────────────────────────

void MacOSPowerService::onBatteryChanged(BatteryChangedCallback cb) {
    std::lock_guard<std::mutex> lk(m_mutex);
    m_batteryChangedCb = std::move(cb);
}

void MacOSPowerService::startMonitoring() {
    m_running = true;
    m_monitorThread = std::thread([this]{ monitorLoop(); });
}

void MacOSPowerService::stopMonitoring() {
    m_running = false;
    if (m_monitorThread.joinable()) m_monitorThread.join();
}

void MacOSPowerService::monitorLoop() {
    BatteryInfo prev{};
    while (m_running) {
        BatteryInfo cur = getBatteryInfo();
        bool changed = (cur.level != prev.level || cur.isCharging != prev.isCharging);
        if (changed) {
            BatteryChangedCallback cb;
            { std::lock_guard<std::mutex> lk(m_mutex); cb = m_batteryChangedCb; }
            if (cb) cb(cur);
            prev = cur;
        }
        for (int i = 0; i < 300 && m_running; ++i)
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

} // namespace aureon::platform::macos
