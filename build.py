import os, sys

sys.dont_write_bytecode = True

import rsxpy as rsx

rsx.builder.build(
    path = "rsx.exe",
    console = True,
    hidden_imports = ["raylib", "pysdl2", "pysdl2-dll", "pyinstaller"]
)

rsx.builder.build_raid(
    path = "raid.exe"
)