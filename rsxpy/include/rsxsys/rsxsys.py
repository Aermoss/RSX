from rsxpy.tools import *
from rsxpy.core import *

import sys

create_library("rsxsys")

@create_function("VOID", {"name": "STRING"})
def run(environment):
    return run_function(environment["args"]["name"], environment["context"])

@create_function("VOID", {"code": "STRING"})
def eval(environment):
    context = environment["context"]
    tmp = context.ast
    context.ast = parser(lexer(environment["args"]["code"], "<eval>"), "<eval>")
    tmp_ret = context.current_return_type
    context.current_return_type = None
    tmp_val = interpreter(context)
    context.current_return_type = tmp_ret
    context.ast = tmp

@create_function("VOID", {"code": "INT"})
def exit(environment):
    sys.exit(environment["args"]["code"])

@create_function("VOID", {"message": "STRING"})
def warning(environment):
    warning(environment["args"]["message"], environment["file"])

@create_function("VOID", {"message": "STRING"})
def error(environment):
    error(environment["args"]["message"], environment["file"])

@create_function("BOOL", {"name": "STRING"})
def hasattr(environment):
    if environment["context"].isexists(environment["args"]["name"]): return True
    else: return False

@create_function("STRING", {"name": "STRING"})
def gettype(environment):
    return get_variable_type(environment["args"]["name"], environment["context"]).lower()

@create_function("VOID", {"name": "STRING", "namespace": "BOOL"})
def include_library(environment):
    include_library(environment["args"]["name"], environment["args"]["namespace"], environment["context"])

@create_function("VOID", {"dir": "STRING"})
def add_include_folder(environment):
    environment["include_folders"].append(environment["args"]["dir"])

@create_function("VOID", {"limit": "INT"})
def set_reqursion_limit(environment):
    environment["context"].recursion_limit = environment["args"]["limit"]

@create_function("BOOL", {})
def iscompiled(environment):
    return is_compiled()

@create_function("STRING", {})
def getdir(environment):
    return get_dir()

@create_function("INT", {})
def maxsize(environment):
    return sys.maxsize

rsxsys = pack_library()