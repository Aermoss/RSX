import os, sys

sys.dont_write_bytecode = True

import rsharp as rsx

rsx.builder.build_program(
    path = "",
    name = input("file path > "),
    include_folders = [
        os.path.split(rsx.__file__)[0] + "\\include\\"
    ],
    console = False,
    imports = [
        "raylib"
    ]
)