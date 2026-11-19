#include "search_engine.h"
#include <algorithm>
#include <cctype>

namespace aureon::core {

SearchEngine::SearchEngine() {
    indexApplication("Files", "System", "📁");
    indexApplication("Browser", "Internet", "🌐");
    indexApplication("Terminal", "Development", "⌨️");
    indexApplication("System Settings", "System", "⚙️");
    indexApplication("Aureon Store", "Marketplace", "🛍️");
    indexApplication("Aureon AI", "Intelligence", "✨");
    indexApplication("System Monitor", "Utilities", "📊");
    indexApplication("Notes", "Productivity", "📝");
    indexApplication("Calendar", "Productivity", "📅");
    indexApplication("Calculator", "Utilities", "🔢");
}

void SearchEngine::indexApplication(const std::string& name, const std::string& cat, const std::string& icon) {
    m_items.push_back({name, cat, icon, SearchResultType::Application});
}

std::vector<SearchResult> SearchEngine::search(const std::string& query) const {
    std::vector<SearchResult> results;
    if (query.empty()) return results;

    std::string lq = query;
    std::transform(lq.begin(), lq.end(), lq.begin(), [](unsigned char c){ return std::tolower(c); });

    for (const auto& item : m_items) {
        std::string lname = item.name;
        std::transform(lname.begin(), lname.end(), lname.begin(), [](unsigned char c){ return std::tolower(c); });

        if (lname.find(lq) != std::string::npos) {
            SearchResult res;
            res.id = item.name;
            res.title = item.name;
            res.subtitle = item.category;
            res.type = item.type;
            res.icon = item.icon;
            res.score = (lname.rfind(lq, 0) == 0) ? 1.0f : 0.5f;
            results.push_back(res);
        }
    }

    std::sort(results.begin(), results.end(), [](const SearchResult& a, const SearchResult& b){
        return a.score > b.score;
    });

    return results;
}

} // namespace aureon::core
