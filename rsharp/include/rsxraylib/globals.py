from rsharp.tools import *

from colors import *

var_dict = colors.copy()

def get_unique_index():
    index = 0

    while index in var_dict:
        index += 1

    return index

def get_var(index):
    if index not in var_dict: error("unknown variable", "<rsxraylib>/globals.py")
    else: return var_dict[index]

def add_var(var):
    index = get_unique_index()
    var_dict[index] = var
    return index

def del_var(index):
    del var_dict[index]