# PS3DK-Exports

This repository contains source files to generate the assembly files and header files used in PS3DK for calling syscalls and PRX exports, this includes the specifications (`specs` folder) which contain the specifications of the syscalls in JSON format. `generate.py` is used to add specs or generate the source files.

The `generate.py` script can be used to add specifications by running it with any arguments. For example, if the first argument anything other than `add` then that is used as the filename.

Also, if the `generate.py` script is passed `upgrade` as the only argument, then it will automatically update all the JSON files to schema-compatible versions of themselves - currently this only moves `id` into `ids` as `syscall_id`.

To use this script, you need to have `clang-format` installed on your machine and available in path.

## Example flow
This is an example flow for adding a spec and generating the source files:
```
$ python3 generate.py add
File name: process_get_sdk_version.json
Function name [sys_process_get_sdk_version]: 
ID: 25
Return type [void]: int
Description: Returns the SDK version of a process
Class [sys_process]: 
Parameter 1 name: pid
Parameter 1 type: sys_pid_t
Parameter 1 description: The PID of the process you want to get the SDK Version of
Parameter 2 name: version
Parameter 2 type: u32*
Parameter 2 description: The pointer to the u32 which the SDK Version will be written to
Parameter 3 name: 
Does this function work on CEX (y/n): y
Does this function work on DEX (y/n): y
Does this function work on DECR (y/n): y
Enter a required flag: root
Enter a required flag:
```
Any blank entry (pressing enter without typing any input) will either error and retry or user the default option (depending if there is a default option available, usually denoted by `[...]` in the prompt.

This then generates this JSON file in `specs`:
```json
{
  "name": "sys_process_get_sdk_version",
  "id": 25,
  "returns": "int",
  "brief": "Returns the SDK version of a process",
  "class": "sys_process",
  "params": [
    {
      "name": "pid",
      "type": "sys_pid_t",
      "description": "The PID of the process you want to get the SDK Version of"
    },
    {
      "name": "version",
      "type": "u32*",
      "description": "The pointer to the u32 which the SDK Version will be written to"
    }
  ],
  "flags": [
    "root"
  ],
  "firmwares": [
    "CEX",
    "DEX",
    "DECR"
  ]
}
```
This then generates these source files when parsed by the generator (running `generate.py` with no arguments):

`sys_process.h`:
```h
#include <ppu_types.h>

/*! \brief Returns the SDK version of a process
           To use this syscall, the caller process must have this flag: root. This syscall works on: CEX, DEX, DECR firmwares
* \param pid The PID of the process you want to get the SDK Version of
* \param version The pointer to the u32 which the SDK Version will be written to
*/

int sys_process_get_sdk_version(sys_pid_t pid, u32* version);
```
`syscalls.h`:
```h
#ifndef LV2_SYSCALLS_H
#define LV2_SYSCALLS_H

#include "sys_process.h"

#endif
```
`syscalls.S`:
```
.globl   sys_process_get_sdk_version

sys_process_get_sdk_version:
    li, r11  25
    sc
    blr
```
