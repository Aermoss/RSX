from rsharp.tools import *

create_library("rsxstr")

@create_function("STRING", {"a": "STRING", "b": "STRING"})
def addstr(environment):
    return environment["args"]["a"] + environment["args"]["b"]

@create_function("STRING", {"a": "STRING", "b": "INT"})
def mulstr(environment):
    return environment["args"]["a"] * environment["args"]["b"]

@create_function("STRING", {"a": "BOOL"})
def btos(environment):
    return str(environment["args"]["a"]).lower()

@create_function("STRING", {"a": "FLOAT"})
def ftos(environment):
    return str(environment["args"]["a"])

@create_function("STRING", {"a": "INT"})
def itos(environment):
    return str(environment["args"]["a"])

@create_function("BOOL", {"a": "STRING"})
def stob(environment):
    if environment["args"]["a"] == "true": return True
    else: return False

@create_function("FLOAT", {"a": "STRING"})
def stof(environment):
    return float(environment["args"]["a"].lower().replace("f", ""))

@create_function("INT", {"a": "STRING"})
def stoi(environment):
    return int(environment["args"]["a"])

rsxstr = pack_library()