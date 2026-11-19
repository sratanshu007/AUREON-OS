// AUREON OS — Platform Service Interfaces
// service_interface.h
//
// Pure abstract C++ interfaces for all platform services.
// Each platform (macOS, Linux) provides concrete implementations.
// The shell and core components program only to these interfaces.

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace aureon::platform {

// ─────────────────────────────────────────────────────────────────────────────
// Common data structures
// ─────────────────────────────────────────────────────────────────────────────

struct WifiNetwork {
    std::string ssid;
    std::string bssid;
    int         signalStrength;   // dBm
    int         channel;
    bool        isSecured;
    bool        isConnected;
    std::string securityType;     // "WPA2", "WPA3", "Open", etc.
};

struct BluetoothDevice {
    std::string name;
    std::string address;
    bool        isPaired;
    bool        isConnected;
    std::string deviceType;       // "Headphones", "Keyboard", "Mouse", etc.
    int         batteryLevel;     // -1 if unknown
};

struct NetworkStatus {
    bool        isConnected;
    std::string activeSSID;
    std::string ipAddress;
    std::string ipv6Address;
    std::string gateway;
    std::string dns;
    bool        isVpnActive;
    std::string vpnName;
    bool        isMetered;
    int         signalStrength;   // 0-100
};

struct Screen {
    std::string id;
    std::string name;
    int         width;
    int         height;
    int         x;
    int         y;
    double      scaleFactor;
    int         refreshRate;
    bool        isPrimary;
    bool        isBuiltin;
};

struct Resolution {
    int width;
    int height;
    int refreshRate;
};

struct AudioDevice {
    std::string id;
    std::string name;
    bool        isDefault;
    bool        isInput;
    bool        isOutput;
    bool        isMuted;
    int         volume;           // 0-100
    std::string deviceType;      // "Speaker", "Headphones", "Microphone", etc.
};

struct BatteryInfo {
    int         level;             // 0-100
    bool        isCharging;
    bool        isPluggedIn;
    int         timeToFullMinutes; // -1 if discharging or unknown
    int         timeToEmptyMinutes;// -1 if charging or unknown
    double      voltage;
    double      temperature;
    std::string health;           // "Good", "Replace Soon", "Replace Now"
};

enum class PowerMode {
    Performance,
    Balanced,
    PowerSaver,
    Custom
};

struct Notification {
    std::string id;
    std::string appId;
    std::string appName;
    std::string title;
    std::string body;
    std::string iconPath;
    int64_t     timestamp;         // Unix ms
    int         priority;          // 0=low, 1=normal, 2=high, 3=critical
    bool        persistent;
    std::vector<std::pair<std::string,std::string>> actions; // {id, label}
};

struct FileEntry {
    std::string path;
    std::string name;
    bool        isDirectory;
    bool        isSymlink;
    bool        isHidden;
    int64_t     size;             // bytes
    int64_t     modifiedTime;     // Unix ms
    int64_t     createdTime;      // Unix ms
    std::string mimeType;
    std::string permissions;      // "rwxr-xr-x"
};

enum class Permission {
    Notifications,
    Location,
    Camera,
    Microphone,
    Contacts,
    Calendar,
    FileSystem,
    Bluetooth,
    Network,
    Accessibility
};

enum class PermissionStatus {
    Granted,
    Denied,
    NotDetermined,
    Restricted
};

// ─────────────────────────────────────────────────────────────────────────────
// INetworkService
// ─────────────────────────────────────────────────────────────────────────────

class INetworkService {
public:
    virtual ~INetworkService() = default;

    // Wi-Fi
    virtual NetworkStatus              getWifiStatus() const = 0;
    virtual std::vector<WifiNetwork>   getWifiNetworks() = 0; // triggers scan
    virtual bool connect(const std::string& ssid, const std::string& password) = 0;
    virtual bool disconnect() = 0;
    virtual bool setWifiEnabled(bool enabled) = 0;
    virtual bool isWifiEnabled() const = 0;

    // Bluetooth
    virtual std::vector<BluetoothDevice> getBluetoothDevices() const = 0;
    virtual bool setBluetoothEnabled(bool enabled) = 0;
    virtual bool isBluetoothEnabled() const = 0;
    virtual bool connectBluetoothDevice(const std::string& address) = 0;
    virtual bool disconnectBluetoothDevice(const std::string& address) = 0;
    virtual bool pairBluetoothDevice(const std::string& address) = 0;
    virtual bool unpairBluetoothDevice(const std::string& address) = 0;

    // VPN
    virtual bool        isVpnActive() const = 0;
    virtual std::string getActiveVpnName() const = 0;

    // Change callbacks
    using NetworkChangedCallback = std::function<void(const NetworkStatus&)>;
    using WifiNetworksCallback   = std::function<void(const std::vector<WifiNetwork>&)>;

    virtual void onNetworkChanged(NetworkChangedCallback cb) = 0;
    virtual void onWifiNetworksUpdated(WifiNetworksCallback cb) = 0;
};

using INetworkServicePtr = std::shared_ptr<INetworkService>;

// ─────────────────────────────────────────────────────────────────────────────
// IDisplayService
// ─────────────────────────────────────────────────────────────────────────────

class IDisplayService {
public:
    virtual ~IDisplayService() = default;

    virtual int                      getBrightness() const = 0;         // 0-100
    virtual bool                     setBrightness(int level) = 0;
    virtual bool                     setNightModeEnabled(bool enabled) = 0;
    virtual bool                     isNightModeEnabled() const = 0;
    virtual int                      getNightModeTemperature() const = 0; // 1000-6500 K
    virtual bool                     setNightModeTemperature(int kelvin) = 0;

    virtual std::vector<Screen>      getScreens() const = 0;
    virtual Screen                   getPrimaryScreen() const = 0;
    virtual std::vector<Resolution>  getAvailableResolutions(const std::string& screenId) const = 0;
    virtual bool                     setResolution(const std::string& screenId, const Resolution& res) = 0;
    virtual bool                     setRefreshRate(const std::string& screenId, int hz) = 0;
    virtual bool                     setPrimaryScreen(const std::string& screenId) = 0;
    virtual bool                     setScreenEnabled(const std::string& screenId, bool enabled) = 0;
    virtual bool                     setScreenPosition(const std::string& screenId, int x, int y) = 0;
    virtual bool                     setScaleFactor(const std::string& screenId, double factor) = 0;

    using ScreenChangedCallback = std::function<void(const std::vector<Screen>&)>;
    virtual void onScreenConfigurationChanged(ScreenChangedCallback cb) = 0;
};

using IDisplayServicePtr = std::shared_ptr<IDisplayService>;

// ─────────────────────────────────────────────────────────────────────────────
// IAudioService
// ─────────────────────────────────────────────────────────────────────────────

class IAudioService {
public:
    virtual ~IAudioService() = default;

    // Master output
    virtual int  getVolume() const = 0;         // 0-100
    virtual bool setVolume(int level) = 0;
    virtual bool isMuted() const = 0;
    virtual bool setMuted(bool muted) = 0;

    // Input (microphone)
    virtual int  getInputVolume() const = 0;
    virtual bool setInputVolume(int level) = 0;
    virtual bool isInputMuted() const = 0;
    virtual bool setInputMuted(bool muted) = 0;

    // Devices
    virtual std::vector<AudioDevice> getOutputDevices() const = 0;
    virtual std::vector<AudioDevice> getInputDevices() const = 0;
    virtual AudioDevice              getDefaultOutputDevice() const = 0;
    virtual AudioDevice              getDefaultInputDevice() const = 0;
    virtual bool                     setOutputDevice(const std::string& deviceId) = 0;
    virtual bool                     setInputDevice(const std::string& deviceId) = 0;

    using AudioChangedCallback = std::function<void()>;
    virtual void onVolumeChanged(AudioChangedCallback cb) = 0;
    virtual void onDevicesChanged(AudioChangedCallback cb) = 0;
};

using IAudioServicePtr = std::shared_ptr<IAudioService>;

// ─────────────────────────────────────────────────────────────────────────────
// IPowerService
// ─────────────────────────────────────────────────────────────────────────────

class IPowerService {
public:
    virtual ~IPowerService() = default;

    virtual BatteryInfo getBatteryInfo() const = 0;
    virtual bool        hasBattery() const = 0;

    virtual PowerMode   getPowerMode() const = 0;
    virtual bool        setPowerMode(PowerMode mode) = 0;

    virtual bool        sleep() = 0;
    virtual bool        displaySleep() = 0;
    virtual bool        shutdown() = 0;
    virtual bool        restart() = 0;
    virtual bool        logOut() = 0;
    virtual bool        lockScreen() = 0;

    virtual int         getDisplaySleepTimeout() const = 0;   // seconds
    virtual bool        setDisplaySleepTimeout(int seconds) = 0;
    virtual int         getSystemSleepTimeout() const = 0;
    virtual bool        setSystemSleepTimeout(int seconds) = 0;

    using BatteryChangedCallback = std::function<void(const BatteryInfo&)>;
    virtual void onBatteryChanged(BatteryChangedCallback cb) = 0;
};

using IPowerServicePtr = std::shared_ptr<IPowerService>;

// ─────────────────────────────────────────────────────────────────────────────
// INotificationService
// ─────────────────────────────────────────────────────────────────────────────

class INotificationService {
public:
    virtual ~INotificationService() = default;

    virtual bool        sendNotification(const Notification& notif) = 0;
    virtual bool        dismissNotification(const std::string& id) = 0;
    virtual bool        dismissAll() = 0;

    virtual std::vector<Notification> getHistory() const = 0;
    virtual void                      clearHistory() = 0;

    virtual bool            isDoNotDisturbEnabled() const = 0;
    virtual bool            setDoNotDisturb(bool enabled) = 0;
    virtual void            setDoNotDisturbSchedule(int startHour, int startMin,
                                                    int endHour,   int endMin) = 0;

    virtual PermissionStatus requestPermission(const std::string& appId) = 0;
    virtual PermissionStatus getPermissionStatus(const std::string& appId) const = 0;
    virtual bool             revokePermission(const std::string& appId) = 0;

    using NotificationCallback = std::function<void(const Notification&)>;
    using ActionCallback       = std::function<void(const std::string& notifId,
                                                    const std::string& actionId)>;
    virtual void onNotificationReceived(NotificationCallback cb) = 0;
    virtual void onNotificationAction(ActionCallback cb) = 0;
};

using INotificationServicePtr = std::shared_ptr<INotificationService>;

// ─────────────────────────────────────────────────────────────────────────────
// IFileService
// ─────────────────────────────────────────────────────────────────────────────

class IFileService {
public:
    virtual ~IFileService() = default;

    virtual std::vector<FileEntry> listDirectory(const std::string& path,
                                                  bool showHidden = false) const = 0;
    virtual std::optional<FileEntry> getEntry(const std::string& path) const = 0;

    virtual std::string readFile(const std::string& path) const = 0;
    virtual bool        writeFile(const std::string& path, const std::string& content,
                                  bool createParents = true) = 0;
    virtual bool        appendFile(const std::string& path, const std::string& content) = 0;
    virtual bool        deleteFile(const std::string& path) = 0;
    virtual bool        deleteDirectory(const std::string& path, bool recursive = false) = 0;
    virtual bool        moveFile(const std::string& src, const std::string& dst) = 0;
    virtual bool        copyFile(const std::string& src, const std::string& dst,
                                 bool overwrite = false) = 0;
    virtual bool        createDirectory(const std::string& path, bool createParents = true) = 0;
    virtual bool        exists(const std::string& path) const = 0;
    virtual bool        isDirectory(const std::string& path) const = 0;
    virtual int64_t     getFileSize(const std::string& path) const = 0;

    virtual std::string getHomeDirectory() const = 0;
    virtual std::string getDesktopDirectory() const = 0;
    virtual std::string getDocumentsDirectory() const = 0;
    virtual std::string getDownloadsDirectory() const = 0;
    virtual std::string getTempDirectory() const = 0;

    // File watching
    using FileWatchCallback = std::function<void(const std::string& path,
                                                  const std::string& event)>;
    virtual int  watchPath(const std::string& path, FileWatchCallback cb,
                           bool recursive = false) = 0;
    virtual void unwatchPath(int watchId) = 0;
};

using IFileServicePtr = std::shared_ptr<IFileService>;

// ─────────────────────────────────────────────────────────────────────────────
// IPermissionService
// ─────────────────────────────────────────────────────────────────────────────

class IPermissionService {
public:
    virtual ~IPermissionService() = default;

    virtual PermissionStatus requestPermission(const std::string& appId,
                                               Permission permission) = 0;
    virtual PermissionStatus getPermissionStatus(const std::string& appId,
                                                 Permission permission) const = 0;
    virtual bool             revokePermission(const std::string& appId,
                                              Permission permission) = 0;
    virtual std::vector<std::pair<Permission, PermissionStatus>>
                             getAllPermissions(const std::string& appId) const = 0;

    using PermissionChangedCallback = std::function<void(const std::string& appId,
                                                          Permission permission,
                                                          PermissionStatus status)>;
    virtual void onPermissionChanged(PermissionChangedCallback cb) = 0;
};

using IPermissionServicePtr = std::shared_ptr<IPermissionService>;

// ─────────────────────────────────────────────────────────────────────────────
// IPlatformServiceFactory
// Factory that creates all platform-specific service implementations.
// ─────────────────────────────────────────────────────────────────────────────

class IPlatformServiceFactory {
public:
    virtual ~IPlatformServiceFactory() = default;

    virtual INetworkServicePtr      createNetworkService() = 0;
    virtual IDisplayServicePtr      createDisplayService() = 0;
    virtual IAudioServicePtr        createAudioService() = 0;
    virtual IPowerServicePtr        createPowerService() = 0;
    virtual INotificationServicePtr createNotificationService() = 0;
    virtual IFileServicePtr         createFileService() = 0;
    virtual IPermissionServicePtr   createPermissionService() = 0;

    static std::unique_ptr<IPlatformServiceFactory> createForCurrentPlatform();
};

} // namespace aureon::platform
