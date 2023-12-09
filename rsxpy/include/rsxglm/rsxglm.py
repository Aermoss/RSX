import rsxpy.rsxlib as rsxlib
import rsxpy.tools as tools
from rsxglm_globals import *

import glm, ctypes
import rsxglm_globals

tools.environ["RSXGLM_GLOBALS"] = rsxglm_globals

rsxlib.begin()

def radians(val: float) -> float:
    return glm.radians(val)

def degrees(val: float) -> float:
    return glm.degrees(val)

def vec2(x: float, y: float) -> int:
    return add_var(glm.vec2(x, y))

def vec3(x: float, y: float, z: float) -> int:
    return add_var(glm.vec3(x, y, z))

def vec4(x: float, y: float, z: float, w: float) -> int:
    return add_var(glm.vec4(x, y, z, w))

def mat4(val: float) -> int:
    return add_var(glm.mat4(val))

def _translate(addr1: int, addr2: int) -> int:
    return add_var(glm.translate(get_var(addr1), get_var(addr2)))

def _scale(addr1: int, addr2: int) -> int:
    return add_var(glm.scale(get_var(addr1), get_var(addr2)))

def _rotate(addr1: int, val: float, addr2: int) -> int:
    return add_var(glm.rotate(get_var(addr1), val, get_var(addr2)))

def translate(addr1: int, addr2: int) -> int:
    tmp = add_var(glm.translate(get_var(addr1), get_var(addr2)), True)
    del_var(addr1)
    return tmp

def scale(addr1: int, addr2: int) -> int:
    tmp = add_var(glm.scale(get_var(addr1), get_var(addr2)), True)
    del_var(addr1)
    return tmp

def rotate(addr1: int, val: float, addr2: int) -> int:
    tmp = add_var(glm.rotate(get_var(addr1), val, get_var(addr2)), True)
    del_var(addr1)
    return tmp

def add(addr1: int, addr2: int) -> int:
    return add_var(get_var(addr1) + get_var(addr2))

def mul(addr1: int, addr2: int) -> int:
    return add_var(get_var(addr1) * get_var(addr2))

def neg(addr: int) -> int:
    return add_var(-get_var(addr))

def cross(addr1: int, addr2: int) -> int:
    return add_var(glm.cross(get_var(addr1), get_var(addr2)))

def normalize(addr: float) -> int:
    return add_var(glm.normalize(get_var(addr)))

def perspective(fov: float, aspect: float, near: float, far: float) -> int:
    return add_var(glm.perspective(fov, aspect, near, far))

def lookAt(eye: int, center: int, up: int) -> int:
    return add_var(glm.lookAt(get_var(eye), get_var(center), get_var(up)))

def delete(addr: int) -> None:
    del_var(addr)

def value_ptr(addr: int) -> int:
    var = get_var(addr)
    if type(var) in [glm.vec2, glm.vec3, glm.vec4]: arr = [i for i in var.to_list()]
    elif isinstance(var, glm.mat4): return add_var(glm.value_ptr(var)) # arr = [i[j] for j in range(4) for i in var.to_list()]
    else: error("invalid type for value ptr", "<rsxglm>")
    return add_var(arr)

rsxlib.end()

# tools.create_library("_rsxglm")
# 
# @tools.create_function(tools.IntType(), {"addr1": tools.IntType(), "addr2": tools.IntType()})
# def translate(environ):
#     addr1, addr2 = environ["args"].values()
#     tmp = tools.py_to_rsx_value(add_var(glm.translate(get_var(addr1), get_var(addr2))))
#     tmp["not assigned"] = True
#     tmp["callback"] = lambda context, value: del_var(value)
#     for i in environ["args_pure"].values():
#         if "not assigned" not in i: del_var(rsx_to_py_value(i))
#     return tmp
# 
# @tools.create_function(tools.IntType(), {"addr1": tools.IntType(), "addr2": tools.IntType()})
# def scale(environ):
#     addr1, addr2 = environ["args"].values()
#     tmp = tools.py_to_rsx_value(add_var(glm.scale(get_var(addr1), get_var(addr2))))
#     tmp["not assigned"] = True
#     tmp["callback"] = lambda context, value: del_var(value)
#     for i in environ["args_pure"].values():
#         if "not assigned" not in i: del_var(rsx_to_py_value(i))
#     return tmp
# 
# @tools.create_function(tools.IntType(), {"addr1": tools.IntType(), "val": tools.FloatType(), "addr2": tools.IntType()})
# def rotate(environ):
#     addr1, val, addr2 = environ["args"].values()
#     tmp = tools.py_to_rsx_value(add_var(glm.rotate(get_var(addr1), val, get_var(addr2))))
#     tmp["not assigned"] = True
#     tmp["callback"] = lambda context, value: del_var(value)
#     for i in [environ["args_pure"]["addr1"], environ["args_pure"]["addr2"]]:
#         if "not assigned" not in i: del_var(rsx_to_py_value(i))
#     return tmp
# 
# @tools.create_function(tools.IntType(), {"addr1": tools.IntType(), "addr2": tools.IntType()})
# def cross(environ):
#     addr1, addr2 = environ["args"].values()
#     tmp = tools.py_to_rsx_value(add_var(glm.cross(get_var(addr1), get_var(addr2))))
#     tmp["not assigned"] = True
#     tmp["callback"] = lambda context, value: del_var(value)
#     for i in environ["args_pure"].values():
#         if "not assigned" not in i: del_var(rsx_to_py_value(i))
#     return tmp
# 
# @tools.create_function(tools.IntType(), {"addr": tools.IntType()})
# def normalize(environ):
#     addr, = environ["args"].values()
#     tmp = tools.py_to_rsx_value(add_var(glm.normalize(get_var(addr))))
#     tmp["not assigned"] = True
#     tmp["callback"] = lambda context, value: del_var(value)
#     for i in environ["args_pure"].values():
#         if "not assigned" not in i: del_var(rsx_to_py_value(i))
#     return tmp
# 
# @tools.create_function(tools.IntType(), {"fov": tools.FloatType(), "aspect": tools.FloatType(), "near": tools.FloatType(), "far": tools.FloatType()})
# def perspective(environ):
#     fov, aspect, near, far = environ["args"].values()
#     tmp = tools.py_to_rsx_value(add_var(glm.perspective(fov, aspect, near, far)))
#     tmp["not assigned"] = True
#     tmp["callback"] = lambda context, value: del_var(value)
#     return tmp
# 
# globals()["rsxglm"].update(tools.pack_library())