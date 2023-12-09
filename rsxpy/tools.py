import rsxpy.core as core
import rsxpy.rsxlib as rsxlib

import sys, os, string, pickle, traceback
import importlib, ctypes, hashlib

import __main__

environ = {}

def get_requirements():
    return ["raylib", "pyinstaller", "pysdl2", "pysdl2-dll", "glfw", "imgui", "pyglet", "pyglm", "numpy", "pillow", "openvr", "rvr"]

def rsx_struct_to_py_class(value, context):
    return type(value["struct_type"], (object, ), {i: rsx_to_py_value(value["scope"]["public"][i], context, i) for i in value["scope"]["public"]})()

def rsx_to_py_value(value, context = None, name = "<rsx_to_py_value>"):
    if value == None: value = {"type": "NULL", "value": "NULL"}
    if value["type"] == "INT": return int(value["value"])
    elif value["type"] == "FLOAT": return float(value["value"].lower().replace("f", ""))
    elif value["type"] == "BOOL":
        if value["value"].lower() == "true": return True
        elif value["value"].lower() == "false": return False
        else: error("unknown value for bool: '" + value["value"].lower() + "'", "<rsx_to_py_value>")
    elif value["type"] == "STRING": return value["value"]
    elif value["type"] == "NULL": return None
    elif value["type"] == "var": return rsx_to_py_value(value["value"], context, name)
    elif value["type"] == "func": return rsx_to_py_func(name, value, context)
    elif value["type"] == "array_object": return [rsx_to_py_value(i, context, name) for i in value["value"]]
    elif value["type"] == "struct_object": return rsx_struct_to_py_class(value, context)
    else: error("unknown type: '" + str(value["type"]).lower() + "'", "<rsx_to_py_value>")

def py_to_rsx_value(value):
    if type(value) == int: return IntType(value)
    elif type(value) == bool: return BoolType(value)
    elif isinstance(value, float): return FloatType(value)
    elif isinstance(value, str): return StringType(value)
    elif isinstance(value, list): return Array(value)
    elif isinstance(value, dict): return value
    elif value == None: return {"type": "NULL", "value": "NULL"}
    else: error("unknown type", "<py_to_rsx_value>")

class FunctionType:
    def __init__(self, return_type, args):
        self.return_type = return_type
        self.args = args

class VoidType:
    def __new__(self):
        return "VOID"

class IntType:
    def __new__(self, value = None):
        if value == None: return "INT"
        return {"type": "INT", "value": str(value)}

class FloatType:
    def __new__(self, value = None):
        if value == None: return "FLOAT"
        return {"type": "FLOAT", "value": str(value).replace("f", "")}

class BoolType:
    def __new__(self, value = None):
        if value == None: return "BOOL"
        return {"type": "BOOL", "value": str(value).upper()}

class StringType:
    def __new__(self, value = None):
        if value == None: return "STRING"
        return {"type": "STRING", "value": str(value)}

class AnyType:
    def __new__(self):
        return "ANY_T"

class RawArrayType:
    def __new__(self, type = None, size = None):
        if type == None: return "RAW_ARRAY_T"
        return {"type": "RAW_ARRAY_T", "array_type": None if type == AnyType() else type, "size": size}

class ArrayType:
    def __new__(self, type = None, size = None):
        if type == None: return "ARRAY_T"
        return {"type": "ARRAY_T", "array_type": None if type == AnyType() else type, "size": size}

class Array:
    def __new__(self, value = None, type = None, size = None, scope = {"public": {}, "private": {}}):
        if value == None: return "array_object"
        arr = [py_to_rsx_value(i) for i in value]
        scope["public"]["length"] = lambda: {"type": "libfunc", "args": {}, "return_type": "INT", "func": (lambda: size), "const": True}
        return {"type": "array_object", "array_type": arr[0]["type"] if type == None else type, "size": len(arr) if size == None else size, "value": arr, "scope": scope}

class RawStructType:
    def __new__(self, value = None):
        if value == None: return "RAW_STRUCT_T"
        return {"type": "RAW_STRUCT_T", "value": None if value == AnyType() else value}

class StructType:
    def __new__(self, value = None):
        if value == None: return "STRUCT_T"
        return {"type": "STRUCT_T", "value": None if value == AnyType() else value}

def is_array_t(var):
    if "type" in var and var["type"] == ArrayType():
        return True
    
    return False

def is_array(var):
    if "type" in var and var["type"] == Array():
        return True
    
    return False

def get_version():
    return "0.1.2"

