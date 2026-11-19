add_library(aureon_core STATIC
    window-management/window_manager.cpp
    workspace/workspace_manager.cpp
    search-engine/search_engine.cpp
    theme-engine/theme_engine.cpp
    notification-engine/notification_engine.cpp
)

target_include_directories(aureon_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}/include
)
