cmake_minimum_required(VERSION 3.25)
project(
    AureonOS
    VERSION 1.0.0
    DESCRIPTION "AUREON OS — Premium Cross-Platform Desktop Environment"
    HOMEPAGE_URL "https://aureon.dev"
    LANGUAGES CXX C
)

# ============================================================
#  Global C++ Standard
# ============================================================
set(CMAKE_CXX_STANDARD          20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS        OFF)

# ============================================================
#  CMake module path
# ============================================================
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules")

# ============================================================
#  Build options
# ============================================================
option(AUREON_ENABLE_TESTS         "Build unit and integration tests"       ON)
option(AUREON_ENABLE_SANITIZERS    "Enable address/UB sanitizers (dev)"     OFF)
option(AUREON_ENABLE_COVERAGE      "Enable code-coverage instrumentation"   OFF)
option(AUREON_ENABLE_LTO           "Enable link-time optimisation"          OFF)
option(AUREON_STATIC_LINK          "Statically link Qt and third-party libs" OFF)
option(AUREON_ENABLE_AI_LOCAL      "Build with on-device AI inference"      ON)
option(AUREON_ENABLE_WAYLAND       "Enable Wayland compositor support"      ON)
option(AUREON_ENABLE_X11           "Enable X11 fallback support"            ON)
option(AUREON_DEVELOPER_MODE       "Enable developer overlay and debug UI"  OFF)
option(AUREON_BUILD_INSTALLER      "Build platform installer targets"       OFF)
option(AUREON_USE_SYSTEM_LIBS      "Prefer system-installed libraries"      OFF)
option(AUREON_CCACHE               "Use ccache if available"                ON)

# ============================================================
#  ccache
# ============================================================
if(AUREON_CCACHE)
    find_program(CCACHE_PROGRAM ccache)
    if(CCACHE_PROGRAM)
        set(CMAKE_CXX_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
        set(CMAKE_C_COMPILER_LAUNCHER   "${CCACHE_PROGRAM}")
        message(STATUS "[Aureon] ccache enabled: ${CCACHE_PROGRAM}")
    endif()
endif()

# ============================================================
#  Link-time optimisation
# ============================================================
if(AUREON_ENABLE_LTO)
    include(CheckIPOSupported)
    check_ipo_supported(RESULT IPO_SUPPORTED OUTPUT IPO_OUTPUT)
    if(IPO_SUPPORTED)
        set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
        message(STATUS "[Aureon] LTO enabled")
    else()
        message(WARNING "[Aureon] LTO not supported: ${IPO_OUTPUT}")
    endif()
endif()

# ============================================================
#  Sanitizers
# ============================================================
if(AUREON_ENABLE_SANITIZERS)
    if(NOT MSVC)
        set(SANITIZER_FLAGS "-fsanitize=address,undefined -fno-omit-frame-pointer")
        string(APPEND CMAKE_CXX_FLAGS " ${SANITIZER_FLAGS}")
        string(APPEND CMAKE_C_FLAGS   " ${SANITIZER_FLAGS}")
        string(APPEND CMAKE_EXE_LINKER_FLAGS " ${SANITIZER_FLAGS}")
        message(STATUS "[Aureon] Sanitizers: address + UB")
    else()
        message(WARNING "[Aureon] Sanitizers not supported on MSVC")
    endif()
endif()

# ============================================================
#  Coverage
# ============================================================
if(AUREON_ENABLE_COVERAGE)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        string(APPEND CMAKE_CXX_FLAGS " --coverage")
        string(APPEND CMAKE_C_FLAGS   " --coverage")
        string(APPEND CMAKE_EXE_LINKER_FLAGS " --coverage")
        message(STATUS "[Aureon] Code coverage enabled")
    endif()
endif()

# ============================================================
#  Qt6 — mandatory components
# ============================================================
set(AUREON_QT_COMPONENTS
    Core
    Gui
    Widgets
    Quick
    QuickControls2
    QuickWidgets
    Qml
    QmlModels
    Network
    NetworkAuth
    DBus
    Multimedia
    MultimediaWidgets
    Sql
    Svg
    WebSockets
    Concurrent
    OpenGL
    OpenGLWidgets
    PrintSupport
    Test
)

if(WIN32)
    list(APPEND AUREON_QT_COMPONENTS WinExtras)
endif()

find_package(Qt6 6.5 REQUIRED COMPONENTS ${AUREON_QT_COMPONENTS})

qt_standard_project_setup()

# ============================================================
#  Third-party dependencies
# ============================================================

# --- nlohmann/json (header-only) -------
find_package(nlohmann_json 3.11 QUIET)
if(NOT nlohmann_json_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        nlohmann_json
        GIT_REPOSITORY https://github.com/nlohmann/json.git
        GIT_TAG        v3.11.3
        GIT_SHALLOW    TRUE
    )
    FetchContent_MakeAvailable(nlohmann_json)
endif()

# --- spdlog -------
find_package(spdlog 1.12 QUIET)
if(NOT spdlog_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        spdlog
        GIT_REPOSITORY https://github.com/gabime/spdlog.git
        GIT_TAG        v1.13.0
        GIT_SHALLOW    TRUE
    )
    FetchContent_MakeAvailable(spdlog)
endif()

# --- libsecret (Linux keychain) -------
if(UNIX AND NOT APPLE)
    find_package(PkgConfig QUIET)
    if(PKG_CONFIG_FOUND)
        pkg_check_modules(LIBSECRET QUIET libsecret-1)
    endif()
endif()

# ============================================================
#  Platform detection
# ============================================================
set(AUREON_PLATFORM "")
if(APPLE)
    set(AUREON_PLATFORM "macos")
    set(AUREON_PLATFORM_MACOS TRUE)
elseif(WIN32)
    set(AUREON_PLATFORM "windows")
    set(AUREON_PLATFORM_WINDOWS TRUE)
elseif(UNIX)
    set(AUREON_PLATFORM "linux")
    set(AUREON_PLATFORM_LINUX TRUE)
endif()
message(STATUS "[Aureon] Platform: ${AUREON_PLATFORM}")

# ============================================================
#  Version info header
# ============================================================
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/core/version.h.in"
    "${CMAKE_CURRENT_BINARY_DIR}/include/aureon/version.h"
    @ONLY
)

