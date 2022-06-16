import os, sys

sys.dont_write_bytecode = True

import rsharp as rsx

rsx.builder.build(
    path = (os.path.split(__file__)[0] + "\\").replace("\\", "/"),
    name = "rsharp.exe",
    console = True,
    imports = [
        "raylib"
    ]
)
