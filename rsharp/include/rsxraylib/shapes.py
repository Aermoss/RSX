from rsharp.tools import *

import raylib

from globals import *

create_library("shapes")

# @create_function("VOID", {..., ...})
# def SetShapesTexture(environment):
#     raylib.SetShapesTexture(..., ...)

@create_function("VOID", {"posX": "INT", "posY": "INT", "color": "INT"})
def DrawPixel(environment):
    raylib.DrawPixel(environment["args"]["posX"], environment["args"]["posY"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "color": "INT"})
# def DrawPixelV(environment):
#     raylib.DrawPixelV(..., get_var(environment["args"]["color"]))

@create_function("VOID", {"startPosX": "INT", "startPosY": "INT", "endPosX": "INT", "endPosY": "INT", "color": "INT"})
def DrawLine(environment):
    raylib.DrawLine(environment["args"]["startPosX"], environment["args"]["startPosY"], environment["args"]["endPosX"], environment["args"]["endPosY"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., ..., "color": "INT"})
# def DrawLineV(environment):
#     raylib.DrawLineV(..., ..., get_var(environment["args"]["color"]))

# @create_function("VOID", {..., ..., "thick": "FLOAT", "color": "INT"})
# def DrawLineEx(environment):
#     raylib.DrawLineEx(..., ..., environment["args"]["thick"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., ..., "thick": "FLOAT", "color": "INT"})
# def DrawLineBezier(environment):
#     raylib.DrawLineBezier(..., ..., environment["args"]["thick"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., ..., ..., "thick": "FLOAT", "color": "INT"})
# def DrawLineBezierQuad(environment):
#     raylib.DrawLineBezierQuad(..., ..., ..., environment["args"]["thick"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., ..., ..., ..., "thick": "FLOAT", "color": "INT"})
# def DrawLineBezierCubic(environment):
#     raylib.DrawLineBezierCubic(..., ..., ..., ..., environment["args"]["thick"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "pointsCount": "INT", "color": "INT"})
# def DrawLineStrip(environment):
#     raylib.DrawLineStrip(..., environment["args"]["pointsCount"], get_var(environment["args"]["color"]))

@create_function("VOID", {"centerX": "INT", "centerY": "INT", "radius": "FLOAT", "color": "INT"})
def DrawCircle(environment):
    raylib.DrawCircle(environment["args"]["centerX"], environment["args"]["centerY"], environment["args"]["radius"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "radius": "FLOAT", "startAngle": "FLOAT", "endAngle": "FLOAT", "segments": "INT", "color": "INT"})
# def DrawCircleSector(environment):
#     raylib.DrawCircleSector(..., environment["args"]["radius"], environment["args"]["startAngle"], environment["args"]["endAngle"], environment["args"]["segments"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "radius": "FLOAT", "startAngle": "FLOAT", "endAngle": "FLOAT", "segments": "INT", "color": "INT"})
# def DrawCircleSectorLines(environment):
#     raylib.DrawCircleSectorLines(..., environment["args"]["radius"], environment["args"]["startAngle"], environment["args"]["endAngle"], environment["args"]["segments"], get_var(environment["args"]["color"]))

@create_function("VOID", {"centerX": "INT", "centerY": "INT", "radius": "FLOAT", "color1": "INT", "color2": "INT"})
def DrawCircleGradient(environment):
    raylib.DrawCircleGradient(environment["args"]["centerX"], environment["args"]["centerY"], environment["args"]["radius"], get_var(environment["args"]["color1"]), get_var(environment["args"]["color2"]))

# @create_function("VOID", {..., "radius": "FLOAT", "color": "INT"})
# def DrawCircleV(environment):
#     raylib.DrawCircleV(..., environment["args"]["radius"], get_var(environment["args"]["color"]))

@create_function("VOID", {"centerX": "INT", "centerY": "INT", "radius": "FLOAT", "color": "INT"})
def DrawCircleLines(environment):
    raylib.DrawCircleLines(environment["args"]["centerX"], environment["args"]["centerY"], environment["args"]["radius"], get_var(environment["args"]["color"]))

