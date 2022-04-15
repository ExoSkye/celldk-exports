import os
import json
import inspect
from itertools import chain
import sys

def c_generator():
    header_files = {
        "syscalls": inspect.cleandoc("""#ifndef LV2_SYSCALLS_H
            #define LV2_SYSCALLS_H
            """)
        }
    assembly_file = ""

    header_fmt_str = inspect.cleandoc("""
    #define {}_ID {}
    
    /*! \\brief {}
               {}
    {}*/
    
    {} {}({});\n
    """)

    assembly_fmt_str = inspect.cleandoc("""
        .globl  {}
    
    {}:
        li, r11  {}
        sc
        blr
    """)

    files_and_roots = [(files, root) for root, _, files in os.walk("specs", topdown=False)]

    total = len(list(chain(*[files for files, _ in files_and_roots])))
    i = 0

    for files, root in files_and_roots:
        for file in files:
            i += 1
            if file.split(".")[-1] == "json":
                with open(os.path.join(root, file)) as f:
                    spec = json.load(f)

                    if spec['class'] not in header_files.keys():
                        header_files[spec['class']] = "#include <ppu_types.h>\n\n"

                    requirements = ""
                    if len(spec["flags"]) != 0:
                        if len(spec["flags"]) == 1:
                            requirements += "To use this syscall, the caller process must have this flag: {}. ".format(spec["flags"][0])
                        else:
                            requirements += "To use this syscall, the caller process must have any of these flags: {}. ".format(", ".join(spec["flags"]))

                    requirements += "This syscall works on: {} firmwares".format(", ".join(spec["firmwares"]))

                    header_files[spec['class']] += inspect.cleandoc(
                        header_fmt_str.format(
                            spec['name'].upper(), spec['id'],
                            spec['brief'],
                            requirements,
                            "".join([f"* \\param {param['name']} {param['description']}\n" for param in spec["params"]]),
                            spec["returns"], spec['name'], ', '.join([f"{param['type']} {param['name']}" for param in spec["params"]])
                            )
                        )
                    header_files[spec['class']] += "\n\n"

                    assembly_file += inspect.cleandoc(
                        assembly_fmt_str.format(spec['name'],
                                                spec['name'],
                                                spec['id'])
                        )
                    assembly_file += "\n\n"

                    print(f"Parsed {file} ({i}/{total})")


    try:
        os.mkdir("generated")
    except FileExistsError:
        pass

    with open("generated/syscalls.S", mode="w") as f:
        f.write(assembly_file)

    header_files["syscalls"] += "\n"

    for file in [name for name in header_files.keys() if name != "syscalls"]:
        header_files["syscalls"] += '\n#include "{}.h"'.format(file)

    header_files["syscalls"] += "\n"

    header_files["syscalls"] += "\n#endif"

    for file in header_files.keys():
        with open(f"generated/{file}.h", mode="w") as f:
            f.write(header_files[file])

def ask_param(question, default = None, no_response = False):
    if default is not None:
        tmp = input(f"{question} [{default}]: ").strip("\n")
        if tmp == "":
            return default
        else:
            return tmp

    else:
        tmp = input(f"{question}: ").strip("\n")
        if tmp == "" and not no_response:
            print("This parameter is required, please enter a value")
            return ask_param(question, default, no_response)
        elif tmp == "" and no_response:
            return None
        else:
            return tmp


def json_generator(argv):
    if sys.argv[1] != "add":
        fname = sys.argv[1]
    else:
        fname = ask_param("File name")

    func_name = ask_param("Function name", default=f"sys_{fname[:-5]}")

    spec = {
        "name": func_name,
        "id": int(ask_param("ID")),
        "returns": ask_param("Return type", default="void"),
        "brief": ask_param("Description"),
        "class": ask_param("Class", default=f"{'_'.join(func_name.split('_')[:2])}"),
        "params": [],
        "flags": [],
        "firmwares": []
    }

    i = 0

    while True:
        name = ask_param(f"Parameter {i + 1} name", no_response=True)

        if name is None:
            break

        param = {
            "name": name,
            "type": ask_param(f"Parameter {i + 1} type", no_response=True),
            "description": ask_param(f"Parameter {i + 1} description", no_response=True)
        }

        if param["name"] is None or param["type"] is None or param["description"] is None:
            break
        else:
            spec["params"].append(param)

        i += 1

    for firmware in ["CEX", "DEX", "DECR"]:
        if ask_param(f"Does this function work on {firmware} (y/n)") == "y":
            spec["firmwares"].append(firmware)

    while True:
        flag = ask_param("Enter a required flag", no_response=True)

        if flag is None:
            break
        else:
            spec["flags"].append(flag)

    with open(f"specs/{fname}", "w") as f:
        json.dump(spec, f)

if __name__ == '__main__':
    if len(sys.argv) != 1:
        json_generator(sys.argv)
    else:
        c_generator()
