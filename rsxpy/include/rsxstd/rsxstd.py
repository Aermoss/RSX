from rsxpy.tools import *

create_library("rsxstd")

@create_function("STRING", {})
def getfile(environment):
    return environment["file"]

@create_function("INT", {"value": {"type": "ARRAY", "array_type": "INT"}})
def max(environment):
    return max(*(environment["value"]))

@create_function("INT", {"value": {"type": "ARRAY", "array_type": "FLOAT"}})
def maxf(environment):
    return max(*(environment["value"]))

@create_function("INT", {"value": {"type": "ARRAY", "array_type": "INT"}})
def min(environment):
    return min(*(environment["value"]))

@create_function("INT", {"value": {"type": "ARRAY", "array_type": "FLOAT"}})
def minf(environment):
    return min(*(environment["value"]))

rsxstd = pack_library()