# ============================================================
#  Compile definitions (global)
# ============================================================
add_compile_definitions(
    AUREON_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    AUREON_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    AUREON_VERSION_PATCH=${PROJECT_VERSION_PATCH}
    AUREON_VERSION_STRING="${PROJECT_VERSION}"
    AUREON_PLATFORM_${AUREON_PLATFORM_LABEL}=1
    $<$<BOOL:${AUREON_DEVELOPER_MODE}>:AUREON_DEVELOPER_MODE>
    $<$<CONFIG:Debug>:AUREON_DEBUG>
    $<$<CONFIG:Release>:AUREON_RELEASE>
    $<$<BOOL:${AUREON_ENABLE_AI_LOCAL}>:AUREON_AI_LOCAL>
)

if(AUREON_PLATFORM_MACOS)
    add_compile_definitions(AUREON_PLATFORM_LABEL=MACOS)
elseif(AUREON_PLATFORM_LINUX)
    add_compile_definitions(AUREON_PLATFORM_LABEL=LINUX)
elseif(AUREON_PLATFORM_WINDOWS)
    add_compile_definitions(AUREON_PLATFORM_LABEL=WINDOWS)
endif()

# ============================================================
#  Include directories (global)
# ============================================================
include_directories(
    "${CMAKE_CURRENT_SOURCE_DIR}/aureon"
    "${CMAKE_CURRENT_BINARY_DIR}/include"
)

# ============================================================
#  Subdirectories
# ============================================================
add_subdirectory(core)
add_subdirectory(services)
add_subdirectory(platform/${AUREON_PLATFORM})
add_subdirectory(platform/shared)
add_subdirectory(apps/desktop-shell)
add_subdirectory(apps/files)
add_subdirectory(apps/settings)
add_subdirectory(apps/launcher)
add_subdirectory(apps/search)
add_subdirectory(apps/terminal)
add_subdirectory(apps/browser)
add_subdirectory(apps/ai-assistant)
add_subdirectory(apps/store)
add_subdirectory(apps/calendar)
add_subdirectory(apps/notes)
add_subdirectory(apps/system-monitor)
add_subdirectory(apps/calculator)
add_subdirectory(apps/photos)
add_subdirectory(apps/music)
add_subdirectory(apps/videos)
add_subdirectory(distribution)

# ============================================================
#  Tests
# ============================================================
if(AUREON_ENABLE_TESTS)
    enable_testing()
    find_package(Qt6 REQUIRED COMPONENTS Test)
    add_subdirectory(tests)
    message(STATUS "[Aureon] Tests enabled")
endif()

# ============================================================
#  Packaging (CPack)
# ============================================================
if(AUREON_BUILD_INSTALLER)
    include(cmake/packaging.cmake)
endif()

# ============================================================
#  Summary
# ============================================================
message(STATUS "")
message(STATUS "===== AUREON OS Build Configuration =====")
message(STATUS "  Version      : ${PROJECT_VERSION}")
message(STATUS "  Platform     : ${AUREON_PLATFORM}")
message(STATUS "  Build type   : ${CMAKE_BUILD_TYPE}")
message(STATUS "  Qt version   : ${Qt6_VERSION}")
message(STATUS "  C++ standard : ${CMAKE_CXX_STANDARD}")
message(STATUS "  Tests        : ${AUREON_ENABLE_TESTS}")
message(STATUS "  Sanitizers   : ${AUREON_ENABLE_SANITIZERS}")
message(STATUS "  LTO          : ${AUREON_ENABLE_LTO}")
message(STATUS "  AI local     : ${AUREON_ENABLE_AI_LOCAL}")
message(STATUS "  Wayland      : ${AUREON_ENABLE_WAYLAND}")
message(STATUS "  Dev mode     : ${AUREON_DEVELOPER_MODE}")
message(STATUS "=========================================")
message(STATUS "")
