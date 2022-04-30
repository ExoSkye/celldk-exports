project(CellDK-Syscalls-Test)

add_executable(test main.c)
target_link_libraries(test PRIVATE ps3dk-syscalls)
target_include_directories(test PRIVATE ../generated .)