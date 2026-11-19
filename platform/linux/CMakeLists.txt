if(UNIX AND NOT APPLE)
  add_library(aureon_platform_linux STATIC linux_network_service.cpp linux_power_service.cpp linux_audio_service.cpp)
  target_link_libraries(aureon_platform_linux PUBLIC aureon_platform_shared)
endif()
