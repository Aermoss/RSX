import rsxpy.tools as tools

import msvcrt

tools.create_library("rsxterm")

@tools.create_function("VOID", {"style": "INT"})
def set_text_attr(environment):
    tools.set_text_attr(environment["args"]["style"])

@tools.create_function("VOID", {})
def getch(environment):
    msvcrt.getch()

rsxterm = tools.pack_library()