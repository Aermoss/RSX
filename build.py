import os, sys

sys.dont_write_bytecode = True

import rsxpy as rsx

rsx.builder.build(
    path = "rsx.exe",
    console = True
)

rsx.builder.build_raid(
    path = "raid.exe"
)