from rsharp.tools import *

import msvcrt

create_library("rsxterm")

@create_function("VOID", {"style": "INT"})
def set_text_attr(environment):
    console_handle = ctypes.windll.kernel32.GetStdHandle(-11)
    ctypes.windll.kernel32. SetConsoleTextAttribute(console_handle, environment["args"]["style"])

@create_function("VOID", {})
def getch(environment):
    msvcrt.getch()

rsxterm = pack_library()