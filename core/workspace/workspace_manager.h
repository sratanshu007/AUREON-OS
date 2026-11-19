#pragma once
#include <string>
#include <vector>

namespace aureon::core {

struct Workspace {
    int id;
    std::string name;
    bool isActive{false};
};

class WorkspaceManager {
public:
    WorkspaceManager();
    void addWorkspace(const std::string& name);
    void switchWorkspace(int id);
    int activeWorkspaceId() const;
    const std::vector<Workspace>& workspaces() const;

private:
    std::vector<Workspace> m_workspaces;
    int m_activeId{1};
};

} // namespace aureon::core
