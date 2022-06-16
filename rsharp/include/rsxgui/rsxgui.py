from rsharp.tools import *

import ctypes

create_library("rsxgui")

@create_function("INT", {"msg": "STRING", "title": "STRING", "style": "INT"})
def msgbox(environment):
    return ctypes.windll.user32.MessageBoxW(0, environment["args"]["msg"], environment["args"]["title"], environment["args"]["style"])

rsxgui = pack_library()