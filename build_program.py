import os, sys

sys.dont_write_bytecode = True

import rsxpy as rsx

include_folders = [f"{rsx.tools.get_dir()}/include/", "./"]
if sys.platform == "win32": include_folders.append("C:\\RSX\\include\\")

context = rsx.tools.auto_include(
    file = input("file path > "),
    include_folders = include_folders
)

rsx.builder.build_program(
    console = True,
    context = context,
    hidden_imports = ["raylib", "pysdl2", "pysdl2-dll"]
)