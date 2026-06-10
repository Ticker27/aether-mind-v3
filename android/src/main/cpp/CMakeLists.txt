cmake_minimum_required(VERSION 3.22)
project("hardware_service" C CXX)

# Hide all symbols by default (stealth)
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_C_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

# Disable exceptions and RTTI (reduce binary size)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-exceptions -fno-rtti -Os -s")
set(CMAKE_C_FLAGS "${CMAKE_FLAGS} -Os -s")

# Source files
add_library(hardware_service SHARED
    libhardware_service.cpp
)

# Android libraries
target_link_libraries(hardware_service
    android
    log
)

# Include directories
target_include_directories(hardware_service PRIVATE
    ${ANDROID_NDK}/sysroot/usr/include
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Strip debug symbols (reduce size + anti-reverse)
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--strip-all -Wl,--gc-sections")
