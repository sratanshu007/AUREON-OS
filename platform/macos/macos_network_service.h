// AUREON OS — macOS Network Service
// macos_network_service.h
//
// macOS implementation of INetworkService using CoreWLAN,
// NetworkExtension, and IOBluetooth frameworks.

#pragma once

#include "../shared/service_interface.h"
#include <atomic>
#include <mutex>
#include <thread>

#ifdef __OBJC__
@class CWWiFiClient;
@class IOBluetoothDevice;
#else
typedef void CWWiFiClient;
typedef void IOBluetoothDevice;
#endif

namespace aureon::platform::macos {

class MacOSNetworkService final : public INetworkService {
public:
    MacOSNetworkService();
    ~MacOSNetworkService() override;

    // ── INetworkService ──────────────────────────────────────────────────────

    // Wi-Fi
    NetworkStatus             getWifiStatus() const override;
    std::vector<WifiNetwork>  getWifiNetworks() override;
    bool connect(const std::string& ssid, const std::string& password) override;
    bool disconnect() override;
    bool setWifiEnabled(bool enabled) override;
    bool isWifiEnabled() const override;

    // Bluetooth
    std::vector<BluetoothDevice> getBluetoothDevices() const override;
    bool setBluetoothEnabled(bool enabled) override;
    bool isBluetoothEnabled() const override;
    bool connectBluetoothDevice(const std::string& address) override;
    bool disconnectBluetoothDevice(const std::string& address) override;
    bool pairBluetoothDevice(const std::string& address) override;
    bool unpairBluetoothDevice(const std::string& address) override;

    // VPN
    bool        isVpnActive() const override;
    std::string getActiveVpnName() const override;

    // Callbacks
    void onNetworkChanged(NetworkChangedCallback cb) override;
    void onWifiNetworksUpdated(WifiNetworksCallback cb) override;

private:
    void startMonitoring();
    void stopMonitoring();
    void monitorLoop();

    NetworkChangedCallback   m_networkChangedCb;
    WifiNetworksCallback     m_wifiNetworksUpdatedCb;
    mutable std::mutex       m_mutex;

    std::atomic<bool>        m_running{false};
    std::thread              m_monitorThread;

    // Cached state
    mutable NetworkStatus    m_cachedStatus;
    mutable bool             m_statusDirty{true};
};

} // namespace aureon::platform::macos
