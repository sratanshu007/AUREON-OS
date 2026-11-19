// AUREON OS — Linux Network Service
// linux_network_service.h
//
// Linux implementation using NetworkManager D-Bus + BlueZ D-Bus via QtDBus.

#pragma once

#include "../shared/service_interface.h"
#include <QObject>
#include <QDBusInterface>
#include <QDBusReply>
#include <atomic>
#include <mutex>
#include <thread>

namespace aureon::platform::linux_impl {

class LinuxNetworkService final : public QObject, public INetworkService {
    Q_OBJECT
public:
    explicit LinuxNetworkService(QObject *parent = nullptr);
    ~LinuxNetworkService() override;

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

    void onNetworkChanged(NetworkChangedCallback cb) override;
    void onWifiNetworksUpdated(WifiNetworksCallback cb) override;

private Q_SLOTS:
    void onNMStateChanged(uint state);
    void onNMPropertiesChanged(const QString& interface,
                                const QVariantMap& changed,
                                const QStringList& invalidated);

private:
    std::string nmObjectPathToSSID(const QString& apPath) const;
    uint32_t    nmSecurityFlags(uint32_t flags) const;

    QDBusInterface*    m_nmIface   {nullptr};
    QDBusInterface*    m_nmWifiDev {nullptr};
    mutable std::mutex m_mutex;

    NetworkChangedCallback  m_networkChangedCb;
    WifiNetworksCallback    m_wifiNetworksUpdatedCb;
};

} // namespace aureon::platform::linux_impl
