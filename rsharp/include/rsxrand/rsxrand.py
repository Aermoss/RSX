from rsharp.tools import *

import random

create_library("rsxrand")

@create_function("INT", {"min": "INT", "max": "INT"})
def randint(environment):
    return random.randint(environment["args"]["min"], environment["args"]["max"])

rsxrand = pack_library()