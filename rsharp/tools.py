import rsharp.main as core

import ctypes, sys
import importlib, os

import __main__

def read_file(file_path):
        return open(file_path, "r").read() + "\n"

def include_library(file, namespace, enviroment):
    name, ext = os.path.splitext(file)

    if ext == ".py":
        file_path = None
        
        for j in enviroment["include_folders"]:
            if os.path.exists(j + "/" + file):
                file_path = j + "/" + file
                break

        if file_path == None: error("'" + file + "'" + " " + "was not found")

        if os.path.split(file_path)[0] not in sys.path:
            sys.path.append(os.path.split(file_path)[0])

        temp = getattr(importlib.import_module(os.path.split(name)[1]), os.path.split(name)[1])

        if namespace:
            library = {"functions": {}, "variables": {}}

            for j in temp["functions"].keys():
                library["functions"][os.path.split(name)[1] + "." + j] = temp["functions"][j]

            enviroment["library_functions"].update(library["functions"])
        
        else:
            enviroment["library_functions"].update(temp["functions"])

    else:
        file_path = None

        if ext == ".rsxh":
            for j in enviroment["include_folders"]:
                if os.path.exists(j + "/" + file):
                    file_path = j + "/" + file
                    break

        else:
            for j in enviroment["include_folders"]:
                if os.path.exists(j + "/" + file + "/" + "init.rsxh"):
                    file_path = j + "/" + file + "/" + "init.rsxh"
                    break

        if file_path == None:
            error("'" + file + "'" + " " + "was not found")

        temp = core.interpreter(core.parser(core.lexer(read_file(file_path), file_path, enviroment["create_json"]), file_path, enviroment["create_json"]), file_path, False, False, {}, {}, None, {}, enviroment["include_folders"], enviroment["create_json"])

        if namespace:
            library = {"functions": {}, "variables": {}}

            for j in temp[1].keys():
                library["functions"][os.path.split(file)[1] + "." + j] = temp[1][j]

            for j in temp[0].keys():
                library["variables"][os.path.split(file)[1] + "." + j] = temp[0][j]

            enviroment["variables"].update(library["variables"])
            enviroment["functions"].update(library["functions"])
        
        else:
            enviroment["variables"].update(temp[0])
            enviroment["functions"].update(temp[1])

        enviroment["library_functions"].update(temp[2])

def set_text_attr(color):
    console_handle = ctypes.windll.kernel32.GetStdHandle(-11)
    ctypes.windll.kernel32. SetConsoleTextAttribute(console_handle, color)

def error(msg, file, type = "error", terminated = False):
    print(f"{file}:", end = " ", flush = True)
    set_text_attr(12)
    print(f"{type}: ", end = "", flush = True)
    set_text_attr(7)
    print(msg, end = "\n", flush = True)
    if terminated: print("program terminated.")
    sys.exit(-1)

def warning(message, file, type = "warning"):
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(13)
        print(f"{type}: ", end = "", flush = True)
        set_text_attr(7)
        print(message, end = "\n", flush = True)

def create_library(name):
    setattr(__main__, "name", name)
    setattr(__main__, name, {"functions": {}, "variables": {}})

def pack_library():
    temp = getattr(__main__, getattr(__main__, "name"))
    delattr(__main__, getattr(__main__, "name"))
    delattr(__main__, "name")
    return temp

def create_function(type, args):
    def inner(func):
        getattr(__main__, getattr(__main__, "name"))["functions"][func.__name__] = {"type": type, "args": args, "func": func}

    return inner

def create_variable(name, value):
    if value == None: value = {"NULL": "NULL"}
    elif type(value) == int: value = {"INT": str(value)}
    elif type(value) == float: value = {"FLOAT": str(value)}
    elif type(value) == bool: value = {"BOOL": str(value).upper()}
    elif type(value) == str: value = {"STRING": str(value)}
    else: error("unknown type")

    getattr(__main__, getattr(__main__, "name"))["variables"][name] = value

def create_variables(variables):
    for i in variables:
        create_variable(i, variables[i])

def run_function(name, enviroment):
    temp = core.interpreter(enviroment["functions"][name]["ast"], enviroment["file"], False, False, enviroment["functions"], enviroment["variables"], enviroment["functions"][name]["type"], enviroment["library_functions"])

    if temp == None: return None
    if list(temp.keys())[0] == "INT": return int(list(temp.values())[0])
    elif list(temp.keys())[0] == "FLOAT": return float(list(temp.values())[0].lower().replace("f", ""))

    elif list(temp.keys())[0] == "BOOL":
        if list(temp.values())[0].lower() == "true": return True
        elif list(temp.values())[0].lower() == "false": return False
        else: error("unknown value", enviroment["file"])

    elif list(temp.keys())[0] == "STRING": return list(temp.values())[0]
    elif list(temp.keys())[0] == "NULL": return None
    else: error("unknown type", enviroment["file"])

def get_variable(name, enviroment):
    var = enviroment["variables"][name]

    if var["type"] == "INT": return int(var["value"])
    elif var["type"] == "FLOAT": return float(var["value"].lower().replace("f", ""))

    elif var["type"] == "BOOL":
        if var["value"].lower() == "true": return True
        elif var["value"].lower() == "false": return False
        else: error("unknown value", enviroment["file"])

    elif var["type"] == "STRING": return var["value"]
    elif var["type"] == "NULL": return None
    else: error("unknown type", enviroment["file"])

def get_variable_type(name, enviroment):
    return enviroment["variables"][name]["type"]