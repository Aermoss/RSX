import sys, os, inspect

def begin():
    global f_locals, copy_f_locals
    f_locals = inspect.stack()[1][0].f_locals
    copy_f_locals = f_locals.copy()

def end():
    functions = []
    lib = {}
    
    for i in f_locals:
        if callable(f_locals[i]) and not i in copy_f_locals:
            functions.append(f_locals[i])

    def get_type_str(var_type):
        if var_type == int:
            return "INT"

        elif var_type == float:
            return "FLOAT"

        elif var_type == bool:
            return "BOOL"

        elif var_type == str:
            return "STRING"

        elif var_type == None:
            return "VOID"

        else:
            raise TypeError("unknown type")

    for i in functions:
        args = {}

        if "return" not in i.__annotations__: return_type = "VOID"
        else: return_type = get_type_str(i.__annotations__["return"])

        if i.__code__.co_argcount != len(i.__annotations__) - (1 if "return" in i.__annotations__ else 0):
            raise TypeError("undefined types are not implemented")

        if i.__defaults__ != None:
            raise NotImplementedError("default arguments are not implemented")

        for j in range(i.__code__.co_argcount):
            args[i.__code__.co_varnames[j]] = get_type_str(i.__annotations__[i.__code__.co_varnames[j]])

        code = f"def _{i.__name__}(environ):\n"
        code += f"    return globals()[\"{i.__name__}\"]("

        for index, j in enumerate(args):
            code += f"environ[\"args\"][\"{j}\"]"

            if index != len(args) - 1:
                code += ", "

        code += ")\n"
        exec(code)

        globals()[i.__name__] = i
        globals()[f"_{i.__name__}"] = locals()[f"_{i.__name__}"]
        lib[i.__name__] = {"type": "libfunc", "func_name": f"_{i.__name__}", "code": code, "return_type": return_type, "args": args, "func": globals()[f"_{i.__name__}"], "const": False}

    f_locals[os.path.splitext(os.path.split(f_locals["__file__"])[1])[0]] = lib