import rsxpy.rsxlib as rsxlib

import tkinter.messagebox as msgbox

rsxlib.begin()

def showinfo(title: str, message: str) -> str:
    return msgbox.showinfo(title = title, message = message)

def showwarning(title: str, message: str) -> str:
    return msgbox.showwarning(title = title, message = message)

def showerror(title: str, message: str) -> str:
    return msgbox.showerror(title = title, message = message)

def askquestion(title: str, message: str) -> str:
    return msgbox.askquestion(title = title, message = message)

def askokcancel(title: str, message: str) -> bool:
    return msgbox.askokcancel(title = title, message = message)

def askretrycancel(title: str, message: str) -> bool:
    return msgbox.askretrycancel(title = title, message = message)

def askyesno(title: str, message: str) -> bool:
    return msgbox.askyesno(title = title, message = message)

def askyesnocancel(title: str, message: str) -> bool:
    return msgbox.askyesnocancel(title = title, message = message)

rsxlib.end()