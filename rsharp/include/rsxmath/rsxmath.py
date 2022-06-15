from rsharp.tools import *

create_library("rsxmath")

@create_function("INT", {"a": "INT", "b": "INT"})
def add(environment):
    return environment["args"]["a"] + environment["args"]["b"]

@create_function("INT", {"a": "INT", "b": "INT"})
def sub(environment):
    return environment["args"]["a"] - environment["args"]["b"]

@create_function("INT", {"a": "INT", "b": "INT"})
def mul(environment):
    return environment["args"]["a"] * environment["args"]["b"]

@create_function("INT", {"a": "INT", "b": "INT"})
def div(environment):
    return int(environment["args"]["a"] / environment["args"]["b"])

@create_function("INT", {"a": "INT", "b": "INT"})
def pow(environment):
    return environment["args"]["a"] ** environment["args"]["b"]

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def addf(environment):
    return environment["args"]["a"] + environment["args"]["b"]

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def subf(environment):
    return environment["args"]["a"] - environment["args"]["b"]

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def mulf(environment):
    return environment["args"]["a"] * environment["args"]["b"]

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def divf(environment):
    return environment["args"]["a"] / environment["args"]["b"]

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def powf(environment):
    return environment["args"]["a"] ** environment["args"]["b"]

@create_function("INT", {"a": "FLOAT"})
def ftoi(environment):
    return int(environment["args"]["a"])

@create_function("FLOAT", {"a": "INT"})
def itof(environment):
    return float(environment["args"]["a"])

rsxmath = pack_library()