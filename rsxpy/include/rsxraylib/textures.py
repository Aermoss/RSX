from rsxpy.tools import *

import raylib, ctypes

from globals import *

create_library("textures")

@create_function("INT", {"fileName": "STRING"})
def LoadImage(environment):
    return add_var(raylib.LoadImage(environment["args"]["fileName"].encode()))

@create_function("VOID", {"image": "INT"})
def UnloadImage(environment):
    raylib.UnloadImage(get_var(environment["args"]["image"]))
    del_var(environment["args"]["image"])

@create_function("INT", {"fileName": "STRING"})
def LoadTexture(environment):
    return add_var(raylib.LoadTexture(environment["args"]["fileName"].encode()))

@create_function("INT", {"image": "INT"})
def LoadTextureFromImage(environment):
    return add_var(raylib.LoadTextureFromImage(get_var(environment["args"]["image"])))

@create_function("VOID", {"texture": "INT"})
def UnloadTexture(environment):
    raylib.UnloadTexture(get_var(environment["args"]["texture"]))
    del_var(environment["args"]["texture"])

@create_function("VOID", {"texture": "INT", "x": "INT", "y": "INT", "color": "INT"})
def DrawTexture(environment):
    raylib.DrawTexture(get_var(environment["args"]["texture"]), environment["args"]["x"], environment["args"]["y"], get_var(environment["args"]["color"]))

textures = pack_library()