def tokens_to_string(tokens):
    pos = 0
    result = ""

    def get(index, pure = False):
        if pure:
            return tokens[index]
            
        else:
            value = tokens[index]

            if isinstance(value, str):
                return value

            else:
                return value["value"]

    reverse_keywords = {core.keywords[key]: key for key in core.keywords.keys()}
    reverse_symbols = {core.symbols[key]: key for key in core.symbols.keys()}
    indent, tolerate = 0, 0

    while pos < len(tokens):
        if get(pos) in core.keywords.values():
            if get(pos) in ["STRING", "CHAR", "DOUBLE", "BOOL", "INT", "FLOAT"] and (get(pos + 1) not in list(core.keywords.values()) + list(core.symbols.values()) + ["IDENTIFIER"] or get(pos + 1) in ["FALSE", "TRUE"]):
                string = get(pos + 1).replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t") \
                                        .replace("\0", "\\0").replace("\'", "\\\'").replace("\"", "\\\"") if get(pos) == "STRING" else get(pos + 1)
                string = string.replace("FALSE", "false").replace("TRUE", "true") if get(pos) == "BOOL" else string
                string = string + ("f" if get(pos) == "FLOAT" else "")
                result += ("\"" if get(pos) == "STRING" else ("\'" if get(pos) == "CHAR" else "")) + string + ("\"" if get(pos) == "STRING" else ("\'" if get(pos) == "CHAR" else ""))
                pos += 2

            else:
                if get(pos) in ["IF", "WHILE"] and pos - 1 > 0 and get(pos - 1) not in ["LCURLYBRACKET", "RCURLYBRACKET"]:
                    start, ignore = pos + 1, 0

                    while get(pos + 1) == "LPAREN":
                        if get(start) == "LPAREN":
                            ignore += 1

                        if get(start) == "RPAREN":
                            ignore -= 1
                            if ignore == 0: break

                        start += 1

                    if get(start + 1) == "LCURLYBRACKET":
                        result += "\n"
                        result += indent * " "

                if get(pos) in ["FOR"]:
                    tolerate += 2

                result += reverse_keywords[get(pos)]

                if get(pos + 1) in ["IDENTIFIER", "STRING", "CHAR", "DOUBLE", "BOOL", "INT", "FLOAT", "LPAREN"]:
                    result += " "

                pos += 1

        elif get(pos) in "IDENTIFIER":
            if pos - 1 > 0 and get(pos - 1) in ["RBRACKET"]:
                result += " "

            result += get(pos + 1)

            if get(pos + 2) in ["IDENTIFIER"]:
                result += " "

            pos += 2

        elif get(pos) in core.symbols.values():
            if reverse_symbols[get(pos)] in ["=", "+", "-", "*", "/", "%", "<", ">"]:
                result += " "

            if reverse_symbols[get(pos)] in ["{"]:
                if pos - 1 > 0 and get(pos - 1) not in ["EQUALS"]:
                    result += " "

                indent += 4

            if reverse_symbols[get(pos)] in ["}"]:
                indent -= 4

            if reverse_symbols[get(pos)] in ["}"]:
                result += "\n"
                result += indent * " "

            result += reverse_symbols[get(pos)]

            if reverse_symbols[get(pos)] in ["}"]:
                if pos + 1 < len(tokens) and get(pos + 1) not in ["RCURLYBRACKET", "SEMICOLON", "ELSE"] + ["ELSE"]:
                    result += "\n"

                if pos + 1 < len(tokens) and get(pos + 1) not in ["SEMICOLON"] + ["ELSE"]:
                    result += "\n"
                    result += indent * " "

                if pos + 1 < len(tokens) and get(pos + 1) in ["ELSE"]:
                    result += " "

            if reverse_symbols[get(pos)] in [")"] and (get(pos + 1) in get(pos + 1) in list(core.keywords.values()) + ["IDENTIFIER", "LPAREN"]):
                result += " "

            if reverse_symbols[get(pos)] in [";", "{"] and not (get(pos + 1) in reverse_symbols and reverse_symbols[get(pos + 1)] in ["}"]):
                if reverse_symbols[get(pos)] in [";"]:
                    if tolerate != 0:
                        result += " "
                        tolerate -= 1
                        pos += 1
                        continue

                result += "\n"
                result += indent * " "

            if reverse_symbols[get(pos)] in ["=", "+", "-", "*", "/", "%", ",", "<", ">"]:
                result += " "

            pos += 1

        else:
            result += get(pos).replace("POSITIVE", "+").replace("NEGATIVE", "-").replace("POSTINCREMENT", "++").replace("POSTDECREMENT", "--").replace("LESSEQUALS", " <= ") \
                    .replace("EQUALSEQUALS", " == ").replace("NOTEQUALS", " != ").replace("PLUSEQUALS", " += ").replace("MINUSEQUALS", " -= ").replace("GREATEREQUALS", " >= ") \
                        .replace("ASTERISKSEQUALS", " *= ").replace("SLASHQUALS", " /= ").replace("MODULUSEQUALS", " %= ").replace("BITWISELEFT", " << ").replace("BITWISERIGHT", " >> ") \
                            .replace("INCREMENT", "++").replace("DECREMENT", "--").replace("BITWISEAND", " & ").replace("BITWISEOR", " | ").replace("AND", " && ").replace("OR", " || ") \
                                .replace("BITWISEXOR", " ^ ").replace("BITWISEOR", " ~ ")
            pos += 1

    return result

