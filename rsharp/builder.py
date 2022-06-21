import os, sys, shutil

import rsharp as rsx

import __main__

def build(path, console, hidden_imports = ["raylib"]):
    if console: console = "--console"
    else: console = "--noconsole"
    hidden_imports_str = ""
    for i in hidden_imports: hidden_imports_str += "--hidden-import=" + i + " "

    first_dir = os.getcwd()
    os.chdir(rsx.tools.get_dir())
    os.system(f"pyinstaller main.py {console} --noconfirm --onefile --clean --paths=include --icon=icon.ico {hidden_imports_str}")

    with open("dist/main.exe", "rb") as file:
        data = file.read()

    shutil.rmtree("build", ignore_errors = True)
    shutil.rmtree("dist", ignore_errors = True)
    os.remove("main.spec")
        
    if "__pycache__" in os.listdir():
        shutil.rmtree("__pycache__", ignore_errors = True)

    os.chdir(first_dir)

    with open(path.replace("\\", "/"), "wb") as file:
        file.write(data)

def build_program(path, include_folders, console, variables, functions, library_functions, pre_included = [], hidden_imports = ["raylib"], icon = "icon.ico"):
    with open(path.replace("\\", "/"), "r") as file:
        file_content = file.read()

    first_dir = os.getcwd()
    os.chdir(rsx.tools.get_dir())

    modules = []

    for i in library_functions:
        if library_functions[i]["func"].__module__ not in modules:
            modules.append(library_functions[i]["func"].__module__)

    code = "import rsharp as rsx\n"
    code += "\n"

    for i in modules:
        code += f"{i} = rsx.tools.load_module(\"{i}\")\n"

    new_library_functions = "{\n"
    index = 0

    for i in library_functions:
        new_library_functions += "    \"" + i + "\": {"
        new_library_functions += "\"type\": \"" + library_functions[i]["type"] + "\", "
        new_library_functions += "\"args\": " + str(library_functions[i]["args"]).replace("'", "\"") + ", "
        new_library_functions += "\"func\": " + library_functions[i]["func"].__module__ + "." + library_functions[i]["func"].__module__ + "[\"functions\"]" + "[\"" + library_functions[i]["func"].__name__ + "\"][\"func\"]}"

        if index != len(library_functions) - 1:
            new_library_functions += ", "

        new_library_functions += "\n"
        index += 1

    new_library_functions += "}"

    code += "\n"
    code += "code = \"\"\""
    code += file_content
    code += "\"\"\"\n"
    code += "\n"
    code += f"variables = " + str(variables).replace("'", "\"") + "\n"
    code += f"functions = " + str(functions).replace("'", "\"") + "\n"
    code += f"library_functions = {new_library_functions}\n"
    code += "create_json = False\n"
    code += f"path = \"{path}\"\n"
    code += f"include_folders = {str(include_folders)}\n"
    code += f"pre_included = {str(pre_included)}\n"
    code += "\n"
    code += "rsx.core.interpreter(\n"
    code += "    rsx.core.parser(\n"
    code += "        rsx.core.lexer(\n"
    code += "            data = code,\n"
    code += "            file = path,\n"
    code += "            create_json = create_json\n"
    code += "        ),"
    code += "        file = path,\n"
    code += "        create_json = create_json\n"
    code += "    ),\n"
    code += "    file = path,\n"
    code += "    isbase = True,\n"
    code += "    islib = False,\n"
    code += "    functions = functions,\n"
    code += "    variables = variables,\n"
    code += "    return_type = None,\n"
    code += "    library_functions = library_functions,\n"
    code += "    include_folders = include_folders,\n"
    code += "    create_json = create_json,\n"
    code += "    pre_included = pre_included\n"
    code += ")"
    
    with open("temp.py", "w") as file:
        file.write(code)

    paths = []
    paths_only_folder = ["build", "dist", "include"]

    for i in include_folders:
        for j in os.listdir(i):
            if os.path.isdir(i + j):
                if os.path.split(i + j)[1] not in paths_only_folder:
                    paths.append(i + j)
                    paths_only_folder.append(os.path.split(i + j)[1])

    paths_str = ""

    for index, i in enumerate(paths):
        paths_str += f"--paths={i}"

        if index != len(paths) - 1:
            paths_str += " "

    for i in paths:
        for j in os.listdir(i):
            if os.path.isfile(i + "\\" + j):
                if os.path.splitext(j)[1] == ".py":
                    if os.path.splitext(j)[0] in modules:
                        hidden_imports.append(os.path.splitext(j)[0])

    if console: console = "--console"
    else: console = "--noconsole"

    hidden_imports_str = ""

    for index, i in enumerate(hidden_imports): 
        hidden_imports_str += "--hidden-import=" + i

        if index != len(hidden_imports) - 1:
            hidden_imports_str += " "

    os.system(f"pyinstaller temp.py {console} --noconfirm --onefile --clean {paths_str} --icon=\"{icon}\" {hidden_imports_str}")

    with open("dist/temp.exe", "rb") as file:
        data = file.read()

    shutil.rmtree("build", ignore_errors = True)
    shutil.rmtree("dist", ignore_errors = True)
    os.remove("temp.spec")
    os.remove("temp.py")

    if "__pycache__" in os.listdir():
        shutil.rmtree("__pycache__", ignore_errors = True)

    os.chdir(first_dir)
    name = os.path.splitext(path.replace("\\", "/"))[0] + ".exe"

    with open(name, "wb") as file:
        file.write(data)