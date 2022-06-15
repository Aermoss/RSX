from rsharp.tools import *

import raylib

from globals import *

create_library("textures")

@create_function("INT", {"fileName": "STRING"})
def LoadImage(environment):
    return add_var(raylib.LoadImage(environment["args"]["fileName"].encode()))

@create_function("VOID", {"image": "INT"})
def UnloadImage(environment):
    raylib.UnloadImage(get_var(environment["args"]["image"]))
    del_var(environment["args"]["image"])

textures = pack_library()