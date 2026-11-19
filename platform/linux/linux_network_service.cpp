#include "linux_network_service.h"
#include <iostream>

namespace aureon::platform::linux {

LinuxNetworkService::LinuxNetworkService() = default;

bool LinuxNetworkService::isWifiEnabled() const {
    return true;
}

std::string LinuxNetworkService::connectedSsid() const {
    return "Aureon-5G-Mesh";
}

std::vector<std::string> LinuxNetworkService::availableSsids() const {
    return {"Aureon-5G-Mesh", "Studio-Fast-6E", "Guest-Aureon"};
}

bool LinuxNetworkService::connectToWifi(const std::string& ssid, const std::string& password) {
    std::cout << "[LinuxNetworkService] Connected to SSID: " << ssid << std::endl;
    return true;
}

} // namespace aureon::platform::linux
