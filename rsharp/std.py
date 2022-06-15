from rsharp.tools import *

import os

create_library("std")

@create_function("VOID", {"command": "STRING"})
def system(environment):
    os.system(environment["args"]["command"])

std = pack_library()