def add_scope_trigger(context, target, args):
    context.set(context.get_unique_name(), {"type": "trigger", "target": target, "args": args}, force = True)

def read_file(file, encoding = "utf-8"):
    return open(file, "r", encoding = encoding).read() + "\n"

def dump_bytecode(ast, custom_types, file_content, version = get_version()):
    return pickle.dumps({"ast": ast, "custom_types": custom_types, "file_content": hashlib.sha256(file_content.encode()).digest(), "version": version})

def load_bytecode(bytes):
    return pickle.loads(bytes)

def is_compiled():
    if os.path.splitext(os.path.split(sys.executable)[1])[0] == os.path.splitext(os.path.split(sys.argv[0])[1])[0] and os.path.splitext(os.path.split(sys.argv[0])[1])[1] in [".exe", ""]:
        return True

    return False

def get_dir():
    if is_compiled():
        if os.path.split(sys.argv[0])[0] not in [".", ""]:
            return os.path.split(sys.argv[0])[0] + "/"

        else:
            if sys.platform == "win32":
                return "C:\\RSX\\"

            else:
                return os.path.split(__file__)[0]

    else:
        return os.path.split(__file__)[0]

def remove_libs_bytecode(include_folder = get_dir() + "/include"):
    for folder in [include_folder]:
        for file in os.listdir(folder):
            if os.path.isdir(folder + "/" + file):
                for _file in os.listdir(folder + "/" + file):
                    if os.path.splitext(_file)[1] == ".rsxc":
                        os.remove(folder + "/" + file + "/" + _file)

            elif os.path.splitext(file)[1] == ".rsxc":
                os.remove(folder + "/" + file)

def compile_libs(include_folder = get_dir() + "/include"):
    for i in os.listdir(include_folder):
        print(f"RSX: INFO: byte-compiling: {i}")
        context = core.Context([], "<build>")
        context.include_folders = [include_folder]
        include_library(context, [i], False, None, None)

def recompile_libs(include_folder = get_dir() + "/include"):
    for folder in [include_folder]:
        for file in os.listdir(folder):
            if os.path.isdir(folder + "/" + file):
                for _file in os.listdir(folder + "/" + file):
                    if os.path.splitext(_file)[1] == ".rsxc":
                        os.remove(folder + "/" + file + "/" + _file)

            elif os.path.splitext(file)[1] == ".rsxc":
                os.remove(folder + "/" + file)

    for i in os.listdir(include_folder):
        context = core.Context([], "<build>")
        context.include_folders = [include_folder]
        print(f"RSX: INFO: byte-compiling: {i}")
        include_library(context, [i], False, None, None)

def rsx_to_py_func(name, tree, context):
    def inner(*args, **kwargs):
        context.prepare_to_execute(name)

        if len(tree["args"]) < len(args):
            error(f"argument count didn't match: '{name}'", context.file)

        for index, i in enumerate(tree["args"]):
            if len(args) == index: break
            tmp_ast = context.ast
            context.ast = [{"type": "var", "name": i, "value_type": tree["args"][i], "value": py_to_rsx_value(args[index]), "const": False}]
            tmp_ret = context.current_return_type
            context.current_return_type = None
            core.interpreter(context)
            context.current_return_type = tmp_ret
            context.ast = tmp_ast

        for i in kwargs:
            tmp_ast = context.ast
            context.ast = [{"type": "var", "name": i, "value_type": tree["args"][i], "value": py_to_rsx_value(kwargs[i]), "const": False}]
            tmp_ret = context.current_return_type
            context.current_return_type = None
            core.interpreter(context)
            context.current_return_type = tmp_ret
            context.ast = tmp_ast

        for i in tree["args"]:
            if i not in context.scope[context.current_scope]:
                error(f"argument count didn't match: '{name}'", context.file)

        tmp = rsx_to_py_value(core.interpreter(context))
        context.end_execute()
        return tmp

    inner.__name__ = name
    return inner

