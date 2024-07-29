
cmake_minimum_required(VERSION 3.24)

### Setup project name and language
project(EFFBORR VERSION 1.2
        DESCRIPTION "A CMake project template"
        HOMEPAGE_URL "https://github.com/DavidAce/CMakeTemplate"
        LANGUAGES C CXX)


### Set up options
option(EFFBORR_ENABLE_COVERAGE "Adds the --coverage flag (used with github actions)"  OFF)
option(EFFBORR_BUILD_BENCH     "Builds benchmarks in ./bench"                         OFF)
option(EFFBORR_BUILD_EXAMPLES  "Builds examples in ./examples"                        OFF)
option(EFFBORR_BUILD_TESTS     "Builds unit tests in ./tests"                         OFF)
option(EFFBORR_CMAKE_DEBUG     "Print info during CMake configuration"                OFF)



if(EFFBORR_DEBUG_CMAKE)
    ### Print operating system details
    include(cmake/PrintHostInfo.cmake)
endif()

### Add all source files
add_executable(EFFBORR
        source/main.cpp 
        source/rnd.cpp
        source/cli.cpp
        source/io.cpp
)

target_include_directories(EFFBORR PRIVATE source)


### Find dependencies
find_package(h5pp       1.11.1  REQUIRED)
find_package(pcg-cpp            REQUIRED)
find_package(nanobench  4.3.11  REQUIRED)
find_package(CLI11      2.3.2   REQUIRED)


### Create a helper target that links dependencies (this target can be used to build tests and benchmarks)
add_library(effborr-libs INTERFACE)

# Link the libraries to the helper target
target_link_libraries(effborr-libs INTERFACE h5pp::h5pp)
target_link_libraries(effborr-libs INTERFACE pcg-cpp::pcg-cpp )
target_link_libraries(effborr-libs INTERFACE nanobench::nanobench)
target_link_libraries(effborr-libs INTERFACE CLI11::CLI11)


### Link targets to the main executable
target_link_libraries(EFFBORR PUBLIC effborr-libs)


################################################################
### Get git version number                                   ###
### Generates a header gitversion/gitversion.h               ###
### Include it using #include <gitversion.h>                 ###
### Gives a namespace GIT:: with several git identifiers     ###
################################################################
include(cmake/gitversion.cmake)

#add_subdirectory(bench)    # Builds benchmarks if EFFBORR_BUILD_BENCH==ON
add_subdirectory(examples) # Builds examples if EFFBORR_BUILD_EXAMPLES==ON


### CTest
if(EFFBORR_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
    if(EFFBORR_ENABLE_COVERAGE)
        # Coverage is used to check what fraction of the source code is tested
        # We use this option in the github actions when compiling on Ubuntu with gcc
        target_compile_options(effborr-libs INTERFACE --coverage)
        target_link_options(effborr-libs INTERFACE --coverage)
    endif()
endif()


if(EFFBORR_CMAKE_DEBUG)
    # Print summary of CMake configuration
    include(cmake/PrintTargetInfo.cmake)
    print_and_write_project_summary(EFFBORR)
endif()
