import os, sys

sys.dont_write_bytecode = True

import rsharp as rsx

include_folders = [f"{rsx.tools.get_dir()}/include/", "./"]
if sys.platform == "win32": include_folders.append("C:\\RSharp\\include\\")

file = input("file path > ")

variables, functions, library_functions, files, tokens, ast = rsx.tools.auto_include(
    file = file,
    include_folders = include_folders
)

rsx.builder.build_program(
    path = file,
    include_folders = include_folders,
    console = True,
    variables = variables,
    functions = functions,
    library_functions = library_functions,
    pre_included = files,
    hidden_imports = ["raylib"]
)