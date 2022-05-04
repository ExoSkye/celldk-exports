cmake_minimum_required(VERSION 3.0)
project(celldk-exports C ASM)

if (NOT DEFINED CELLDK_ROOT)
    message(FATAL_ERROR "CellDK requires CELLDK_ROOT to be set in a CMake variable")
endif()


add_subdirectory(generated)