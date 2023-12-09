import os, glm

from rsxobj_globals import *
from rsxpy import *

from typing import List

def loadMTL(filePath):
    materials, current = {}, ""
    names = {
        "illumination": (["illum"], int),
        "roughness": (["Ns"], float),
        "albedo": (["Kd"], glm.vec3),
        "ambient": (["Ka"], glm.vec3),
        "specular": (["Ks"], glm.vec3),
        "emission": (["Ke"], glm.vec3),
        "dissolve": (["d"], float),
        "roughnessMap": (["map_Ns"], str),
        "albedoMap": (["map_Kd"], str),
        "specularMap": (["map_Ks"], str),
        "ambientMap": (["map_Ka"], str),
        "dissolveMap": (["map_d"], str),
        "normalMap": (["map_Bump", "map_bump", "bump"], str),
        "emissionMap": (["map_Ke"], str),
        "metallicMap": (["map_refl", "refl"], str)
    }

    attributes = {}

    for i in names:
        for j in names[i][0]:
            attributes[j] = (i, names[i][1])

    for line in open(filePath, "r").read().split("\n"):
        values = line.split(" ")

        if values[0] == "newmtl":
            current = values[1]
            materials[current] = {}

        elif values[0] in attributes:
            if attributes[values[0]][1] == str:
                materials[current][attributes[values[0]][0]] = os.path.join(os.path.split(filePath)[0], " ".join(values[1:]))

            if attributes[values[0]][1] == float:
                materials[current][attributes[values[0]][0]] = float(values[1])

            if attributes[values[0]][1] == glm.vec3:
                materials[current][attributes[values[0]][0]] = glm.vec3(*[float(i) for i in values[1:]])

    return materials

rsxlib.begin()
    
def loadOBJ(filePath: str) -> int:
    materials, meshes, data = {}, {}, {"v": [], "vt": [], "vn": []}
    current_mesh, current_material = "", ""

    for line in open(filePath, "r").read().split("\n"):
        values = line.split(" ")

        if values[0] in list(data.keys()):
            data[values[0]].append([float(i) for i in values[1:] if i != ""])

        elif values[0] == "f":
            if current_mesh == "":
                current_mesh = "main"
                meshes[current_mesh] = {}

            if current_material == "":
                current_material = "None"
                materials["None"] = {"Kd": [1.0, 1.0, 1.0]}
                meshes[current_mesh][current_material] = []

            for i in values[1:]:
                if i == "": continue
                
                meshes[current_mesh][current_material] += data["v"][int(i.split("/")[0]) - 1] \
                    + (data["vt"][int(i.split("/")[1]) - 1][:2] if i.split("/")[1] != "" else [0.0, 0.0]) \
                        + (data["vn"][int(i.split("/")[2]) - 1] if i.split("/")[2] != "" else [0.0, 0.0, 0.0]) if len(i.split("/")) == 3 else []

        elif values[0] == "mtllib":
            materials = loadMTL(os.path.join(os.path.split(filePath)[0], " ".join(values[1:])))

        elif values[0] == "usemtl":
            if current_mesh == "":
                current_mesh = "main"
                meshes[current_mesh] = {}

            current_material = " ".join(values[1:])
            meshes[current_mesh][current_material] = []

        elif values[0] == "o":
            current_mesh = " ".join(values[1:])
            meshes[current_mesh] = {}

    return add_var({"meshes": meshes, "materials": materials}, True)

def getMaterials(obj: int) -> List[str]:
    return list(get_var(obj)["materials"].keys())

def getMaterialContents(obj: int, material: str) -> List[str]:
    return list(get_var(obj)["materials"][material].keys())

def getMaterialContent(obj: int, material: str, content: str) -> float:
    return get_var(obj)["materials"][material][content]

def getMeshes(obj: int) -> List[str]:
    return list(get_var(obj)["meshes"].keys())

def getMeshMaterials(obj: int, mesh: str) -> List[str]:
    return list(get_var(obj)["meshes"][mesh].keys())

def getMeshDataByMaterial(obj: int, mesh: str, material: str) -> List[float]:
    return get_var(obj)["meshes"][mesh][material]

rsxlib.end()