from rsharp.tools import *

import raylib

from globals import *

create_library("extras")

@create_function("VOID", {"var": "INT"})
def Delete(environment):
    del_var(environment["args"]["var"])

@create_function("INT", {})
def GetVarCount(environment):
    return len(var_dict)

extras = pack_library()