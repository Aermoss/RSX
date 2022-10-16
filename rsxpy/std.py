import sys, os

import rsxpy.tools as tools

tools.create_library("std")

@tools.create_function("VOID", {"command": "STRING"})
def system(environment):
    os.system(environment["args"]["command"])

std = tools.pack_library()