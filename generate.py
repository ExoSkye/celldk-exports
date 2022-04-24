import os
import json
import inspect
from itertools import chain
import sys
from subprocess import run
import jsonschema
from jsonschema import validate
from enum import Enum


def get_schema():
    with open("schema.json", "r") as f:
        schema = json.load(f)
    return schema


def validate_json(json_data):
    execute_api_schema = get_schema()

    try:
        validate(instance=json_data, schema=execute_api_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False

    return True


class LibType(Enum):
    Syscall = 0
    PRX = 1


class Library:
    def __init__(self, _name: str, _type: LibType):
        self.type = _type
        self.name = _name
        self.files = {}

    def write_to_disk(self, prefix: str):
        try:
            os.mkdir(prefix + self.name)
        except FileExistsError:
            pass

        for file in self.files.keys():
            with open(prefix + self.name + "/" + file, "w") as f:
                f.write(self.files[file])


def c_generator():
    generated_libraries = {}

    header_files = {
        "syscalls": inspect.cleandoc("""#ifndef LV2_SYSCALLS_H
            #define LV2_SYSCALLS_H
            """)
    }
    assembly_file = ""

    header_fmt_str = inspect.cleandoc("""
    // {}
    #define {}_ID {}
    
    /*! \\brief {}.
        {}
    {}*/
    
    {} {}({});\n
    """)

    assembly_fmt_str = inspect.cleandoc("""
        .globl  {}
    
    {}:
        li 11, {}
        sc
        blr
    """)

    cmake_syscall_file = inspect.cleandoc("""
    cmake_minimum_required(VERSION 3.0)
    project({}_syscalls LANGUAGES C ASM)
    
    if(CMAKE_TOOLCHAIN_FILE STREQUAL "")
        message(FATAL_ERROR "The PS3DK Toolchain File must be used to build this library")
    endif()
    
    add_library({}_syscalls STATIC {})
    """)

    cmake_prx_file = inspect.cleandoc("""
    cmake_minimum_required(VERSION 3.0)
    project({}_prx LANGUAGES C)
    
    if(CMAKE_TOOLCHAIN_FILE STREQUAL "")
        message(FATAL_ERROR "The PS3DK Toolchain File must be used to build this library")
    endif()
    
    add_library({}_prx STATIC exports.c)
    """)

    prx_def_file = inspect.cleandoc("""
    EXPORT({}, {})
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
                    if not validate_json(spec):
                        print(f"{file} isn't conformant to the schema, skipping")
                        continue

                    syscall_lib_name = spec["class"] + "_syscalls"
                    prx_lib_name = spec["class"] + "_prx"

                    spec_defines_syscall = spec["ids"].get("syscall_id", None) is not None
                    spec_defines_prx_export = spec["ids"].get("prx_id", None) is not None

                    if spec_defines_syscall and syscall_lib_name not in generated_libraries.keys():
                        generated_libraries[syscall_lib_name] = Library(syscall_lib_name, LibType.Syscall)
                        generated_libraries[syscall_lib_name].files["CMakeLists.txt"] = cmake_syscall_file.format(
                            spec["class"], spec["class"], "{}")

                    if spec_defines_prx_export and prx_lib_name not in generated_libraries.keys():
                        generated_libraries[prx_lib_name] = Library(prx_lib_name, LibType.PRX)
                        generated_libraries[prx_lib_name].files["CMakeLists.txt"] = cmake_prx_file.format(
                            spec["class"], spec["class"])
                        generated_libraries[prx_lib_name].files["exports.c"] = inspect.cleandoc("""
                            #include <sprx_common.h>
                        """) + "\n"

                    requirements = ""
                    if len(spec["flags"]) != 0:
                        requirements += inspect.cleandoc("""
                            Required flags:
                        """)
                        for flag in spec["flags"]:
                            requirements += f"\n- {flag}\n\n"

                    cex_support = "×"
                    dex_support = "×"
                    decr_support = "×"

                    if "CEX" in spec["firmwares"]:
                        cex_support = "✓"

                    if "DEX" in spec["firmwares"]:
                        dex_support = "✓"

                    if "DECR" in spec["firmwares"]:
                        decr_support = "✓"

                    requirements += inspect.cleandoc(f"""
                        Firmware support:
                        |Firmware|Supported|
                        |--------|---------|
                        |CEX|{cex_support}|
                        |DEX|{dex_support}|
                        |DECR|{decr_support}|
                    """)

                    if spec_defines_prx_export:
                        generated_libraries[prx_lib_name].files["exports.c"] += "\n" + prx_def_file.format(
                            "".join([f"{x[0].upper()}{x[1:]}" for x in spec["name"].split("_")]),
                                                spec["ids"]["prx_id"]
                        )

                    # if "syscall_id" in spec["ids"].keys():
                    #     if f"{spec['class']}_syscalls" not in header_files.keys():
                    #         header_files[f"{spec['class']}_syscalls"] = "#include <ppu-types.h>\n\n"
                    #
                    #     header_files[f"{spec['class']}_syscalls"] += inspect.cleandoc(
                    #         header_fmt_str.format(
                    #             file,
                    #             spec['name'].upper(), spec['ids']['syscall_id'],
                    #             spec['brief'],
                    #             "\n" + "".join(
                    #                 [f"{req_line}\n" for req_line in requirements.split("\n")],
                    #             ),
                    #             "".join(
                    #                 [f" * \\param {param['name']} {param['description']}\n" for param in spec["params"]]),
                    #             spec["returns"], spec['name'],
                    #             ', '.join([f"{param['type']} {param['name']}" for param in spec["params"]])
                    #         )
                    #     )
                    #     header_files[f"{spec['class']}_syscalls"] += "\n\n"
                    #
                    #     assembly_file += inspect.cleandoc(
                    #         assembly_fmt_str.format(spec['name'],
                    #                                 spec['name'],
                    #                                 spec['ids']['syscall_id'])
                    #     )
                    #     assembly_file += "\n\n"
                    #
                    print(f"Parsed {file} ({i}/{total} - {int(i / total * 100)}%)")

    try:
        os.mkdir("generated")
        os.mkdir("generated/sprx")
        os.mkdir("generated/syscall")
    except FileExistsError:
        pass

    for lib in generated_libraries.values():
        if lib.type == LibType.PRX:
            lib.write_to_disk("generated/sprx/")
        else:
            lib.write_to_disk("generated/syscall/")


def ask_param(question, default=None, no_response=False):
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


def json_upgrade():
    print("Upgrading JSON files")
    files_and_roots = [(files, root) for root, _, files in os.walk("specs", topdown=False)]

    for files, root in files_and_roots:
        for file in files:
            print(f"Upgrading file: {file}")
            with open(os.path.join(root, file), "r") as f:
                data = json.load(f)

            if "id" in data.keys():
                prx_id = ask_param("PRX ID", no_response=True)

                data["ids"] = {
                    "syscall_id": data["id"]
                }

                if prx_id is not None:
                    data["ids"]["prx_id"] = prx_id

                del data["id"]

            with open(os.path.join(root, file), "w") as f:
                json.dump(data, f)

            run(['clang-format', '-i', os.path.join(root, file)])


def json_generator(argv):
    if sys.argv[1] == "upgrade":
        json_upgrade()
    else:
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

        run(['clang-format', '-i', f'specs/{fname}'])


if __name__ == '__main__':
    if len(sys.argv) != 1:
        json_generator(sys.argv)
    else:
        c_generator()
