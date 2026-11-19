#pragma once
#include <string>
#include <vector>

namespace aureon::core {

struct Notification {
    std::string id;
    std::string appId;
    std::string title;
    std::string body;
    std::string timestamp;
    bool isRead{false};
};

class NotificationEngine {
public:
    NotificationEngine();
    void postNotification(const std::string& appId, const std::string& title, const std::string& body);
    const std::vector<Notification>& notifications() const;
    void clearAll();

private:
    std::vector<Notification> m_notifications;
    int m_nextId{1};
};

} // namespace aureon::core
