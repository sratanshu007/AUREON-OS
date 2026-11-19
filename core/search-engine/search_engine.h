#pragma once
#include <string>
#include <vector>

namespace aureon::core {

enum class SearchResultType {
    Application,
    File,
    Setting,
    Web
};

struct SearchResult {
    std::string id;
    std::string title;
    std::string subtitle;
    SearchResultType type;
    std::string icon;
    float score{0.0f};
};

class SearchEngine {
public:
    SearchEngine();
    void indexApplication(const std::string& name, const std::string& cat, const std::string& icon);
    std::vector<SearchResult> search(const std::string& query) const;

private:
    struct SearchItem {
        std::string name;
        std::string category;
        std::string icon;
        SearchResultType type;
    };
    std::vector<SearchItem> m_items;
};

} // namespace aureon::core
