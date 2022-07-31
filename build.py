import os, sys

sys.dont_write_bytecode = True

import rsharp as rsx

rsx.builder.build(
    path = "rsharp.exe",
    console = True,
    hidden_imports = ["raylib", "pysdl2", "pysdl2-dll"]
)