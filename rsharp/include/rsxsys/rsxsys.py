from rsharp.tools import *
from rsharp.main import *

import sys

create_library("rsxsys")

@create_function("VOID", {"name": "STRING"})
def run(environment):
    return run_function(environment["args"]["name"], environment)

@create_function("VOID", {"code": "STRING"})
def eval(environment):
    interpreter(parser(lexer(environment["args"]["code"], "<eval>", False), "<eval>", False), "<eval>", False, environment["functions"], environment["variables"], None, environment["library_functions"], environment["include_folders"], False)

@create_function("VOID", {"code": "INT"})
def exit(environment):
    sys.exit(environment["args"]["code"])

@create_function("VOID", {"message": "STRING"})
def error(environment):
    error(environment["args"]["message"], environment["file"])

@create_function("BOOL", {"name": "STRING"})
def hasattr(environment):
    if environment["args"]["name"] in environment["variables"] or environment["args"]["name"] in environment["functions"] or environment["args"]["name"] in environment["library_functions"]: return True
    else: return False

@create_function("STRING", {"name": "STRING"})
def gettype(environment):
    return get_variable_type(environment["args"]["name"], environment).lower()

@create_function("VOID", {"name": "STRING", "namespace": "BOOL"})
def includelib(environment):
    include_library(environment["args"]["name"], environment["args"]["namespace"], environment)

@create_function("VOID", {"dir": "STRING"})
def add_includedir(environment):
    environment["include_folders"].append(environment["args"]["dir"])

rsxsys = pack_library()