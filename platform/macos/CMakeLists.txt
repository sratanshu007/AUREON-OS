if(APPLE)
  add_library(aureon_platform_macos STATIC macos_network_service.mm macos_power_service.mm)
  target_link_libraries(aureon_platform_macos PUBLIC aureon_platform_shared "-framework Foundation" "-framework CoreWLAN" "-framework IOKit")
endif()
