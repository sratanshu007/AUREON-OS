// AUREON OS — macOS Network Service Implementation
// macos_network_service.mm  (Objective-C++)
//
// Real Wi-Fi & Bluetooth using CoreWLAN + IOBluetooth + NetworkExtension.
// Requires frameworks: CoreWLAN, IOBluetooth, NetworkExtension, SystemConfiguration.

#include "macos_network_service.h"

#import <CoreWLAN/CoreWLAN.h>
#import <IOBluetooth/IOBluetooth.h>
#import <SystemConfiguration/SystemConfiguration.h>
#import <Foundation/Foundation.h>

#include <chrono>
#include <iostream>

namespace aureon::platform::macos {

// ─────────────────────────────────────────────────────────────────────────────
// Construction / Destruction
// ─────────────────────────────────────────────────────────────────────────────

MacOSNetworkService::MacOSNetworkService() {
    startMonitoring();
}

MacOSNetworkService::~MacOSNetworkService() {
    stopMonitoring();
}

// ─────────────────────────────────────────────────────────────────────────────
// Wi-Fi
// ─────────────────────────────────────────────────────────────────────────────

NetworkStatus MacOSNetworkService::getWifiStatus() const {
    @autoreleasepool {
        NetworkStatus status{};
        CWWiFiClient  *client   = [CWWiFiClient sharedWiFiClient];
        CWInterface   *iface    = [client interface];

        if (!iface) return status;

        status.isConnected   = (iface.serviceActive && iface.ssid != nil);
        status.activeSSID    = iface.ssid ? std::string([iface.ssid UTF8String]) : "";
        status.signalStrength = (int)iface.rssiValue; // dBm raw; map to 0-100

        // Map RSSI (-50 excellent … -90 poor)
        int rssi = (int)iface.rssiValue;
        int signal = 0;
        if (rssi >= -50)       signal = 100;
        else if (rssi <= -90)  signal = 0;
        else                   signal = (int)((rssi + 90) * 2.5);
        status.signalStrength = signal;

        // IP via SCNetworkReachability / CFNetwork
        // Simple approach: iterate network interfaces
        struct ifaddrs *ifap = nullptr, *ifa = nullptr;
        if (getifaddrs(&ifap) == 0) {
            for (ifa = ifap; ifa; ifa = ifa->ifa_next) {
                if (!ifa->ifa_addr) continue;
                std::string name(ifa->ifa_name);
                if (name.rfind("en", 0) == 0) {
                    if (ifa->ifa_addr->sa_family == AF_INET) {
                        char buf[INET_ADDRSTRLEN];
                        inet_ntop(AF_INET, &((struct sockaddr_in*)ifa->ifa_addr)->sin_addr,
                                  buf, sizeof(buf));
                        status.ipAddress = buf;
                    } else if (ifa->ifa_addr->sa_family == AF_INET6) {
                        char buf[INET6_ADDRSTRLEN];
                        inet_ntop(AF_INET6, &((struct sockaddr_in6*)ifa->ifa_addr)->sin6_addr,
                                  buf, sizeof(buf));
                        status.ipv6Address = buf;
                    }
                }
            }
            freeifaddrs(ifap);
        }

        // VPN detection via SCNetworkConfiguration
        status.isVpnActive = isVpnActive();
        status.vpnName     = getActiveVpnName();

        {
            std::lock_guard<std::mutex> lk(m_mutex);
            m_cachedStatus = status;
        }
        return status;
    }
}

std::vector<WifiNetwork> MacOSNetworkService::getWifiNetworks() {
    @autoreleasepool {
        std::vector<WifiNetwork> networks;
        CWWiFiClient *client = [CWWiFiClient sharedWiFiClient];
        CWInterface  *iface  = [client interface];
        if (!iface) return networks;

        NSError *error = nil;
        NSSet<CWNetwork*> *found = [iface scanForNetworksWithName:nil error:&error];
        if (error || !found) return networks;

        std::string connectedSSID = iface.ssid ? std::string([iface.ssid UTF8String]) : "";

        for (CWNetwork *net in found) {
            WifiNetwork wn;
            wn.ssid           = net.ssid ? std::string([net.ssid UTF8String]) : "<hidden>";
            wn.bssid          = net.bssid ? std::string([net.bssid UTF8String]) : "";
            wn.signalStrength = (int)net.rssiValue;
            wn.channel        = (int)net.wlanChannel.channelNumber;
            wn.isConnected    = (wn.ssid == connectedSSID);

            CWSecurity sec = net.security;
            switch (sec) {
                case kCWSecurityNone:         wn.isSecured = false; wn.securityType = "Open";  break;
                case kCWSecurityWEP:          wn.isSecured = true;  wn.securityType = "WEP";   break;
                case kCWSecurityWPAPersonal:  wn.isSecured = true;  wn.securityType = "WPA";   break;
                case kCWSecurityWPA2Personal: wn.isSecured = true;  wn.securityType = "WPA2";  break;
                case kCWSecurityWPA3Personal: wn.isSecured = true;  wn.securityType = "WPA3";  break;
                case kCWSecurityWPAEnterprise:wn.isSecured = true;  wn.securityType = "WPA-E"; break;
                default:                      wn.isSecured = true;  wn.securityType = "Unknown";
            }
            networks.push_back(std::move(wn));
        }

        // Sort: connected first, then by signal
        std::sort(networks.begin(), networks.end(), [](auto& a, auto& b){
            if (a.isConnected != b.isConnected) return a.isConnected > b.isConnected;
            return a.signalStrength > b.signalStrength;
        });

        if (m_wifiNetworksUpdatedCb) m_wifiNetworksUpdatedCb(networks);
        return networks;
    }
}

bool MacOSNetworkService::connect(const std::string& ssid, const std::string& password) {
    @autoreleasepool {
        CWWiFiClient *client = [CWWiFiClient sharedWiFiClient];
        CWInterface  *iface  = [client interface];
        if (!iface) return false;

        NSString *nsSSID = [NSString stringWithUTF8String:ssid.c_str()];
        NSString *nsPwd  = password.empty() ? nil : [NSString stringWithUTF8String:password.c_str()];

        // Find the network first
        NSError *error = nil;
        NSSet<CWNetwork*> *found = [iface scanForNetworksWithName:nsSSID error:&error];
        if (error || !found || found.count == 0) return false;

        CWNetwork *target = found.anyObject;
        BOOL ok = [iface associateToNetwork:target password:nsPwd error:&error];
        return (ok && !error);
    }
}

bool MacOSNetworkService::disconnect() {
    @autoreleasepool {
        CWWiFiClient *client = [CWWiFiClient sharedWiFiClient];
        CWInterface  *iface  = [client interface];
        if (!iface) return false;
        [iface disassociate];
        return true;
    }
}

bool MacOSNetworkService::setWifiEnabled(bool enabled) {
    @autoreleasepool {
        CWWiFiClient *client = [CWWiFiClient sharedWiFiClient];
        CWInterface  *iface  = [client interface];
        if (!iface) return false;
        NSError *error = nil;
        BOOL ok = [iface setPower:enabled error:&error];
        return (ok && !error);
    }
}

bool MacOSNetworkService::isWifiEnabled() const {
    @autoreleasepool {
        CWWiFiClient *client = [CWWiFiClient sharedWiFiClient];
        CWInterface  *iface  = [client interface];
        return iface ? iface.powerOn : false;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Bluetooth
// ─────────────────────────────────────────────────────────────────────────────

std::vector<BluetoothDevice> MacOSNetworkService::getBluetoothDevices() const {
    @autoreleasepool {
        std::vector<BluetoothDevice> devices;

        NSArray<IOBluetoothDevice*> *paired = [IOBluetoothDevice pairedDevices];
        for (IOBluetoothDevice *dev in paired) {
            BluetoothDevice bd;
            bd.name        = dev.name ? std::string([dev.name UTF8String]) : "Unknown";
            bd.address     = dev.addressString ?
                             std::string([dev.addressString UTF8String]) : "";
            bd.isPaired    = true;
            bd.isConnected = dev.isConnected;

            // Classify device type from class-of-device major class
            BluetoothClassOfDevice cod = dev.classOfDevice;
            uint32_t major = (cod >> 8) & 0x1F;
            switch (major) {
                case 1:  bd.deviceType = "Computer";     break;
                case 2:  bd.deviceType = "Phone";        break;
                case 4:  bd.deviceType = "Audio/Video";  break;
                case 5:  bd.deviceType = "Peripheral";   break;
                default: bd.deviceType = "Other";
            }
            // Map Audio/Video sub-class
            if (major == 4) {
                uint32_t minor = (cod >> 2) & 0x3F;
                if      (minor == 1 || minor == 2) bd.deviceType = "Headphones";
                else if (minor == 6)               bd.deviceType = "Speaker";
            }

            bd.batteryLevel = -1; // IOBluetooth doesn't expose battery via public API
            devices.push_back(std::move(bd));
        }
        return devices;
    }
}

bool MacOSNetworkService::setBluetoothEnabled(bool enabled) {
    // IOBluetooth does not expose a public API to toggle Bluetooth power
    // on modern macOS without private frameworks. Log a note.
    (void)enabled;
    std::cerr << "[MacOSNetworkService] setBluetoothEnabled: requires private API on macOS 13+\n";
    return false;
}

bool MacOSNetworkService::isBluetoothEnabled() const {
    @autoreleasepool {
        IOBluetoothHostController *ctrl = [IOBluetoothHostController defaultController];
        if (!ctrl) return false;
        return [ctrl powerState] != kBluetoothHCIControllerSleepModeOff;
    }
}

bool MacOSNetworkService::connectBluetoothDevice(const std::string& address) {
    @autoreleasepool {
        NSString *addr = [NSString stringWithUTF8String:address.c_str()];
        IOBluetoothDevice *dev = [IOBluetoothDevice deviceWithAddressString:addr];
        if (!dev) return false;
        IOReturn ret = [dev openConnection];
        return ret == kIOReturnSuccess;
    }
}

bool MacOSNetworkService::disconnectBluetoothDevice(const std::string& address) {
    @autoreleasepool {
        NSString *addr = [NSString stringWithUTF8String:address.c_str()];
        IOBluetoothDevice *dev = [IOBluetoothDevice deviceWithAddressString:addr];
        if (!dev || !dev.isConnected) return false;
        IOReturn ret = [dev closeConnection];
        return ret == kIOReturnSuccess;
    }
}

bool MacOSNetworkService::pairBluetoothDevice(const std::string& address) {
    @autoreleasepool {
        // Pairing requires IOBluetoothDevicePair + delegate; simplified stub
        NSString *addr = [NSString stringWithUTF8String:address.c_str()];
        IOBluetoothDevice *dev = [IOBluetoothDevice deviceWithAddressString:addr];
        if (!dev) return false;
        IOBluetoothDevicePair *pair = [IOBluetoothDevicePair pairWithDevice:dev];
        IOReturn ret = [pair start];
        return ret == kIOReturnSuccess;
    }
}

bool MacOSNetworkService::unpairBluetoothDevice(const std::string& address) {
    @autoreleasepool {
        NSString *addr = [NSString stringWithUTF8String:address.c_str()];
        IOBluetoothDevice *dev = [IOBluetoothDevice deviceWithAddressString:addr];
        if (!dev) return false;
        IOReturn ret = [dev removeFromDevicesList];
        return ret == kIOReturnSuccess;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// VPN
// ─────────────────────────────────────────────────────────────────────────────

bool MacOSNetworkService::isVpnActive() const {
    @autoreleasepool {
        SCPreferencesRef prefs = SCPreferencesCreate(nullptr, CFSTR("aureon"), nullptr);
        if (!prefs) return false;

        CFArrayRef services = SCNetworkServiceCopyAll(prefs);
        bool vpnActive = false;

        if (services) {
            CFIndex count = CFArrayGetCount(services);
            for (CFIndex i = 0; i < count && !vpnActive; ++i) {
                SCNetworkServiceRef svc =
                    (SCNetworkServiceRef)CFArrayGetValueAtIndex(services, i);
                SCNetworkInterfaceRef iface = SCNetworkServiceGetInterface(svc);
                if (!iface) continue;
                CFStringRef type = SCNetworkInterfaceGetInterfaceType(iface);
                if (type && (CFStringCompare(type, CFSTR("PPP"), 0) == kCFCompareEqualTo ||
                             CFStringCompare(type, CFSTR("VPN"), 0) == kCFCompareEqualTo ||
                             CFStringCompare(type, CFSTR("IPSec"), 0) == kCFCompareEqualTo)) {
                    vpnActive = true;
                }
            }
            CFRelease(services);
        }
        CFRelease(prefs);
        return vpnActive;
    }
}

std::string MacOSNetworkService::getActiveVpnName() const {
    @autoreleasepool {
        SCPreferencesRef prefs = SCPreferencesCreate(nullptr, CFSTR("aureon"), nullptr);
        if (!prefs) return "";
        std::string name;

        CFArrayRef services = SCNetworkServiceCopyAll(prefs);
        if (services) {
            CFIndex count = CFArrayGetCount(services);
            for (CFIndex i = 0; i < count && name.empty(); ++i) {
                SCNetworkServiceRef svc =
                    (SCNetworkServiceRef)CFArrayGetValueAtIndex(services, i);
                SCNetworkInterfaceRef iface = SCNetworkServiceGetInterface(svc);
                if (!iface) continue;
                CFStringRef type = SCNetworkInterfaceGetInterfaceType(iface);
                if (type && (CFStringCompare(type, CFSTR("PPP"), 0) == kCFCompareEqualTo ||
                             CFStringCompare(type, CFSTR("VPN"), 0) == kCFCompareEqualTo)) {
                    CFStringRef svcName = SCNetworkServiceGetName(svc);
                    if (svcName) {
                        char buf[256];
                        CFStringGetCString(svcName, buf, sizeof(buf), kCFStringEncodingUTF8);
                        name = buf;
                    }
                }
            }
            CFRelease(services);
        }
        CFRelease(prefs);
        return name;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Callbacks / Monitoring
// ─────────────────────────────────────────────────────────────────────────────

void MacOSNetworkService::onNetworkChanged(NetworkChangedCallback cb) {
    std::lock_guard<std::mutex> lk(m_mutex);
    m_networkChangedCb = std::move(cb);
}

void MacOSNetworkService::onWifiNetworksUpdated(WifiNetworksCallback cb) {
    std::lock_guard<std::mutex> lk(m_mutex);
    m_wifiNetworksUpdatedCb = std::move(cb);
}

void MacOSNetworkService::startMonitoring() {
    m_running = true;
    m_monitorThread = std::thread([this]{ monitorLoop(); });
}

void MacOSNetworkService::stopMonitoring() {
    m_running = false;
    if (m_monitorThread.joinable()) m_monitorThread.join();
}

void MacOSNetworkService::monitorLoop() {
    while (m_running) {
        NetworkStatus current = getWifiStatus();
        NetworkChangedCallback cb;
        {
            std::lock_guard<std::mutex> lk(m_mutex);
            cb = m_networkChangedCb;
        }
        if (cb) cb(current);

        // Poll every 5 seconds
        for (int i = 0; i < 50 && m_running; ++i) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }
}

} // namespace aureon::platform::macos
