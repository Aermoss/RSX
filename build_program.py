import os, sys

sys.dont_write_bytecode = True

import rsharp as rsx

rsx.builder.build_program(
    path = (os.path.split(__file__)[0] + "\\").replace("\\", "/"),
    name = "test.rsx",
    include_folders = [
        (os.path.split(rsx.__file__)[0] + "\\include\\").replace("\\", "/")
    ],
    console = False,
    imports = [
        "raylib"
    ]
)