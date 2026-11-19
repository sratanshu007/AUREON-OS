#include <iostream>
#include <vector>
#include <string>

namespace aureon::platform::linux {

class LinuxAudioService {
public:
    int getVolume() const { return 78; }
    void setVolume(int vol) { std::cout << "[LinuxAudioService] PipeWire set volume: " << vol << std::endl; }
    std::vector<std::string> getOutputDevices() const {
        return {"PipeWire ALSA Output (Direct)", "HDMI / DisplayPort Audio", "Bluetooth A2DP Sink"};
    }
};

} // namespace aureon::platform::linux
