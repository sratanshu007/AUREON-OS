#include <iostream>
#include <string>

namespace aureon::platform::linux {

class LinuxPowerService {
public:
    int getBatteryLevel() const { return 94; }
    bool isCharging() const { return true; }
    void sleep() { std::cout << "[LinuxPowerService] logind Suspend()" << std::endl; }
    void restart() { std::cout << "[LinuxPowerService] logind Reboot()" << std::endl; }
    void shutdown() { std::cout << "[LinuxPowerService] logind PowerOff()" << std::endl; }
};

} // namespace aureon::platform::linux