def pyrsx_to_py_func(name, tree, context):
    def inner(*args, **kwargs):
        new_args = {}

        if len(tree["args"]) < len(args):
            error(f"argument count didn't match: '{name}'", context.file)

        for index, i in enumerate(tree["args"]):
            if len(args) == index: break
            new_args[i] = args[index]

        for i in kwargs:
            new_args[i] = kwargs[i]

        for i in tree["args"]:
            if i not in new_args:
                error(f"argument count didn't match: '{name}'", context.file)

        enviroment = {
            "args": new_args,
            "file": context.file,
            "scope": context.scope,
            "context": context,
            "include_folders": context.include_folders
        }

        return tree["func"](enviroment)

    inner.__name__ = name
    return inner

def extract(context = None, ast = None, tokens = None, content = None, file = None, include_folders = [(os.path.split(__file__)[0] + "/include")]):
    if file != None:
        content = open(file, "r").read()

    else:
        file = "<extract>"

    if content != None:
        tokens = core.lexer(content, file)

    if tokens != None:
        ast = core.parser(tokens, file)

    if ast != None:
        context = core.Context(ast, file)

    if context == None:
        error("at least one argument must be supplied", file)

    context.program_state(False)
    context.include_folders = include_folders
    core.interpreter(context)

    variables, functions = {}, {}
    
    for i in context.scope["global"]:
        tree = context.scope["global"][i]

        if tree["type"] == "var":
            variables[i] = rsx_to_py_value(tree["value"])

        elif tree["type"] == "func":
            functions[i] = rsx_to_py_func(i, tree, context)

        elif tree["type"] == "libfunc":
            functions[i] = pyrsx_to_py_func(i, tree, context)

    return variables, functions

def import_rsx_library(context = None, ast = None, tokens = None, content = None, file = None, include_folders = [(os.path.split(__file__)[0] + "/include")]):
    variables, functions = extract(context, ast, tokens, content, file, include_folders)
    
    class _inner: ...
    inner = _inner()

    for i in functions:
        setattr(inner, i, functions[i])

    for i in variables:
        setattr(inner, i, variables[i])

    return inner

def check_name(value, file):
    temp_value = []
    should_done = False

    for index, i in enumerate(value):
        if i in string.ascii_letters + string.digits + "_" + "." + ":":
            if not should_done:
                if index == 0:
                    if i in string.digits:
                        error(f"invalid character in '{value}': '{i}'", file)

                temp_value.append(i)

            else:
                error(f"invalid character in '{value}': '{i}'", file)

        elif i == " ":
            should_done = True

        else:
            error(f"invalid character in '{value}': '{i}'", file)

    return "".join(temp_value)

def load_module(name):
    sys.path.append(f"{get_dir()}/include/{name}")
    return importlib.import_module(name)

def error(message, file, type = "error", terminated = False, trace = True):
    print(f"{file}:", end = " ", flush = True)
    set_text_attr(12)
    print(f"{type}:", end = " ", flush = True)
    set_text_attr(7)
    print(message, end = "\n", flush = True)

    if trace:
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(12)
        print("traceback:", end = "\n", flush = True)
        if trace: print("".join(traceback.format_stack()[:-1])[:-1])
        set_text_attr(7)

    if terminated: print("program terminated.")
    sys.exit(-1)

def warning(message, file, type = "warning", terminate = True, trace = True):
    print(f"{file}:", end = " ", flush = True)
    set_text_attr(13)
    print(f"{type}:", end = " ", flush = True)
    set_text_attr(7)
    print(message, end = "\n", flush = True)

    if trace:
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(12)
        print("traceback:", end = "\n", flush = True)
        if trace: print("".join(traceback.format_stack()[:-1])[:-1])
        set_text_attr(7)
    
    if terminate: sys.exit(-1)

