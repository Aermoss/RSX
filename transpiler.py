import ctypes, sys
import importlib, os

def python(ast, file, spaces = 0, base = True, defined_functions = {}):
    imports = ""
    code = ""

    defined_functions["system"] = "os.system"

    def set_text_attr(color):
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32. SetConsoleTextAttribute(console_handle, color)

    def error(message, file = file, type = "error", terminated = False):
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(12)
        print(f"{type}: ", end = "", flush = True)
        set_text_attr(7)
        print(message, end = "\n", flush = True)
        if terminated: print("program terminated.")
        sys.exit(-1)

    def warning(message, file = file, type = "warning"):
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(13)
        print(f"{type}: ", end = "", flush = True)
        set_text_attr(7)
        print(message, end = "\n", flush = True)

    librarys = {
        "aerio": {
            "functions": {
                "writeline": "print"
            },
            "import_names": []
        },
        "aertime":{
            "functions": {},
            "import_names": ["time", "datetime"]
        },
        "aermath": {
            "functions": {},
            "import_names": ["math"]
        },
        "aersys": {
            "functions": {},
            "import_names": ["sys"]
        },
        "aerstr": {
            "functions": {},
            "import_names": ["string"]
        }
    }

    for i in ast:
        if i["type"] == "include":
            if i["value"] in librarys:
                if i["all"]: 
                    defined_functions.update(librarys[i["value"]]["functions"])
                
                else:
                    for j in librarys[i["value"]]["functions"].keys():
                        defined_functions[i["value"] + "." + j] = librarys[i["value"]]["functions"][j]

                for j in librarys[i["value"]]["import_names"]:
                    imports += spaces * " " + "import" + " " + j + "\n"

            else:
                warning("module '" + i["value"] + "'" + " " + "was not implemented", file)

        elif i["type"] == "call":
            if i["name"] in defined_functions:
                args = ""

                for j in i["args"]:
                    if j["type"] == "NULL": args += "None" + ", "
                    elif j["type"] == "BOOL": args += j["value"].capitalize() + ", "
                    elif j["type"] == "INT": args += j["value"] + ", "
                    elif j["type"] == "FLOAT": args += j["value"].lower().replace("f", "") + ", "
                    elif j["type"] == "STRING": args += "\"" + j["value"] + "\"" + ", "
                    elif j["type"] == "NAME": args += j["value"] + ", "
                    else: error("unknown type")

                code += spaces * " " + defined_functions[i["name"]] + "(" + args + ")" + "\n"

            else:
                error("'" + i["name"] + "'" + " " + "was not declared in this scope")

        elif i["type"] == "func":
            args = ""

            for j in i["args"]:
                if i["args"][j] == "STRING": args += j + ": " + "str" + ", "
                elif i["args"][j] == "INT": args += j + ": " + "int" + ", "
                elif i["args"][j] == "FLOAT": args += j + ": " + "float" + ", "
                elif i["args"][j] == "STRING": args += j + ": " + "int" + ", "
                else: error("unknown type")

            if i["return_type"] == "STRING": code += spaces * " " + "def" + " " + i["name"] + "(" + args + ")" + " " + "->" + " " + "str" + ":" + "\n"
            elif i["return_type"] == "INT": code += spaces * " " + "def" + " " + i["name"] + "(" + args + ")" + " " + "->" + " " + "int" + ":" + "\n"
            elif i["return_type"] == "FLOAT": code += spaces * " " + "def" + " " + i["name"] + "(" + args + ")" + " " + "->" + " " + "float" + ":" + "\n"
            elif i["return_type"] == "BOOL": code += spaces * " " + "def" + " " + i["name"] + "(" + args + ")" + " " + "->" + " " + "bool" + ":" + "\n"
            elif i["return_type"] in ["AUTO", "VOID"]: code += spaces * " " + "def" + " " + i["name"] + "(" + args + "):" + "\n"
            else: error("unknown type")

            temp_imports, temp_code = python(i["ast"], file, spaces + 4, False, defined_functions)
            imports += temp_imports
            code += temp_code
            code += "\n"
            defined_functions[i["name"]] = i["name"]

            if i["name"] == "main":
                imports += "import sys, os" + "\n"
                code += "if __name__ == \"__main__\":" + "\n"
                code += 4 * " " + "sys.exit(main())" + "\n"

        elif i["type"] == "return":
            if list(i["value"].keys())[0] == "NULL": code += spaces * " " + "return" + " " + "None" + "\n"
            elif list(i["value"].keys())[0] == "BOOL": code += spaces * " " + "return" + " " + list(i["value"].values())[0].capitalize() + "\n"
            elif list(i["value"].keys())[0] == "INT": code += spaces * " " + "return" + " " + list(i["value"].values())[0] + "\n"
            elif list(i["value"].keys())[0] == "FLOAT": code += spaces * " " + "return" + " " + list(i["value"].values())[0].lower().replace("f", "") + "\n"
            elif list(i["value"].keys())[0] == "STRING": code += spaces * " " + "return" + " " + "\"" + list(i["value"].values())[0] + "\"" + "\n"
            elif list(i["value"].keys())[0] == "NAME": code += spaces * " " + "return" + " " + list(i["value"].values())[0] + "\n"
            else: error("unknown type")

    if base:
        with open(os.path.splitext(file)[0] + ".py", "w") as file:
            file.write(imports + "\n" + code)

    return imports, code