from rsxpy.tools import *

create_library("rsxstd")

@create_function("STRING", {})
def getfile(environment):
    return environment["file"]

rsxstd = pack_library()