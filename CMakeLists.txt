cmake_minimum_required(VERSION 3.20)

# [Build Type]
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE "Debug" CACHE STRING "Build type" FORCE)
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# [CMake]
set(DOWNLOAD_EXTRACT_TIMESTAMP true)
include(FetchContent)

# [Styio] Version
project(styio VERSION 0.0.1)

list(APPEND CMAKE_MODULE_PATH
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake"
  "${CMAKE_CURRENT_SOURCE_DIR}"
)

option(STYIO_USE_ICU "Enable ICU-backed Unicode handling for StyioUnicode and CLI option text" OFF)
option(STYIO_BUILD_NANO "Build the profile-pruned styio-nano compiler target" ON)
option(STYIO_NANO_OPTIMIZE_FOR_SIZE "Compile styio-nano with size-oriented optimization flags when supported" ON)
option(STYIO_ENABLE_TREE_SITTER "Enable the generated Tree-sitter syntax backend for styio_ide_core" ON)
set(STYIO_NANO_PROFILE "${CMAKE_SOURCE_DIR}/configs/styio-nano-default.toml" CACHE FILEPATH
    "Path to the styio-nano profile TOML used to configure the styio-nano target")

# [Styio] Build Output Directory
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

message(STATUS "[Styio] Source: " ${PROJECT_SOURCE_DIR})
message(STATUS "[Styio] Binary: " ${PROJECT_BINARY_DIR})
message(STATUS "[Styio] Archive: " ${CMAKE_ARCHIVE_OUTPUT_DIRECTORY})
message(STATUS "[Styio] Library: " ${CMAKE_LIBRARY_OUTPUT_DIRECTORY})
message(STATUS "[Styio] Runtime: " ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

include(StyioLLVM)
include(StyioTreeSitter)
include(StyioNanoProfile)

add_subdirectory(src)

include(StyioICU)

enable_testing()
include(StyioGoogleTest)

add_subdirectory(tests)
add_subdirectory(benchmark)
