from rsxpy.tools import *

import random as rand

create_library("rsxrand")

@create_function("FLOAT", {})
def random(environment):
    return rand.random()

@create_function("INT", {"min": "INT", "max": "INT"})
def randint(environment):
    return rand.randint(environment["args"]["min"], environment["args"]["max"])

@create_function("INT", {"min": "INT", "max": "INT", "step": "INT"})
def randrange(environment):
    return rand.randrange(environment["args"]["min"], environment["args"]["max"], environment["args"]["step"])

@create_function("FLOAT", {"min": "FLOAT", "max": "FLOAT"})
def uniform(environment):
    return rand.uniform(environment["args"]["min"], environment["args"]["max"])

rsxrand = pack_library()