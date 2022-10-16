import os, sys, shutil, subprocess

import rsxpy as rsx

import __main__

def build(path, console, hidden_imports = ["raylib", "pysdl2", "pysdl2-dll"]):
    if console: console = "--console"
    else: console = "--noconsole"
    hidden_imports_str = ""
    for i in hidden_imports: hidden_imports_str += "--hidden-import=" + i + " "

    first_dir = os.getcwd()
    os.chdir(rsx.tools.get_dir())
    subprocess.run(f"pyinstaller core.py {console} --noconfirm --clean --name=rsx --paths=include --icon=icon.ico {hidden_imports_str}"[:-1].split(" "))
    shutil.copytree("dist/rsx", first_dir + "/rsx")
    shutil.rmtree("dist", ignore_errors = True)
    shutil.rmtree("build", ignore_errors = True)
    shutil.rmtree("__pycache__", ignore_errors = True)
    os.remove("rsx.spec")
    os.chdir(first_dir)

def build_raid(path):
    first_dir = os.getcwd()
    os.chdir(rsx.tools.get_dir())
    os.chdir("raidpy")
    subprocess.run(f"pyinstaller core.py --noconfirm --clean --name=raid --icon=raid_icon.ico".split(" "))
    shutil.copytree("dist/raid", first_dir + "/raid")
    shutil.rmtree("dist", ignore_errors = True)
    shutil.rmtree("build", ignore_errors = True)
    shutil.rmtree("__pycache__", ignore_errors = True)
    os.remove("raid.spec")
    os.chdir(first_dir)

def build_program(console, context, hidden_imports = ["raylib", "pysdl2", "pysdl2-dll", "tkinter", "tkinter.messagebox"], icon = "icon.ico"):
    with open(context.file.replace("\\", "/"), "r") as file:
        file_content = rsx.preprocessor.preprocessor(file.read(), context.include_folders)

    modules = []
    libfuncs = {}
    rsxlibfuncs = {}
    new_scope = {}

    for i in context.scope:
        new_scope[i] = {}

        for j in context.scope[i]:
            if context.scope[i][j]["type"] == "libfunc":
                if "code" in context.scope[i][j] and "func_name" in context.scope[i][j]:
                    rsxlibfuncs[j] = context.scope[i][j]

                libfuncs[j] = context.scope[i][j]

                if context.scope[i][j]["func"].__module__ not in modules:
                    if not context.scope[i][j]["func"].__module__.startswith("rsxpy"):
                        modules.append(context.scope[i][j]["func"].__module__)

            else:
                new_scope[i][j] = context.scope[i][j]

    code = "import rsxpy as rsx\n\n"
    code += "import sys\n\n"

    for i in modules:
        code += f"{i} = rsx.tools.load_module(\"{i}\")\n"

    code += "\n"

    for i in rsxlibfuncs:
        code += rsxlibfuncs[i]["code"] + "\n"

    new_libfuncs = "{\n"
    index = 0

    for i in libfuncs:
        func_name = libfuncs[i]["func"].__module__.replace("rsxpy", "rsx") + "." + libfuncs[i]["func"].__module__.replace("rsxpy.", "")
        if func_name == "rsx.rsxlib.rsxlib": func_name = rsxlibfuncs[i]["func_name"]

        new_libfuncs += "    \"" + i + "\": {"
        new_libfuncs += "\"type\": \"libfunc\", "
        new_libfuncs += "\"return_type\": \"" + libfuncs[i]["return_type"] + "\", "
        new_libfuncs += "\"args\": " + str(libfuncs[i]["args"]).replace("'", "\"") + ", "
        new_libfuncs += "\"func\": " + func_name + "[\"" + libfuncs[i]["func"].__name__ + "\"][\"func\"], "
        new_libfuncs += "\"const\": False}"

        if index != len(libfuncs) - 1:
            new_libfuncs += ", "

        new_libfuncs += "\n"
        index += 1

    new_libfuncs += "}"

    new_scope_str = ""
    indent = 0

    for i in str(new_scope).replace("'", "\""):
        if i == "{":
            indent += 1
            new_scope_str += "{\n" + (indent * 4 * " ")

        elif i == "}":
            indent -= 1
            new_scope_str += "\n" + (indent * 4 * " ") + "}"

        else:
            new_scope_str += i

    code += "code = \"\"\""
    code += file_content
    code += "\"\"\"\n"
    code += "\n"
    code += f"file = \"{context.file}\"\n"
    code += "\n"
    code += "context = rsx.core.Context(\n"
    code += "    rsx.core.parser(\n"
    code += "        rsx.core.lexer(\n"
    code += "            data = code,\n"
    code += "            file = file\n"
    code += "        ),file = file\n"
    code += "    ), file = file\n"
    code += ")\n\n"
    code += "context.is_compiled_var = True\n"
    code += "context.args = sys.argv.copy()\n"
    code += f"context.scope = {new_scope_str}\n\n"
    code += f"context.scope[\"global\"].update({new_libfuncs})\n\n"
    code += f"context.include_folders = " + str(context.include_folders).replace("'", "\"") + "\n"
    code += f"context.included = " + str(context.included).replace("'", "\"") + "\n"
    code += "\n"
    code += "rsx.core.interpreter(context)"

    paths = []
    paths_only_folder = ["build", "dist", "include"]

    for i in context.include_folders:
        for j in os.listdir(i):
            if os.path.isdir(i + j):
                if os.path.split(i + j)[1] not in paths_only_folder and j != "raidpy":
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
        hidden_imports_str += " "

    first_dir = os.getcwd()
    os.chdir(rsx.tools.get_dir())

    with open("temp.py", "w") as file:
        file.write(code)

    subprocess.run(f"pyinstaller temp.py {console} --noconfirm --onefile --clean {paths_str} --icon={icon} {hidden_imports_str}"[:-1].split(" "))

    with open("dist/" + os.listdir("dist")[0], "rb") as file:
        data = file.read()

    ext = os.path.splitext(os.listdir("dist")[0])[1]

    shutil.rmtree("build", ignore_errors = True)
    shutil.rmtree("dist", ignore_errors = True)
    os.remove("temp.spec")
    os.remove("temp.py")

    if "__pycache__" in os.listdir():
        shutil.rmtree("__pycache__", ignore_errors = True)

    os.chdir(first_dir)
    name = os.path.splitext(context.file.replace("\\", "/"))[0] + ext

    with open(name, "wb") as file:
        file.write(data)