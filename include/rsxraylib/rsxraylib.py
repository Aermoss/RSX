from tools import *

import raylib, string

import raylib.enums as enums
import raylib.colors as colors

constants = {
    "Colors": {
        0: raylib.LIGHTGRAY,
        1: raylib.GRAY,
        2: raylib.DARKGRAY,
        3: raylib.YELLOW,
        4: raylib.GOLD,
        5: raylib.ORANGE,
        6: raylib.PINK,
        7: raylib.RED,
        8: raylib.MAROON,
        9: raylib.GREEN,
        10: raylib.LIME,
        11: raylib.DARKGREEN,
        12: raylib.SKYBLUE,
        13: raylib.BLUE,
        14: raylib.DARKBLUE,
        15: raylib.PURPLE,
        16: raylib.VIOLET,
        17: raylib.DARKPURPLE,
        18: raylib.BEIGE,
        19: raylib.BROWN,
        20: raylib.DARKBROWN,
        21: raylib.WHITE,
        22: raylib.BLACK,
        23: raylib.BLANK,
        24: raylib.MAGENTA,
        25: raylib.RAYWHITE
    }
}

for i in dir(enums):
    if i[0] != "_":
        constants[i] = {}

        for j in dir(getattr(enums, i)):
            if j[0] != "_":
                constants[i][j] = int(getattr(getattr(enums, i), j))

        constants[i] = {v: k for k, v in constants[i].items()}

create_library("rsxraylib")

@create_function("VOID", {"width": "INT", "height": "INT", "title": "STRING"})
def InitWindow(environment):
    raylib.InitWindow(environment["args"]["width"], environment["args"]["height"], environment["args"]["title"].encode())

@create_function("BOOL", {})
def WindowShouldClose(environment):
    return bool(raylib.WindowShouldClose())

@create_function("VOID", {})
def CloseWindow(environment):
    raylib.CloseWindow()

@create_function("VOID", {"fps": "INT"})
def SetTargetFPS(environment):
    raylib.SetTargetFPS(environment["args"]["fps"])

@create_function("VOID", {})
def BeginDrawing(environment):
    raylib.BeginDrawing()

@create_function("VOID", {})
def EndDrawing(environment):
    raylib.EndDrawing()

@create_function("VOID", {"color": "INT"})
def ClearBackground(environment):
    if environment["args"]["color"] not in constants["Colors"]: error("unknown color")
    else: color = constants["Colors"][environment["args"]["color"]]
    raylib.ClearBackground(color)

@create_function("VOID", {"text": "STRING", "x": "INT", "y": "INT", "fontsize": "INT", "color": "INT"})
def DrawText(environment):
    if environment["args"]["color"] not in constants["Colors"]: error("unknown color")
    else: color = constants["Colors"][environment["args"]["color"]]
    raylib.DrawText(environment["args"]["text"].encode(), environment["args"]["x"], environment["args"]["y"], environment["args"]["fontsize"], color)

@create_function("VOID", {"x": "INT", "y": "INT"})
def DrawFPS(environment):
    raylib.DrawFPS(environment["args"]["x"], environment["args"]["y"])

@create_function("VOID", {"x": "INT", "y": "INT", "width": "INT", "height": "INT", "color": "INT"})
def DrawRectangle(environment):
    if environment["args"]["color"] not in constants["Colors"]: error("unknown color")
    else: color = constants["Colors"][environment["args"]["color"]]
    raylib.DrawRectangle(environment["args"]["x"], environment["args"]["y"], environment["args"]["width"], environment["args"]["height"], color)

@create_function("VOID", {"start_x": "INT", "start_y": "INT", "end_x": "INT", "end_y": "INT", "color": "INT"})
def DrawLine(environment):
    if environment["args"]["color"] not in constants["Colors"]: error("unknown color")
    else: color = constants["Colors"][environment["args"]["color"]]
    raylib.DrawLine(environment["args"]["start_x"], environment["args"]["start_y"], environment["args"]["end_x"], environment["args"]["end_y"], color)

@create_function("BOOL", {"key": "INT"})
def IsKeyDown(environment):
    return bool(raylib.IsKeyDown(environment["args"]["key"]))

@create_function("BOOL", {"key": "INT"})
def IsKeyPressed(environment):
    return bool(raylib.IsKeyPressed(environment["args"]["key"]))

@create_function("BOOL", {"key": "INT"})
def IsKeyReleased(environment):
    return bool(raylib.IsKeyReleased(environment["args"]["key"]))

@create_function("BOOL", {"key": "INT"})
def IsKeyUp(environment):
    return bool(raylib.IsKeyUp(environment["args"]["key"]))

@create_function("INT", {})
def GetKeyPressed(environment):
    return raylib.GetKeyPressed()

@create_function("BOOL", {"button": "INT"})
def IsMouseButtonDown(environment):
    return bool(raylib.IsMouseButtonDown(environment["args"]["button"]))

@create_function("BOOL", {"button": "INT"})
def IsMouseButtonPressed(environment):
    return bool(raylib.IsMouseButtonPressed(environment["args"]["button"]))

@create_function("BOOL", {"button": "INT"})
def IsMouseButtonReleased(environment):
    return bool(raylib.IsMouseButtonReleased(environment["args"]["button"]))

@create_function("BOOL", {"button": "INT"})
def IsMouseButtonUp(environment):
    return bool(raylib.IsMouseButtonUp(environment["args"]["button"]))

@create_function("INT", {})
def GetMouseX(environment):
    return raylib.GetMouseX()

@create_function("INT", {})
def GetMouseY(environment):
    return raylib.GetMouseY()

@create_function("FLOAT", {})
def GetMouseWheelMove(environment):
    return raylib.GetMouseWheelMove()

rsxraylib = pack_library()