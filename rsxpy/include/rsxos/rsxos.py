from rsxpy.tools import *
from rsxpy.core import *

import sys, os

create_library("rsxos")

@create_function("STRING", {})
def getcwd(environment):
    return os.getcwd()

@create_function("VOID", {"path": "STRING"})
def chdir(environment):
    os.chdir(environment["args"]["path"])

@create_function("STRING", {})
def getlogin(environment):
    return os.getlogin()

rsxos = pack_library()