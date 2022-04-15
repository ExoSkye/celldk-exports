cmake_minimum_required(VERSION 3.0)
project(ps3dk-syscalls ASM C)

file(GLOB_RECURSE SPEC_FILES LIST_DIRECTORIES false RELATIVE specs **.json)

add_custom_command(
        OUTPUT generated/syscalls.S generated/syscalls.h
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMAND python3 ${CMAKE_SOURCE_DIR}/generate.py
        DEPENDS ${SPEC_FILES} generate.py
)

add_library(ps3dk-syscalls generated/syscalls.S generated/syscalls.h)
