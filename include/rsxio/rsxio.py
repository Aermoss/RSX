from tools import *

create_library("rsxio")

@create_function("VOID", {"text": "STRING"})
def rout(environment):
    if environment["args"]["text"] == None: print("null", end = "", flush = True)
    else: print(environment["args"]["text"], end = "", flush = True)

@create_function("STRING", {})
def rin(environment):
    return input()

rsxio = pack_library()