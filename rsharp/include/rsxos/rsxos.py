from rsharp.tools import *
from rsharp.main import *

import sys, os

create_library("rsxos")

@create_function("STRING", {})
def getcwd(environment):
    return os.getcwd()

@create_function("VOID", {"path": "STRING"})
def chdir(environment):
    os.chdir(environment["args"]["path"])

rsxos = pack_library()