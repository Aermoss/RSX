from rsharp.tools import *

import raylib

from globals import *

create_library("structs")

@create_function("INT", {"x": "FLOAT", "y": "FLOAT"})
def Vector2(environment):
    return add_var((environment["args"]["x"], environment["args"]["y"]))

@create_function("INT", {"x": "FLOAT", "y": "FLOAT", "z": "FLOAT"})
def Vector3(environment):
    return add_var((environment["args"]["x"], environment["args"]["y"], environment["args"]["z"]))

@create_function("INT", {"x": "FLOAT", "y": "FLOAT", "z": "FLOAT", "w": "FLOAT"})
def Vector4(environment):
    return add_var((environment["args"]["x"], environment["args"]["y"], environment["args"]["z"], environment["args"]["w"]))

@create_function("INT", {"x": "FLOAT", "y": "FLOAT", "z": "FLOAT", "w": "FLOAT"})
def Quaternion(environment):
    return add_var((environment["args"]["x"], environment["args"]["y"], environment["args"]["z"], environment["args"]["w"]))

@create_function("INT", {"m0": "FLOAT", "m4": "FLOAT", "m8": "FLOAT", "m12": "FLOAT",
                         "m1": "FLOAT", "m5": "FLOAT", "m9": "FLOAT", "m13": "FLOAT",
                         "m2": "FLOAT", "m6": "FLOAT", "m10": "FLOAT", "m14": "FLOAT",
                         "m3": "FLOAT", "m7": "FLOAT", "m11": "FLOAT", "m15": "FLOAT"})
def Matrix(environment):
    return add_var((environment["args"]["m0"], environment["args"]["m4"], environment["args"]["m8"], environment["args"]["m12"],
                    environment["args"]["m1"], environment["args"]["m5"], environment["args"]["m9"], environment["args"]["m13"],
                    environment["args"]["m2"], environment["args"]["m6"], environment["args"]["m10"], environment["args"]["m14"],
                    environment["args"]["m3"], environment["args"]["m7"], environment["args"]["m11"], environment["args"]["m15"]))

@create_function("INT", {"r": "INT", "g": "INT", "b": "INT", "a": "INT"})
def Color(environment):
    return add_var((environment["args"]["r"], environment["args"]["g"], environment["args"]["b"], environment["args"]["a"]))

@create_function("INT", {"x": "FLOAT", "y": "FLOAT", "width": "FLOAT", "height": "FLOAT"})
def Rectangle(environment):
    return add_var((environment["args"]["x"], environment["args"]["y"], environment["args"]["width"], environment["args"]["height"]))

# @create_function("INT", {..., "width": "INT", "height": "INT", "mipmaps": "INT", "format": "INT"})
# def Image(environment):
#     return add_var((..., environment["args"]["width"], environment["args"]["height"], environment["args"]["mipmaps"], environment["args"]["format"]))

@create_function("INT", {"id": "INT", "width": "INT", "height": "INT", "mipmaps": "INT", "format": "INT"})
def Texture(environment):
    return add_var((environment["args"]["id"], environment["args"]["width"], environment["args"]["height"], environment["args"]["mipmaps"], environment["args"]["format"]))

@create_function("INT", {"id": "INT", "width": "INT", "height": "INT", "mipmaps": "INT", "format": "INT"})
def Texture2D(environment):
    return add_var((environment["args"]["id"], environment["args"]["width"], environment["args"]["height"], environment["args"]["mipmaps"], environment["args"]["format"]))

@create_function("INT", {"id": "INT", "width": "INT", "height": "INT", "mipmaps": "INT", "format": "INT"})
def TextureCubemap(environment):
    return add_var((environment["args"]["id"], environment["args"]["width"], environment["args"]["height"], environment["args"]["mipmaps"], environment["args"]["format"]))

@create_function("INT", {"id": "INT", "texture": "INT", "depth": "INT"})
def RenderTexture(environment):
    return add_var((environment["args"]["id"], get_var(environment["args"]["texture"]), get_var(environment["args"]["depth"])))

@create_function("INT", {"id": "INT", "texture": "INT", "depth": "INT"})
def RenderTexture2D(environment):
    return add_var((environment["args"]["id"], get_var(environment["args"]["texture"]), get_var(environment["args"]["depth"])))

@create_function("INT", {"source": "INT", "left": "INT", "top": "INT", "right": "INT", "bottom": "INT", "layout": "INT"})
def NPatchInfo(environment):
    return add_var((get_var(environment["args"]["source"]), environment["args"]["left"], environment["args"]["top"], environment["args"]["right"], environment["args"]["bottom"], environment["args"]["layout"]))

@create_function("INT", {"value": "INT", "offsetX": "INT", "offsetY": "INT", "advanceX": "INT", "image": "INT"})
def GlyphInfo(environment):
    return add_var((environment["args"]["value"], environment["args"]["offsetX"], environment["args"]["offsetY"], environment["args"]["advanceX"], get_var(environment["args"]["image"])))

# @create_function("INT", {"baseSize": "INT", "glyphCount": "INT", "glyphPadding": "INT", "texture": "INT", ..., ...})
# def Font(environment):
#     return add_var((environment["args"]["baseSize"], environment["args"]["glyphCount"], environment["args"]["glyphPadding"], get_var(environment["args"]["texture"]), ..., ...))

@create_function("INT", {"position": "INT", "target": "INT", "up": "INT", "fovy": "FLOAT", "projection": "INT"})
def Camera3D(environment):
    return add_var((get_var(environment["args"]["position"]), get_var(environment["args"]["target"]), get_var(environment["args"]["up"]), environment["args"]["fovy"], environment["args"]["projection"]))

@create_function("INT", {"position": "INT", "target": "INT", "up": "INT", "fovy": "FLOAT", "projection": "INT"})
def Camera(environment):
    return add_var((get_var(environment["args"]["position"]), get_var(environment["args"]["target"]), get_var(environment["args"]["up"]), environment["args"]["fovy"], environment["args"]["projection"]))

@create_function("INT", {"offset": "INT", "target": "INT", "rotation": "FLOAT", "zoom": "FLOAT"})
def Camera2D(environment):
    return add_var((get_var(environment["args"]["offset"]), get_var(environment["args"]["target"]), environment["args"]["rotation"], environment["args"]["zoom"]))

structs = pack_library()