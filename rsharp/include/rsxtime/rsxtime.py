from rsharp.tools import *

import time as t
import datetime as dt

create_library("rsxtime")

@create_function("FLOAT", {})
def time(environment):
    return t.time()

@create_function("VOID", {"time": "FLOAT"})
def sleep(environment):
    t.sleep(environment["args"]["time"])

rsxtime = pack_library()