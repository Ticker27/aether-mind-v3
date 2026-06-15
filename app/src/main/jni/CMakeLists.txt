cmake_minimum_required(VERSION 3.18.1)
project("aether_brain")
set(CMAKE_CXX_STANDARD 17)

# Only compile existing .cpp files
add_library(aether_brain SHARED
    core/jni_bridge.cpp
)

# Include headers for brain (header-only library)
target_include_directories(aether_brain PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/brain
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)

# Link Android system libraries
target_link_libraries(aether_brain
    log
    android
    jnigraphics
)
