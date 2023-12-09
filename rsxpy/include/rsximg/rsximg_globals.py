from rsxpy.tools import *

var_dict = {}

def get_var(index):
    if index not in var_dict: error("unknown variable", "<rsximg>/rsximg_globals.py")
    else: return var_dict[index]

def get_unique_index():
    index = 1

    while index in var_dict:
        index += 1

    return index

def del_var(index):
    del var_dict[index]

def add_var(var):
    index = get_unique_index()
    var_dict[index] = var
    add_scope_trigger(rsxlib.context(), del_var, [index])
    return index

def _add_var_float_arr(environ):
    index = get_unique_index()
    var = environ["args"]["var"]
    var = (ctypes.c_float * len(var))(*var)
    var_dict[index] = var
    return index

def _add_var_int_arr(environ):
    index = get_unique_index()
    var = environ["args"]["var"]
    var = (ctypes.c_uint32 * len(var))(*var)
    var_dict[index] = var
    return index

def _del_var(environ):
    del var_dict[environ["args"]["index"]]

create_library("rsximg_globals")
create_function("VOID", {"index": "INT"})(_del_var)
create_function("INT", {"var": {"type": "ARRAY", "array_type": "INT"}})(_add_var_int_arr)
create_function("INT", {"var": {"type": "ARRAY", "array_type": "FLOAT"}})(_add_var_float_arr)
rsximg_globals = pack_library()