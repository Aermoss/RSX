from rsharp.tools import *
import rsharp.builder as builder

create_library("rsxbuild")

@create_function("VOID", {"path": "STRING", "console": "BOOL"})
def build(environment):
    builder.build(
        path = environment["args"]["path"],
        console = environment["args"]["console"]
    )

@create_function("VOID", {"path": "STRING", "include_folders": "STRING", "console": "BOOL", "icon": "STRING"})
def build_program(environment):
    variables, functions, library_functions, files = auto_include(
        file = environment["args"]["path"].replace("\\", "/"),
        include_folders = environment["args"]["include_folders"].split(";")
    )

    builder.build_program(
        path = environment["args"]["path"],
        include_folders = environment["args"]["include_folders"].split(";"),
        console = environment["args"]["console"],
        variables = variables,
        functions = functions,
        library_functions = library_functions,
        pre_included = files,
        icon = environment["args"]["icon"]
    )

rsxbuild = pack_library()