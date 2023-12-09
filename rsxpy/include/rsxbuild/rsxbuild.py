from rsxpy.tools import *
import rsxpy.builder as builder

create_library("rsxbuild")

@create_function("VOID", {"path": StringType(), "console": BoolType()})
def build(environment):
    builder.build(
        path = environment["args"]["path"],
        console = environment["args"]["console"]
    )

@create_function("VOID", {"path": StringType()})
def build_raid(environment):
    builder.build_raid(
        path = environment["args"]["path"]
    )

@create_function("VOID", {"path": StringType(), "include_folders": ArrayType(StringType()), "console": BoolType(), "icon": StringType()})
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