@create_function("VOID", {"centerX": "FLOAT", "centerY": "FLOAT", "radiusH": "FLOAT", "radiusV": "FLOAT", "color": "INT"})
def DrawEllipse(environment):
    raylib.DrawEllipse(environment["args"]["centerX"], environment["args"]["centerY"], environment["args"]["radiusH"], environment["args"]["radiusV"], get_var(environment["args"]["color"]))

@create_function("VOID", {"centerX": "FLOAT", "centerY": "FLOAT", "radiusH": "FLOAT", "radiusV": "FLOAT", "color": "INT"})
def DrawEllipseLines(environment):
    raylib.DrawEllipseLines(environment["args"]["centerX"], environment["args"]["centerY"], environment["args"]["radiusH"], environment["args"]["radiusV"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "innerRadius": "FLOAT", "outerRadius": "FLOAT", "startAngle": "FLOAT", "endAngle": "FLOAT", "segments": "INT", "color": "INT"})
# def DrawRing(environment):
#     raylib.DrawRing(..., environment["args"]["innerRadius"], environment["args"]["outerRadius"], environment["args"]["startAngle"], environment["args"]["endAngle"], environment["args"]["segments"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "innerRadius": "FLOAT", "outerRadius": "FLOAT", "startAngle": "FLOAT", "endAngle": "FLOAT", "segments": "INT", "color": "INT"})
# def DrawRingLines(environment):
#     raylib.DrawRingLines(..., environment["args"]["innerRadius"], environment["args"]["outerRadius"], environment["args"]["startAngle"], environment["args"]["endAngle"], environment["args"]["segments"], get_var(environment["args"]["color"]))

@create_function("VOID", {"posX": "INT", "posY": "INT", "width": "INT", "height": "INT", "color": "INT"})
def DrawRectangle(environment):
    raylib.DrawRectangle(environment["args"]["posX"], environment["args"]["posY"], environment["args"]["width"], environment["args"]["height"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., ..., "color": "INT"})
# def DrawRectangleV(environment):
#     raylib.DrawRectangleV(..., ..., get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "color": "INT"})
# def DrawRectangleRec(environment):
#     raylib.DrawRectangleRec(..., get_var(environment["args"]["color"]))

# @create_function("VOID", {..., ..., "rotation": "FLOAT", "color": "INT"})
# def DrawRectanglePro(environment):
#     raylib.DrawRectanglePro(..., ..., environment["args"]["rotation"], get_var(environment["args"]["color"]))

@create_function("VOID", {"posX": "INT", "posY": "INT", "width": "INT", "height": "INT", "color1": "INT", "color2": "INT"})
def DrawRectangleGradientV(environment):
    raylib.DrawRectangleGradientV(environment["args"]["posX"], environment["args"]["posY"], environment["args"]["width"], environment["args"]["height"], get_var(environment["args"]["color1"]), get_var(environment["args"]["color2"]))

@create_function("VOID", {"posX": "INT", "posY": "INT", "width": "INT", "height": "INT", "color1": "INT", "color2": "INT"})
def DrawRectangleGradientH(environment):
    raylib.DrawRectangleGradientH(environment["args"]["posX"], environment["args"]["posY"], environment["args"]["width"], environment["args"]["height"], get_var(environment["args"]["color1"]), get_var(environment["args"]["color2"]))

# @create_function("VOID", {..., "col1": "INT", "col2": "INT", "col3": "INT", "col4": "INT"})
# def DrawRectangleGradientEx(environment):
#     raylib.DrawRectangleGradientEx(..., get_var(environment["args"]["col1"]), get_var(environment["args"]["col2"]), get_var(environment["args"]["col3"]), get_var(environment["args"]["col4"]))

@create_function("VOID", {"posX": "INT", "posY": "INT", "width": "INT", "height": "INT", "color": "INT"})
def DrawRectangleLines(environment):
    raylib.DrawRectangleLines(environment["args"]["posX"], environment["args"]["posY"], environment["args"]["width"], environment["args"]["height"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "lineThick": "INT", "color": "INT"})
