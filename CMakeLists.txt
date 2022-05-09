cmake_minimum_required(VERSION 3.0)
project(celldk-exports C ASM)

if (NOT DEFINED CELLDK_ROOT)
    message(FATAL_ERROR "CellDK requires CELLDK_ROOT to be set in a CMake variable")
endif()

if (NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    message(FATAL_ERROR "CMAKE_TOOLCHAIN_FILE is required to be set to the CellDK PPU Toolchain file")
endif()

find_package(Python3 COMPONENTS Interpreter REQUIRED)

execute_process(
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/generate.py clean
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

execute_process(
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/generate.py
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_subdirectory(generated)