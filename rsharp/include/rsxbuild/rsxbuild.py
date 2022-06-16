from rsharp.tools import *
import rsharp.builder as builder

create_library("rsxbuild")

@create_function("VOID", {"path": "STRING", "name": "STRING", "console": "BOOL", "imports": "STRING"})
def build(environment):
    builder.build(
        path = environment["args"]["path"],
        name = environment["args"]["name"],
        console = environment["args"]["console"],
        imports = environment["args"]["imports"].split(";"),
    )

@create_function("VOID", {"path": "STRING", "name": "STRING", "include_folders": "STRING", "console": "BOOL", "imports": "STRING"})
def build_program(environment):
    builder.build_program(
        path = environment["args"]["path"],
        name = environment["args"]["name"],
        include_folders = environment["args"]["include_folders"].split(";"),
        console = environment["args"]["console"],
        imports = environment["args"]["imports"].split(";"),
    )

rsxbuild = pack_library()