import sys, os

sys.dont_write_bytecode = True

from rsharp.tools import *

create_library("std")

@create_function("VOID", {"command": "STRING"})
def system(environment):
    os.system(environment["args"]["command"])

std = pack_library()