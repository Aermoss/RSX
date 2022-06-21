import os, sys

sys.dont_write_bytecode = True

import rsharp as rsx

rsx.builder.build(
    path = "rsharp.exe",
    console = True
)