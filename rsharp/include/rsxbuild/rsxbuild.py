from rsharp.tools import *
import rsharp.builder as builder

create_library("rsxbuild")

@create_function("VOID", {"path": "STRING", "name": "STRING", "console": "BOOL"})
def build(environment):
    builder.build(
        path = environment["args"]["path"],
        name = environment["args"]["name"],
        console = environment["args"]["console"]
    )

@create_function("VOID", {"path": "STRING", "name": "STRING", "include_folders": "STRING", "console": "BOOL"})
def build_program(environment):
    variables, functions, library_functions, files = auto_include(
        file = environment["args"]["name"],
        include_folders = environment["args"]["include_folders"].split(";")
    )

    builder.build_program(
        path = environment["args"]["path"],
        name = environment["args"]["name"],
        include_folders = environment["args"]["include_folders"].split(";"),
        console = environment["args"]["console"],
        variables = variables,
        functions = functions,
        library_functions = library_functions,
        pre_included = files,
    )

rsxbuild = pack_library()