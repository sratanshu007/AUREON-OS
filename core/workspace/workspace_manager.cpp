#include "workspace_manager.h"

namespace aureon::core {

WorkspaceManager::WorkspaceManager() {
    m_workspaces.push_back({1, "Main", true});
    m_workspaces.push_back({2, "Code", false});
    m_workspaces.push_back({3, "Media", false});
}

void WorkspaceManager::addWorkspace(const std::string& name) {
    int nextId = static_cast<int>(m_workspaces.size()) + 1;
    m_workspaces.push_back({nextId, name, false});
}

void WorkspaceManager::switchWorkspace(int id) {
    m_activeId = id;
    for (auto& ws : m_workspaces) {
        ws.isActive = (ws.id == id);
    }
}

int WorkspaceManager::activeWorkspaceId() const {
    return m_activeId;
}

const std::vector<Workspace>& WorkspaceManager::workspaces() const {
    return m_workspaces;
}

} // namespace aureon::core
