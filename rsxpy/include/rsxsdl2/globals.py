from rsxpy.tools import *

values = {}

def get_unique_index():
    index = 0

    while index in values:
        index += 1

    return index

def get_var(index):
    if index not in values: error("unknown variable", "<rsxsdl2>/globals.py")
    else: return values[index]

def add_var(var):
    index = get_unique_index()
    values[index] = var
    return index

def del_var(index):
    del values[index]