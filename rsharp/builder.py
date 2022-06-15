import os, sys, shutil

sys.dont_write_bytecode = True

import __main__

def build(path, name, console, imports):
    if console: console = "--console"
    else: console = "--noconsole"
    hidden_imports = ""
    for i in imports: hidden_imports += "--hidden-import=" + i + " "

    os.chdir(os.path.split(__file__)[0])
    os.system(f"pyinstaller main.py {console} --noconfirm --onefile --clean --icon=icon.ico {hidden_imports}")

    with open("dist/main.exe", "rb") as file:
        data = file.read()

    shutil.rmtree("build", ignore_errors = True)
    shutil.rmtree("dist", ignore_errors = True)
    os.remove("main.spec")
        
    if "__pycache__" in os.listdir():
        shutil.rmtree("__pycache__", ignore_errors = True)

    os.chdir(os.path.split(__main__.__file__)[0])

    with open(path + name, "wb") as file:
        file.write(data)

def build_program(path, name, include_folders, console, imports):
    with open(path + name, "r") as file:
        file_content = file.read()

    os.chdir(os.path.split(__file__)[0])

    code = "from rsharp.main import *\n"
    code += "\n"
    code += "code = \"\"\""
    code += file_content
    code += "\"\"\"\n"
    code += "\n"
    code += "variables = {}\n"
    code += "functions = {}\n"
    code += "library_functions = {}\n"
    code += "create_json = False\n"
    code += f"name = \"{name}\"\n"
    code += "include_folders = ["

    for index, i in enumerate(include_folders):
        code += "\"" + i + "\""

        if index != len(include_folders) - 1:
            code +=  + ", "

    code += "]\n"
    code += "\n"
    code += "interpreter(parser(lexer(code, name, create_json), name, create_json), name, True, False, functions, variables, None, library_functions, include_folders, create_json)"
    
    with open("temp.py", "w") as file:
        file.write(code)

    if console: console = "--console"
    else: console = "--noconsole"
    hidden_imports = ""
    for i in imports: hidden_imports += "--hidden-import=" + i + " "

    os.system(f"pyinstaller temp.py {console} --noconfirm --onefile --clean --icon=icon.ico {hidden_imports}")

    with open("dist/temp.exe", "rb") as file:
        data = file.read()

    shutil.rmtree("build", ignore_errors = True)
    shutil.rmtree("dist", ignore_errors = True)
    os.remove("temp.spec")
    os.remove("temp.py")
        
    if "__pycache__" in os.listdir():
        shutil.rmtree("__pycache__", ignore_errors = True)

    os.chdir(os.path.split(__main__.__file__)[0])

    with open(f"{os.path.splitext(path + name)[0]}.exe", "wb") as file:
        file.write(data)