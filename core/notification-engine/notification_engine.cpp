#include "notification_engine.h"
#include <chrono>
#include <ctime>

namespace aureon::core {

NotificationEngine::NotificationEngine() {
    postNotification("system", "Welcome to AUREON OS", "Dream. Create. Explore. System is ready.");
}

void NotificationEngine::postNotification(const std::string& appId, const std::string& title, const std::string& body) {
    Notification n;
    n.id = "notif_" + std::to_string(m_nextId++);
    n.appId = appId;
    n.title = title;
    n.body = body;
    n.isRead = false;
    m_notifications.insert(m_notifications.begin(), n);
}

const std::vector<Notification>& NotificationEngine::notifications() const {
    return m_notifications;
}

void NotificationEngine::clearAll() {
    m_notifications.clear();
}

} // namespace aureon::core
