cmake_minimum_required(VERSION 3.18.1)
project("aether_agent")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")

find_library(log-lib log)
find_library(android-lib android)

file(GLOB_RECURSE SOURCES
    core/*.cpp
    vision/*.cpp
    brain/*.cpp
    humanizer/*.cpp
    execution/*.cpp
)

add_library(aether_agent SHARED ${SOURCES})

target_include_directories(aether_agent PRIVATE ${CMAKE_SOURCE_DIR})

target_link_libraries(aether_agent
    ${log-lib}
    ${android-lib}
    jnigraphics
)
