from rsharp.tools import *

create_library("rsxstd")

@create_function("STRING", {})
def getfile(environment):
    return environment["file"]

@create_function("BOOL", {"a": "STRING", "b": "STRING"})
def ifeqstr(environment):
    if environment["args"]["a"] == environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "STRING", "b": "STRING"})
def ifnoteqstr(environment):
    if environment["args"]["a"] != environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "BOOL", "b": "BOOL"})
def ifeqbool(environment):
    if environment["args"]["a"] == environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "BOOL", "b": "BOOL"})
def ifnoteqbool(environment):
    if environment["args"]["a"] != environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "INT", "b": "INT"})
def ifeqint(environment):
    if environment["args"]["a"] == environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "INT", "b": "INT"})
def ifnoteqint(environment):
    if environment["args"]["a"] != environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "INT", "b": "INT"})
def ifgtint(environment):
    if environment["args"]["a"] > environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "INT", "b": "INT"})
def ifltint(environment):
    if environment["args"]["a"] < environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "INT", "b": "INT"})
def ifgeint(environment):
    if environment["args"]["a"] >= environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "INT", "b": "INT"})
def ifleint(environment):
    if environment["args"]["a"] <= environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "FLOAT", "b": "FLOAT"})
def ifeqfloat(environment):
    if environment["args"]["a"] == environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "FLOAT", "b": "FLOAT"})
def ifnoteqfloat(environment):
    if environment["args"]["a"] != environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "FLOAT", "b": "FLOAT"})
def ifgtfloat(environment):
    if environment["args"]["a"] > environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "FLOAT", "b": "FLOAT"})
def ifltfloat(environment):
    if environment["args"]["a"] < environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "FLOAT", "b": "FLOAT"})
def ifgefloat(environment):
    if environment["args"]["a"] >= environment["args"]["b"]: return True
    else: return False

@create_function("BOOL", {"a": "FLOAT", "b": "FLOAT"})
def iflefloat(environment):
    if environment["args"]["a"] <= environment["args"]["b"]: return True
    else: return False

@create_function("VOID", {"a": "STRING", "b": "STRING", "func": "STRING"})
def ifeqstr_callback(environment):
    if environment["args"]["a"] == environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "STRING", "b": "STRING", "func": "STRING"})
def ifnoteqstr_callback(environment):
    if environment["args"]["a"] != environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "BOOL", "b": "BOOL", "func": "STRING"})
def ifeqbool_callback(environment):
    if environment["args"]["a"] == environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "BOOL", "b": "BOOL", "func": "STRING"})
def ifnoteqbool_callback(environment):
    if environment["args"]["a"] != environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "INT", "b": "INT", "func": "STRING"})
def ifeqint_callback(environment):
    if environment["args"]["a"] == environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "INT", "b": "INT", "func": "STRING"})
def ifnoteqint_callback(environment):
    if environment["args"]["a"] != environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "INT", "b": "INT", "func": "STRING"})
def ifgtint_callback(environment):
    if environment["args"]["a"] > environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "INT", "b": "INT", "func": "STRING"})
def ifltint_callback(environment):
    if environment["args"]["a"] < environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "INT", "b": "INT", "func": "STRING"})
def ifgeint_callback(environment):
    if environment["args"]["a"] >= environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "INT", "b": "INT", "func": "STRING"})
def ifleint_callback(environment):
    if environment["args"]["a"] <= environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "FLOAT", "b": "FLOAT", "func": "STRING"})
def ifeqfloat_callback(environment):
    if environment["args"]["a"] == environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "FLOAT", "b": "FLOAT", "func": "STRING"})
def ifnoteqfloat_callback(environment):
    if environment["args"]["a"] != environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "FLOAT", "b": "FLOAT", "func": "STRING"})
def ifgtfloat_callback(environment):
    if environment["args"]["a"] > environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "FLOAT", "b": "FLOAT", "func": "STRING"})
def ifltfloat_callback(environment):
    if environment["args"]["a"] < environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "FLOAT", "b": "FLOAT", "func": "STRING"})
def ifgefloat_callback(environment):
    if environment["args"]["a"] >= environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"a": "FLOAT", "b": "FLOAT", "func": "STRING"})
def iflefloat_callback(environment):
    if environment["args"]["a"] <= environment["args"]["b"]: run_function(environment["args"]["func"], environment)

@create_function("VOID", {"condition_func": "STRING", "loop_func": "STRING"})
def while_callback(environment):
    while run_function(environment["args"]["condition_func"], environment) == True:
        run_function(environment["args"]["loop_func"], environment)

@create_function("BOOL", {"a": "BOOL"})
def bnot(environment):
    return not environment["args"]["a"]

@create_function("BOOL", {"a": "BOOL", "b": "BOOL"})
def band(environment):
    return environment["args"]["a"] and environment["args"]["b"]

rsxstd = pack_library()