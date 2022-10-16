from rsxpy.tools import *
import rsxpy.builder as builder

create_library("rsxbuild")

@create_function("VOID", {"path": "STRING", "console": "BOOL"})
def build(environment):
    builder.build(
        path = environment["args"]["path"],
        console = environment["args"]["console"]
    )

@create_function("VOID", {"path": "STRING"})
def build_raid(environment):
    builder.build_raid(
        path = environment["args"]["path"]
    )

@create_function("VOID", {"path": "STRING", "include_folders": {"type": "ARRAY", "array_type": "STRING", "size": None}, "console": "BOOL", "icon": "STRING"})
def build_program(environment):
    context = auto_include(
        file = environment["args"]["path"].replace("\\", "/"),
        include_folders = environment["args"]["include_folders"]
    )

    builder.build_program(
        console = environment["args"]["console"],
        context = context,
        icon = environment["args"]["icon"]
    )

rsxbuild = pack_library()