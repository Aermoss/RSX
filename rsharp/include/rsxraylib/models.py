from rsharp.tools import *

import raylib

from globals import *

create_library("models")

@create_function("VOID", {"startPos": "INT", "endPos": "INT", "color": "INT"})
def DrawLine3D(environment):
    raylib.DrawLine3D(get_var(environment["args"]["startPos"]), get_var(environment["args"]["endPos"]), get_var(environment["args"]["color"]))

@create_function("VOID", {"position": "INT", "color": "INT"})
def DrawPoint3D(environment):
    raylib.DrawPoint3D(get_var(environment["args"]["position"]), get_var(environment["args"]["color"]))

@create_function("VOID", {"center": "INT", "radius": "FLOAT", "rotationAxis": "INT", "rotationAngle": "FLOAT", "color": "INT"})
def DrawCircle3D(environment):
    raylib.DrawCircle3D(get_var(environment["args"]["center"]), environment["args"]["radius"], get_var(environment["args"]["rotationAxis"]), environment["args"]["rotationAngle"], get_var(environment["args"]["color"]))

@create_function("VOID", {"v1": "INT", "v2": "INT", "v3": "INT", "color": "INT"})
def DrawTriangle3D(environment):
    raylib.DrawTriangle3D(get_var(environment["args"]["v1"]), get_var(environment["args"]["v2"]), get_var(environment["args"]["v3"]), get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "pointsCount": "INT", "color": "INT"})
# def DrawTriangleStrip3D(environment):
#     raylib.DrawTriangleStrip3D(..., environment["args"]["pointsCount"], get_var(environment["args"]["color"]))

@create_function("VOID", {"position": "INT", "width": "FLOAT", "height": "FLOAT", "length": "FLOAT", "color": "INT"})
def DrawCube(environment):
    raylib.DrawCube(get_var(environment["args"]["position"]), environment["args"]["width"], environment["args"]["height"], environment["args"]["length"], get_var(environment["args"]["color"]))

@create_function("VOID", {"position": "INT", "size": "INT", "color": "INT"})
def DrawCubeV(environment):
    raylib.DrawCubeV(get_var(environment["args"]["EMPTY"]), get_var(environment["args"]["EMPTY"]), get_var(environment["args"]["EMPTY"]))

@create_function("VOID", {"position": "INT", "width": "FLOAT", "height": "FLOAT", "length": "FLOAT", "color": "INT"})
def DrawCubeWires(environment):
    raylib.DrawCubeWires(get_var(environment["args"]["position"]), environment["args"]["width"], environment["args"]["height"], environment["args"]["length"], get_var(environment["args"]["color"]))

@create_function("VOID", {"position": "INT", "size": "INT", "color": "INT"})
def DrawCubeWiresV(environment):
    raylib.DrawCubeWiresV(get_var(environment["args"]["position"]), get_var(environment["args"]["size"]), get_var(environment["args"]["color"]))

@create_function("VOID", {"texture": "INT", "position": "INT", "width": "FLOAT", "height": "FLOAT", "length": "FLOAT", "color": "INT"})
def DrawCubeTexture(environment):
    raylib.DrawCubeTexture(get_var(environment["args"]["texture"]), get_var(environment["args"]["position"]), environment["args"]["width"], environment["args"]["height"], environment["args"]["length"], environment["args"]["color"])

@create_function("VOID", {"texture": "INT", "source": "INT", "position": "INT", "width": "FLOAT", "height": "FLOAT", "length": "FLOAT", "color": "INT"})
def DrawCubeTextureRec(environment):
    raylib.DrawCubeTextureRec(get_var(environment["args"]["texture"]), get_var(environment["args"]["source"]), get_var(environment["args"]["position"]), environment["args"]["width"], environment["args"]["height"], environment["args"]["length"], get_var(environment["args"]["color"]))

@create_function("VOID", {"centerPos": "INT", "radius": "FLOAT", "color": "INT"})
def DrawSphere(environment):
    raylib.DrawSphere(get_var(environment["args"]["centerPos"]), environment["args"]["radius"], get_var(environment["args"]["color"]))

@create_function("VOID", {"centerPos": "INT", "radius": "FLOAT", "rings": "INT", "slices": "INT", "color": "INT"})
def DrawSphereEx(environment):
    raylib.DrawSphereEx(get_var(environment["args"]["centerPos"]), environment["args"]["radius"], environment["args"]["rings"], environment["args"]["slices"], get_var(environment["args"]["color"]))

@create_function("VOID", {"centerPos": "INT", "radius": "FLOAT", "rings": "INT", "slices": "INT", "color": "INT"})
def DrawSphereWires(environment):
    raylib.DrawSphereWires(get_var(environment["args"]["centerPos"]), environment["args"]["radius"], environment["args"]["rings"], environment["args"]["slices"], get_var(environment["args"]["color"]))

@create_function("VOID", {"position": "INT", "radiusTop": "FLOAT", "radiusBottom": "FLOAT", "height": "FLOAT", "slices": "INT", "color": "INT"})
def DrawCylinder(environment):
    raylib.DrawCylinder(get_var(environment["args"]["position"]), environment["args"]["radiusTop"], environment["args"]["radiusBottom"], environment["args"]["height"], environment["args"]["slices"], get_var(environment["args"]["color"]))

@create_function("VOID", {"startPos": "INT", "endPos": "INT", "startRadius": "FLOAT", "endRadius": "FLOAT", "sides": "INT", "color": "INT"})
def DrawCylinderEx(environment):
    raylib.DrawCylinderEx(get_var(environment["args"]["startPos"]), get_var(environment["args"]["endPos"]), environment["args"]["startRadius"], environment["args"]["endRadius"], environment["args"]["sides"], get_var(environment["args"]["color"]))

@create_function("VOID", {"position": "INT", "radiusTop": "FLOAT", "radiusBottom": "FLOAT", "height": "FLOAT", "slices": "INT", "color": "INT"})
def DrawCylinderWires(environment):
    raylib.DrawCylinderWires(get_var(environment["args"]["position"]), environment["args"]["radiusTop"], environment["args"]["radiusBottom"], environment["args"]["height"], environment["args"]["slices"], get_var(environment["args"]["color"]))

@create_function("VOID", {"startPos": "INT", "endPos": "INT", "startRadius": "FLOAT", "endRadius": "FLOAT", "sides": "INT", "color": "INT"})
def DrawCylinderWiresEx(environment):
    raylib.DrawCylinderWiresEx(get_var(environment["args"]["startPos"]), get_var(environment["args"]["endPos"]), environment["args"]["startRadius"], environment["args"]["endRadius"], environment["args"]["sides"], get_var(environment["args"]["color"]))

@create_function("VOID", {"centerPos": "INT", "size": "INT", "color": "INT"})
def DrawPlane(environment):
    raylib.DrawPlane(get_var(environment["args"]["centerPos"]), get_var(environment["args"]["size"]), get_var(environment["args"]["color"]))

# @create_function("VOID", {..., "color": "INT"})
# def DrawRay(environment):
#     raylib.DrawRay(..., environment["args"]["color"])

@create_function("VOID", {"slices": "INT", "spacing": "FLOAT"})
def DrawGrid(environment):
    raylib.DrawGrid(environment["args"]["slices"], environment["args"]["spacing"])

models = pack_library()