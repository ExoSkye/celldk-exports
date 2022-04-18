#include <syscalls.h>

void _start() {
    const char* msg = "Hello, PS3!";
    u32 len = 0;
    sys_tty_write(0, msg, 11, &len);
}
