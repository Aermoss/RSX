import os, sys

sys.dont_write_bytecode = True

import rsharp as rsx

include_folders = [
    os.path.split(rsx.__file__)[0] + "\\include\\",
    "C:\\RSharp\\include\\",
    ".\\include\\",
    ".\\"
]

file = input("file path > ")

variables, functions, library_functions, files = rsx.tools.auto_include(
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
)