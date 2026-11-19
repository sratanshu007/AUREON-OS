// AUREON OS — macOS Power Service
// macos_power_service.h

#pragma once

#include "../shared/service_interface.h"
#include <atomic>
#include <mutex>
#include <thread>

namespace aureon::platform::macos {

class MacOSPowerService final : public IPowerService {
public:
    MacOSPowerService();
    ~MacOSPowerService() override;

    BatteryInfo getBatteryInfo() const override;
    bool        hasBattery() const override;

    PowerMode   getPowerMode() const override;
    bool        setPowerMode(PowerMode mode) override;

    bool        sleep() override;
    bool        displaySleep() override;
    bool        shutdown() override;
    bool        restart() override;
    bool        logOut() override;
    bool        lockScreen() override;

    int         getDisplaySleepTimeout() const override;
    bool        setDisplaySleepTimeout(int seconds) override;
    int         getSystemSleepTimeout() const override;
    bool        setSystemSleepTimeout(int seconds) override;

    void onBatteryChanged(BatteryChangedCallback cb) override;

private:
    void startMonitoring();
    void stopMonitoring();
    void monitorLoop();

    BatteryChangedCallback m_batteryChangedCb;
    mutable std::mutex     m_mutex;
    std::atomic<bool>      m_running{false};
    std::thread            m_monitorThread;
    mutable BatteryInfo    m_cachedBattery{};
};

} // namespace aureon::platform::macos
