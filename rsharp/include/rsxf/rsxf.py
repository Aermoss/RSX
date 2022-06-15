from rsharp.tools import *

import os, shutil

create_library("rsxf")

@create_function("STRING", {"name": "STRING"})
def read(environment):
    return open(environment["args"]["name"], "r").read()

@create_function("VOID", {"name": "STRING", "text": "STRING"})
def write(environment):
    open(environment["args"]["name"], "w").write(environment["args"]["text"])

@create_function("VOID", {"name": "STRING"})
def mkfile(environment):
    open(environment["args"]["name"], "w")

@create_function("VOID", {"name": "STRING"})
def rmfile(environment):
    os.remove(environment["args"]["name"])

@create_function("VOID", {"name": "STRING"})
def mkdir(environment):
    os.mkdir(environment["args"]["name"])

@create_function("VOID", {"name": "STRING"})
def rmdir(environment):
    os.rmdir(environment["args"]["name"])

@create_function("VOID", {"name": "STRING"})
def rmtree(environment):
    shutil.rmtree(environment["args"]["name"])

@create_function("VOID", {"name": "STRING"})
def copyfile(environment):
    shutil.copyfile(environment["args"]["name"], environment["args"]["dir"])

@create_function("VOID", {"name": "STRING"})
def copytree(environment):
    shutil.copytree(environment["args"]["name"], environment["args"]["dir"])

rsxf = pack_library()