# def DrawRectangleLinesEx(environment):
#     raylib.DrawRectangleLinesEx(..., environment["args"]["lineThick"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "roundness": "FLOAT", "segments": "INT", "color": "INT"})
# def DrawRectangleRounded(environment):
#     raylib.DrawRectangleRounded(..., environment["args"]["roundness"], environment["args"]["segments"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "roundness": "FLOAT", "segments": "INT", "lineThick": "INT", "color": "INT"})
# def DrawRectangleRoundedLines(environment):
#     raylib.DrawRectangleRoundedLines(..., environment["args"]["roundness"], environment["args"]["segments"], environment["args"]["lineThick"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., ..., ..., "color": "INT"})
# def DrawTriangle(environment):
#     raylib.DrawTriangle(..., ..., ..., get_var(environment["args"]["color"]))

# @create_function("VOID", {..., ..., ..., "color": "INT"})
# def DrawTriangleLines(environment):
#     raylib.DrawTriangleLines(..., ..., ..., get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "pointsCount": "INT", "color": "INT"})
# def DrawTriangleFan(environment):
#     raylib.DrawTriangleFan(..., environment["args"]["pointsCount"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "pointsCount": "INT", "color": "INT"})
# def DrawTriangleStrip(environment):
#     raylib.DrawTriangleStrip(..., environment["args"]["pointsCount"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "sides": "INT", "radius": "FLOAT", "rotation": "FLOAT", "color": "INT"})
# def DrawPoly(environment):
#     raylib.DrawPoly(..., environment["args"]["sides"], environment["args"]["radius"], environment["args"]["rotation"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "sides": "INT", "radius": "FLOAT", "rotation": "FLOAT", "color": "INT"})
# def DrawPolyLines(environment):
#     raylib.DrawPolyLines(..., environment["args"]["sides"], environment["args"]["radius"], environment["args"]["rotation"], get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "sides": "INT", "radius": "FLOAT", "rotation": "FLOAT", "lineThick": "FLOAT", "color": "INT"})
# def DrawPolyLinesEx(environment):
#     raylib.DrawPolyLinesEx(..., environment["args"]["sides"], environment["args"]["radius"], environment["args"]["rotation"], environment["args"]["lineThick"], get_var(environment["args"]["color"]))

# @create_function("BOOL", {..., ...})
# def CheckCollisionRecs(environment):
#     return bool(raylib.CheckCollisionRecs(..., ...))

# @create_function("BOOL", {..., "radius1": "FLOAT", ..., "radius2": "FLOAT"})
# def CheckCollisionCircles(environment):
#     return bool(raylib.CheckCollisionCircles(..., environment["args"]["radius1"], ..., environment["args"]["radius2"])

# @create_function("BOOL", {..., "radius": "FLOAT", ...})
# def CheckCollisionCircleRec(environment):
#     return bool(raylib.CheckCollisionCircleRec(..., environment["args"]["radius"], ...))

# @create_function("BOOL", {..., ...})
# def CheckCollisionPointRec(environment):
#     return bool(raylib.CheckCollisionPointRec(..., ...))

# @create_function("BOOL", {..., ..., "radius": "FLOAT"})
# def CheckCollisionPointCircle(environment):
#     return bool(raylib.CheckCollisionPointCircle(..., ..., environment["args"]["radius"]))

# @create_function("BOOL", {..., ..., ..., ...})
# def CheckCollisionPointTriangle(environment):
#     return bool(raylib.CheckCollisionPointTriangle(..., ..., ..., ...))

# @create_function("BOOL", {..., ..., ..., ..., ...})
# def CheckCollisionLines(environment):
#     return bool(raylib.CheckCollisionLines(..., ..., ..., ..., ...))

# @create_function("BOOL", {..., ..., ..., "threshold": "INT"})
# def CheckCollisionPointLine(environment):
#     return bool(raylib.CheckCollisionPointLine(..., ..., ..., environment["args"]["threshold"]))

# @create_function("BOOL", {..., {..., ...})
# def GetCollisionRec(environment):
#     return bool(raylib.GetCollisionRec(..., ...))

shapes = pack_library()