def include_library(context, libs, namespace, names, special_namespace):
    for lib in libs:
        if context.is_included(lib) and not context.is_compiled():
            warning("trying to include '" + lib + "' twice", context.file)
            continue

        context.included.append(lib)

        name, ext = os.path.splitext(lib)

        if ext == ".py":
            file_path = None
            
            for j in context.include_folders:
                if os.path.exists(j + "/" + lib):
                    file_path = j + "/" + lib
                    break

            if file_path == None: error("'" + lib + "'" + " " + "was not found", context.file)

            if os.path.split(file_path)[0] not in sys.path:
                sys.path.insert(0, os.path.split(file_path)[0])

            tmp = getattr(importlib.import_module(os.path.split(name)[1]), os.path.split(name)[1])

            if namespace:
                for j in tmp:
                    context.set((lib if special_namespace == None else special_namespace) + "::" + j, tmp[j])
                    context.delete(j)
            
            else:
                for j in tmp:
                    if names != None:
                        if j not in names:
                            found = False

                            for name in names:
                                if j.startswith(name):
                                    found = True
                                    break

                            if not found:
                                context.delete(j)
                                continue
                    
                    context.set(j, tmp[j])

        else:
            file_path = None

            if ext == ".rsxh":
                for j in context.include_folders:
                    if os.path.exists(j + "/" + lib):
                        file_path = j + "/" + lib
                        break

            else:
                for j in context.include_folders:
                    if os.path.exists(j + "/" + lib + "/" + "init.rsxh"):
                        file_path = j + "/" + lib + "/" + "init.rsxh"
                        break

            if file_path == None:
                error("'" + lib + "'" + " " + "was not found", context.file)

            file_content = open(file_path, "r").read()
            ast = None

            if os.path.splitext(os.path.split(file_path)[1])[0] + ".rsxc" in os.listdir(os.path.split(file_path)[0]):
                with open(os.path.splitext(file_path)[0] + ".rsxc", "rb") as file:
                    content = load_bytecode(file.read())

                    if "version" in content:
                        if content["version"] == context.version:
                            if content["file_content"] == hashlib.sha256(file_content.encode()).digest():
                                ast = content["ast"]
                                context.custom_types += content["custom_types"]

            if ast is None:
                ast = core.parser(core.lexer(read_file(file_path), file_path), file_path)

                with open(os.path.splitext(file_path)[0] + ".rsxc", "wb") as file:
                    file.write(dump_bytecode(ast, context.custom_types, file_content))

            context.prepare_to_include(ast, file_path)
            if namespace:
                context.begin_namespace(lib if special_namespace == None else special_namespace)
            tmp_ret = context.current_return_type
            context.current_return_type = None
            tmp_parent_scopes = context.parent_scopes
            context.parent_scopes = []
            core.interpreter(context)
            context.parent_scopes = tmp_parent_scopes
            context.current_return_type = tmp_ret
            if namespace: context.end_namespace()
            context.end_include()

            if not namespace and names != None:
                error("including by name is not implemented", context.file)

def auto_include(file, include_folders):
    context = core.Context(
        ast = core.parser(
            core.lexer(
                read_file(file = file),
                file = file
            ),
            file = file
        ),
        file = file
    )

    context.include_folders = include_folders
    files = []

    for i in context.ast:
        if i["type"] == "include":
            include_library(
                context = context,
                libs = i["libs"],
                namespace = i["namespace"],
                names = i["names"],
                special_namespace = i["special_namespace"]
            )

            files += i["libs"]

    return context

def set_text_attr(color):
    if sys.platform == "win32":
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32. SetConsoleTextAttribute(console_handle, color)

    else:
        if color == 7:
            print("\u001b[0m", end = "", flush = True)

        elif color == 13:
            print("\u001b[31;1m", end = "", flush = True)

        elif color == 12:
            print("\u001b[31m", end = "", flush = True)

        elif color == 14:
            print("\u001b[0m", end = "", flush = True)

        else:
            ...

def create_library(name):
    setattr(__main__, "name", name)
    setattr(__main__, name, {})

def pack_library():
    temp = getattr(__main__, getattr(__main__, "name"))
    delattr(__main__, getattr(__main__, "name"))
    delattr(__main__, "name")
    return temp

def create_function(type, args):
    def inner(func):
        getattr(__main__, getattr(__main__, "name"))[func.__name__] = {"type": "libfunc", "return_type": type, "args": args, "func": func, "const": False}

    return inner

def run_function(name, context):
    context.prepare_to_execute(name)
    temp = core.interpreter(context)
    context.end_execute()
    return rsx_to_py_value(temp)

def get_variable(name, context):
    return rsx_to_py_value(context.get_current_elements()[name]["value"])

def get_variable_type(name, context):
    return context.get_current_elements()[name]["value"]["type"]