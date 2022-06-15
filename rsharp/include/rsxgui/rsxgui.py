from rsharp.tools import *

import ctypes, tkinter

create_library("rsxgui")

root = None

@create_function("INT", {"msg": "STRING", "title": "STRING", "style": "INT"})
def msgbox(environment):
    return ctypes.windll.user32.MessageBoxW(0, environment["args"]["msg"], environment["args"]["title"], environment["args"]["style"])

@create_function("VOID", {"title": "STRING", "width": "INT", "height": "INT"})
def init(environment):
    global root
    root = tkinter.Tk()
    root.title(environment["args"]["title"])
    root.geometry(str(environment["args"]["width"]) + "x" + str(environment["args"]["height"]))

@create_function("VOID", {})
def run(environment):
    if root != None: root.mainloop()
    else: error("aergui was not initialized", environment["file"])

@create_function("VOID", {"label": "STRING", "font": "STRING", "size": "INT", "x": "FLOAT", "y": "FLOAT", "anchor": "STRING"})
def add_label(environment):
    if root != None:
        message = tkinter.Label(root, text = environment["args"]["label"], font = (environment["args"]["font"], environment["args"]["size"]))
        message.place(relx = environment["args"]["x"], rely = environment["args"]["y"], anchor = environment["args"]["anchor"])

    else: error("aergui was not initialized", environment["file"])

rsxgui = pack_library()