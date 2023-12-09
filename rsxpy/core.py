import sys, os, time
import platform, traceback

# from numba import njit, jit
# from numba.core import types
# from numba.typed import Dict

from functools import cache

sys.setrecursionlimit(5000)
sys.dont_write_bytecode = True

import importlib, pickle
import ctypes, ctypes.util
import difflib, hashlib

try:
    import rsxpy.tools as tools
    import rsxpy.std as std
    import rsxpy.builder as builder

except ImportError:
    sys.path.append(os.path.split(os.getcwd())[0])

    import rsxpy.tools as tools
    import rsxpy.std as std
    import rsxpy.builder as builder

keywords = {
    "struct": "STRUCT",
    # "class": "CLASS",
    # "public": "PUBLIC",
    # "private": "PRIVATE",
    # "protected": "PROTECTED",
    # "try": "TRY",
    # "throw": "THROW",
    # "catch": "CATCH",
    # "finally": "FINALLY",
    # "new": "NEW",
    "auto": "AUTO",
    "void": "VOID",
    "bool": "BOOL",
    "int": "INT",
    "float": "FLOAT",
    "string": "STRING",
    "char": "CHAR",
    "double": "DOUBLE",
    "return": "RETURN",
    "false": "FALSE",
    "true": "TRUE",
    "null": "NULL",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "switch": "SWITCH",
    "case": "CASE",
    "default": "DEFAULT",
    "const": "CONST",
    "using": "USING",
    "delete": "DELETE",
    "do": "DO",
    "namespace": "NAMESPACE",
    "break": "BREAK",
    "continue": "CONTINUE",
    "include": "INCLUDE"
}

constant_types = {
    "true": "BOOL",
    "false": "BOOL"
}

symbols = {
    ";": "SEMICOLON",
    ":": "COLON",
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    "{": "LCURLYBRACKET",
    "}": "RCURLYBRACKET",
    ",": "COMMA",
    "=": "EQUALS",
    "-": "MINUS",
    "+": "PLUS",
    "*": "ASTERISK",
    "/": "SLASH",
    "\\": "BACKSLASH",
    ">": "GREATER",
    "<": "LESS",
    "!": "NOT",
    "|": "VERTICALBAR",
    "&": "AMPERSAND",
    "%": "MODULUS",
    "~": "TILDE",
    "^": "CARET",
    ".": "DOT"
}

lines = {}

def lexer(data, file):
    pos = 0
    char = data[pos]
    tokens = []

    lines[file] = data.split("\n")

    cache = [[0, 1, 1]]

    def get_row_col():
        row, col = cache[len(cache) - 1][1], cache[len(cache) - 1][2]
        index = cache[len(cache) - 1][0]

        for i in data[cache[len(cache) - 1][0]:]:
            if index == pos:
                cache.append([pos, row, col])
                return row, col

            index += 1

            if i == "\n":
                col = 1
                row += 1

            else:
                col += 1

    def error(message, file = file, type = "error", terminated = False):
        row, col = get_row_col()
        print(f"{file}:{row}:{col}:", end = " ", flush = True)
        tools.set_text_attr(12)
        print(f"{type}:", end = " ", flush = True)
        tools.set_text_attr(7)
        print(message, end = "\n", flush = True)
        if terminated: print("program terminated.")
        sys.exit(-1)

    def warning(message, file = file, type = "warning"):
        row, col = get_row_col()
        print(f"{file}:{row}:{col}:", end = " ", flush = True)
        tools.set_text_attr(13)
        print(f"{type}:", end = " ", flush = True)
        tools.set_text_attr(7)
        print(message, end = "\n", flush = True)

    def get(index, data = data):
        try: return data[index]
        except: return ""

    def append(value):
        row, col = get_row_col()
        tokens.append({"value": value, "row": row, "col": col - 1})

    last_char = ""

    while len(data) > pos:
        while char.isspace():
            pos += 1
            char = get(pos)

        if char.isalpha() or char in ["_"]:
            id_str = ""

            while char.isalnum() or char in [".", "_"] or (char == ":" and (get(pos + 1) == ":" or get(pos - 1) == ":") and get(pos + 2) != ":"):
                if char == ":" and id_str == "default": break
                id_str += char
                pos += 1
                char = get(pos)

            if id_str in keywords:
                if id_str in constant_types:
                    append(constant_types[id_str])

                append(keywords[id_str])

            else:
                append("IDENTIFIER")
                append(id_str)

        elif char.isdigit() or char == "." and get(pos + 1) != ".":
            num_str = ""
            last_char = get(pos - 1)
            base = "decimal"

            if char == ".":
                num_str += "0"

            elif char == "0":
                if get(pos + 1) in ["x", "b", "o"]:
                    base = get(pos + 1).replace("x", "hexadecimal").replace("b", "binary").replace("o", "octal")
                    pos += 2
                    char = get(pos)

            while char.isdigit() or (base == "decimal" and char in [".", "f"]) or (base == "hexadecimal" and char in ["A", "B", "C", "D", "E", "F"]):
                num_str += char
                pos += 1
                char = get(pos)

            if base == "decimal":
                if num_str.count(".") == 1:
                    if num_str[-1:] == ".": num_str += "0"
                    if num_str.count("f") == 0: append("DOUBLE")
                    elif num_str.count("f") == 1: append("FLOAT")
                    else: error("more than one 'f' found in a float")
                    num_str = num_str.replace("f", "")

                elif num_str.count(".") == 0:
                    append("INT")

                    if num_str.count("f") != 0:
                        error("used 'f' in an integer value")

                else:
                    error("more than one '.' found in a value")

                append(num_str)
            
            elif base in ["hexadecimal", "binary", "octal"]:
                base_int = int(base.replace("hexadecimal", "16").replace("binary", "2").replace("octal", "8"))
                append("INT")
                append(str(int(num_str, base_int)))

            else:
                error("unknown number system")

        elif char == "\'":
            if get(pos + 2) == char:
                append("CHAR")
                append(get(pos + 1))
                pos += 3
                char = get(pos)

            else:
                error("invalid syntax for char")

        elif char == "\"":
            pos += 1
            char = get(pos)
            string = ""

            while char and char != "\"":
                if char in "\r\n":
                    error("unterminated string literal")

                if char == "\\" and get(pos + 1) == "\"":
                    string += "\""
                    pos += 2
                    char = get(pos)

                elif char == "\\" and get(pos + 1) == "\'":
                    string += "\'"
                    pos += 2
                    char = get(pos)
                
                elif char == "\\" and get(pos + 1) == "0":
                    string += "\0"
                    pos += 2
                    char = get(pos)

                elif char == "\\" and get(pos + 1) == "\\":
                    string += "\\"
                    pos += 2
                    char = get(pos)

                elif char == "\\" and get(pos + 1) == "r":
                    string += "\r"
                    pos += 2
                    char = get(pos)

                elif char == "\\" and get(pos + 1) == "n":
                    string += "\n"
                    pos += 2
                    char = get(pos)

                elif char == "\\" and get(pos + 1) == "t":
                    string += "\t"
                    pos += 2
                    char = get(pos)

                else:
                    string += char
                    pos += 1
                    char = get(pos)

            append("STRING")
            append(string.replace("mavish", "♥ mavish ♥"))
            pos += 1
            char = get(pos)

        elif char:
            if char == "/":
                if get(pos + 1) == "/":
                    while char and char not in "\r\n":
                        pos += 1
                        char = get(pos)

                    pos += 1
                    char = get(pos)

                elif get(pos + 1) == "*":
                    while char:
                        pos += 1
                        char = get(pos)

                        if char == "*" and get(pos + 1) == "/":
                            pos += 1
                            break
                
                    pos += 1
                    char = get(pos)

                else:
                    append(symbols[char])
                    pos += 1
                    char = get(pos)

            elif char in symbols:
                if tokens[len(tokens) - 1]["value"] in ["GREATER", "LESS", "NOT", "EQUALS", "PLUS", "MINUS", "ASTERISK", "SLASH", "MODULUS"] and char == "=" and last_char != " ":
                    append(tokens[len(tokens) - 1]["value"] + symbols[char])
                    tokens.pop(len(tokens) - 2)

                elif tokens[len(tokens) - 1]["value"] == "MINUS" and char == ">" and last_char != " ":
                    append("ARROW")
                    tokens.pop(len(tokens) - 2)

                elif tokens[len(tokens) - 1]["value"] in ["GREATER", "LESS"] and char in [">", "<"]:
                    if char == "<": append("BITWISELEFT")
                    elif char == ">": append("BITWISERIGHT")
                    tokens.pop(len(tokens) - 2)

                elif char == "|" and get(pos + 1) == "|":
                    append("OR")
                    pos += 1

                elif char == "|":
                    append("BITWISEOR")

                elif char == "&" and get(pos + 1) == "&":
                    append("AND")
                    pos += 1
                
                elif char == "&" and get(pos + 1) != " ":
                    append("ADDROF")

                elif char == "&":
                    append("BITWISEAND")

                elif char == "~":
                    append("BITWISENOT")

                elif char == "^":
                    append("BITWISEXOR")

                elif char == "." and get(pos + 1) == "." and get(pos + 2) == "." and get(pos + 3) != ".":
                    append("THREEDOT")
                    pos += 2

                elif char in ["-", "+"] and get(pos + 1) in ["-", "+"] and char == get(pos + 1) and tokens[len(tokens) - 2]["value"] == "IDENTIFIER":
                    append(char.replace("+", "POSTINCREMENT").replace("-", "POSTDECREMENT"))
                    pos += 1

                elif char in ["-", "+"] and get(pos + 1) in ["-", "+"] and char == get(pos + 1):
                    append(char.replace("+", "PREINCREMENT").replace("-", "PREDECREMENT"))
                    pos += 1

                elif char in ["-", "+"] and (get(pos + 1) not in [" ", char, "\"", "\'", "\n"] + list(symbols.keys())):
                    append(char.replace("-", "NEGATIVE").replace("+", "POSITIVE"))

                else:
                    append(symbols[char])

                pos += 1
                char = get(pos)

                if char in "\r\n":
                    pos += 1
                    char = get(pos)

            else:
                error(f"unknown operator '{char}'")

            last_char = char
    
    return tokens

def parser(tokens, file, custom_types = []):
    ast = []
    pos = 0

    last_token = {"token": None, "pos": None, "value": None}

    types = ["BOOL", "INT", "FLOAT", "STRING", "CHAR", "DOUBLE"]
    operators = ["PLUS", "MINUS", "SLASH", "ASTERISK", "MODULUS", "EQUALS" * 2, "NOT" + "EQUALS", "GREATER", "GREATER" + "EQUALS", "LESS", "LESS" + "EQUALS", "AND", "OR", "NOT", "BITWISEOR", "BITWISEXOR", "BITWISEAND", "BITWISENOT", "BITWISELEFT", "BITWISERIGHT"]
    assignment_operators = ["EQUALS", "PLUS" + "EQUALS", "MINUS" + "EQUALS", "ASTERISK" + "EQUALS", "SLASH" + "EQUALS", "MODULUS" + "EQUALS", "BITWISEOR" + "EQUALS", "BITWISEXOR" + "EQUALS", "BITWISEAND" + "EQUALS", "BITWISELEFT" + "EQUALS", "BITWISERIGHT" + "EQUALS"]

    def error(message = None, file = file, type = "error", terminated = False):
        row, col = None, None

        print(len(tokens), pos)

        if isinstance(tokens[pos], str):
            print(f"{file}:<{tokens[pos]}>:", end = " ", flush = True)

        else:
            row, col = tokens[pos]["row"], tokens[pos]["col"]
            print(f"{file}:{row}:{col}:", end = " ", flush = True)

        tools.set_text_attr(12)
        print(f"{type}:", end = " ", flush = True)
        tools.set_text_attr(7)
        should_pass = False

        if get(pos) == "IDENTIFIER" and message == None:
            if get(pos + 1) not in keywords:
                should_pass = True
                close_matches = difflib.get_close_matches(get(pos + 1), keywords)

                print(f"invalid identifier: '{get(pos + 1)}'", end = "\n", flush = True)
                
                if row != None and col != None:
                    print(lines[file][row - 1][:col - 1], end = "", flush = True)
                    tools.set_text_attr(12)
                    print(lines[file][row - 1][col - 1:col - 1 + len(get(pos + 1))], end = "", flush = True)
                    tools.set_text_attr(7)
                    print(lines[file][row - 1][col - 1 + len(get(pos + 1)):], end = "\n", flush = True)
                    tools.set_text_attr(12)
                    print(" " * (col - 1) + "^" + (len(get(pos + 1)) - 1) * "~", end = "\n", flush = True)
                    tools.set_text_attr(7)

                if len(close_matches) > 0:
                    print("did you mean", end = " ", flush = True)
                    tools.set_text_attr(10)
                    print(close_matches[len(close_matches) - 1], end = "", flush = True)
                    tools.set_text_attr(7)
                    print("?", end = "\n", flush = True)
            
        if not should_pass:
            if message == None:
                message = "failed to generate the ast"

            print(message, end = "\n", flush = True)

        if terminated: print("program terminated.")
        sys.exit(-1)

    def warning(message, file = file, type = "warning"):
        row, col = tokens[pos]["row"], tokens[pos]["col"]
        print(f"{file}:{row}:{col}:", end = " ", flush = True)
        tools.set_text_attr(13)
        print(f"{type}:", end = " ", flush = True)
        tools.set_text_attr(7)
        print(message, end = "\n", flush = True)

    def get(index, pure = False):
        try:
            if pure:
                return tokens[index]
                
            else:
                value = tokens[index]

                if isinstance(value, str):
                    return value

                else:
                    return value["value"]
                
        except IndexError: error()

    def get_call_args(current_pos):
        temp_tokens = []
        args = []
        ignore, ignore_curly = 0, 0
        current_pos += 1

        while True:
            if get(current_pos) == "LPAREN":
                temp_tokens.append(get(current_pos, True))
                current_pos += 1
                ignore += 1

            elif get(current_pos) == "LCURLYBRACKET":
                temp_tokens.append(get(current_pos, True))
                ignore_curly += 1
                current_pos += 1

            elif get(current_pos) == "RPAREN":
                if ignore_curly == 0 and ignore == 0:
                    if len(temp_tokens) != 0:
                        temp_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
                        args.append(parser(temp_tokens, file, custom_types)[0])
                        temp_tokens.clear()

                    break

                temp_tokens.append(get(current_pos, True))
                current_pos += 1
                ignore -= 1

            elif get(current_pos) == "RCURLYBRACKET":
                temp_tokens.append(get(current_pos, True))
                ignore_curly -= 1
                current_pos += 1

            elif get(current_pos) == "COMMA":
                if ignore_curly == 0 and ignore == 0:
                    if len(temp_tokens) != 0:
                        temp_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
                        args.append(parser(temp_tokens, file)[0])
                        temp_tokens.clear()

                else:
                    temp_tokens.append(get(current_pos, True))
                
                current_pos += 1
            
            else:
                temp_tokens.append(get(current_pos, True))
                current_pos += 1

        return args, current_pos + 1

    def get_def_args(current_pos):
        args, arg_type, arg_name, arg_array_type, arg_size = {}, None, None, None, None
        var_arg = False
        ignore = 0

        while True:
            if get(current_pos) == "LPAREN":
                ignore += 1
                current_pos += 1

            elif get(current_pos) == "RPAREN":
                ignore -= 1

                if ignore == 0:
                    if arg_name != None and arg_type != None:
                        if arg_type == "ARRAY_T":
                            args[arg_name] = {"type": arg_type, "array_type": arg_array_type, "size": arg_size}
                            arg_array_type, arg_size = None, None
                            
                        else:
                            args[arg_name] = arg_type

                        arg_type, arg_name = None, None

                    break

                current_pos += 1

            elif get(current_pos) in types:
                arg_type = get(current_pos)
                arg_array_type = None
                arg_size = None

                if get(current_pos + 1) == "LBRACKET":
                    temp_size, current_pos = get_index(current_pos + 2)
                    if temp_size["type"] != "NULL": arg_size = temp_size
                    arg_array_type = arg_type
                    arg_type = "ARRAY_T"

                else:
                    current_pos += 1

            elif get(current_pos) == "IDENTIFIER":
                if get(current_pos + 1) in custom_types:
                    arg_type = {"type": "STRUCT_T", "value": get(current_pos + 1)}
                    arg_array_type = None
                    arg_size = None
                
                else:
                    arg_name = get(current_pos + 1)

                current_pos += 2

            elif get(current_pos) == "THREEDOT":
                var_arg = True
                current_pos += 1

            elif get(current_pos) == "COMMA":
                if arg_name != None and arg_type != None:
                    if arg_type == "ARRAY_T":
                        args[arg_name] = {"type": arg_type, "array_type": arg_array_type, "size": arg_size}
                        arg_array_type, arg_size = None, None
                        
                    else:
                        args[arg_name] = arg_type

                    arg_type, arg_name = None, None

                current_pos += 1
        
        return args, current_pos + 1, var_arg

    def get_func_ast(current_pos):
        temp_tokens = []
        ignore = 0

        if get(current_pos) != "LCURLYBRACKET":
            while True:
                if get(current_pos) == "SEMICOLON":
                    temp_tokens.append(get(current_pos, True))
                    break

                else:
                    temp_tokens.append(get(current_pos, True))
                    current_pos += 1

        else:
            while True:
                if get(current_pos) == "LCURLYBRACKET":
                    if ignore != 0:
                        temp_tokens.append(get(current_pos, True))

                    ignore += 1
                    current_pos += 1

                elif get(current_pos) == "RCURLYBRACKET":
                    ignore -= 1

                    if ignore == 0:
                        break

                    temp_tokens.append(get(current_pos, True))
                    current_pos += 1

                else:
                    temp_tokens.append(get(current_pos, True))
                    current_pos += 1

        return parser(temp_tokens, file, custom_types), current_pos + 1

    def get_index(temp_pos):
        temp_tokens = []
        ignore = 0

        while True:
            if get(temp_pos) == "LBRACKET":
                temp_tokens.append(get(temp_pos, True))
                ignore += 1
                temp_pos += 1

            elif get(temp_pos) == "RBRACKET":
                if ignore == 0: break
                temp_tokens.append(get(temp_pos, True))
                ignore -= 1
                temp_pos += 1

            else:
                temp_tokens.append(get(temp_pos, True))
                temp_pos += 1

        temp_tokens.append("SEMICOLON")

        if get(temp_pos) == "RBRACKET":
            index = parser(temp_tokens, file, custom_types)[0]
            temp_pos += 1

        return index, temp_pos

    def collect_tokens(temp_pos, stop_tokens = ["SEMICOLON"] + operators):
        temp_tokens = []
        ignore = 0
        ignore_curly = 0
        ignore_bracket = 0

        while True:
            if get(temp_pos) in stop_tokens:
                if ignore == 0 and ignore_curly == 0 and ignore_bracket == 0: break
                if get(temp_pos) == "RPAREN": ignore -= 1
                if get(temp_pos) == "LPAREN": ignore += 1
                if get(temp_pos) == "RBRACKET": ignore_bracket -= 1
                if get(temp_pos) == "LBRACKET": ignore_bracket += 1
                if get(temp_pos) == "RCURLYBRACKET": ignore_curly -= 1
                if get(temp_pos) == "LCURLYBRACKET": ignore_curly += 1

                temp_tokens.append(get(temp_pos, True))
                temp_pos += 1

            elif get(temp_pos) == "COMMA":
                if ignore == 0 and ignore_curly == 0 and ignore_bracket == 0: break
                temp_tokens.append(get(temp_pos, True))
                temp_pos += 1

            elif get(temp_pos) == "LPAREN":
                temp_tokens.append(get(temp_pos, True))
                ignore += 1
                temp_pos += 1

            elif get(temp_pos) == "RPAREN":
                temp_tokens.append(get(temp_pos, True))
                ignore -= 1
                temp_pos += 1

            elif get(temp_pos) == "LBRACKET":
                temp_tokens.append(get(temp_pos, True))
                ignore_bracket += 1
                temp_pos += 1

            elif get(temp_pos) == "RBRACKET":
                temp_tokens.append(get(temp_pos, True))
                ignore_bracket -= 1
                temp_pos += 1

            elif get(temp_pos) == "LCURLYBRACKET":
                temp_tokens.append(get(temp_pos, True))
                ignore_curly += 1
                temp_pos += 1

            elif get(temp_pos) == "RCURLYBRACKET":
                temp_tokens.append(get(temp_pos, True))
                ignore_curly -= 1
                temp_pos += 1

            else:
                temp_tokens.append(get(temp_pos, True))
                temp_pos += 1

        temp_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
        return temp_tokens, temp_pos

    def factor(temp_pos, result = None):
        if result != None: return result, temp_pos
        temp_tokens, temp_pos = collect_tokens(temp_pos)
        result = parser(temp_tokens, file, custom_types)[0]
        return result, temp_pos

    def term(temp_pos, result = None):
        result, temp_pos = factor(temp_pos, result)

        while get(temp_pos) in ["ASTERISK", "SLASH", "MODULUS"]:
            type = get(temp_pos)
            temp_pos += 1
            right, temp_pos = factor(temp_pos)
            result = {"type": type.replace("ASTERISK", "mul").replace("SLASH", "div").replace("MODULUS", "mod"), "left": result, "right": right}

        return result, temp_pos

    def expr(temp_pos, result = None):
        result, temp_pos = term(temp_pos, result)

        while get(temp_pos) in ["PLUS", "MINUS", "BITWISEOR", "BITWISEXOR", "BITWISEAND", "BITWISELEFT", "BITWISERIGHT"]:
            type = get(temp_pos)
            temp_pos += 1
            right, temp_pos = term(temp_pos)
            result = {"type": type.replace("PLUS", "add").replace("MINUS", "sub").replace("BITWISE", "BITWISE ").lower(), "left": result, "right": right}

        return result, temp_pos

    while len(tokens) > pos:
        if last_token["token"] == None or get(pos) != last_token["token"] or last_token["pos"] != pos:
            last_token = {"token": get(pos), "pos": pos, "value": 0}

        elif get(pos) == last_token["token"]: last_token["value"] += 1
        if last_token["value"] >= 1000: error()

        if get(pos) == "NAMESPACE":
            if get(pos + 1) == "IDENTIFIER":
                if get(pos + 3) == "LCURLYBRACKET":
                    name = get(pos + 2)
                    temp_ast, pos = get_func_ast(pos + 3)

                    if "." in name:
                        error("invalid character", suggest = False)

                    ast.append({"type": "namespace", "name": name, "ast": temp_ast})

        elif get(pos) == "STRUCT":
            if get(pos + 1) == "IDENTIFIER":
                name = get(pos + 2)
                custom_types.append(name)
                tmp_ast, pos = get_func_ast(pos + 3)
                
                for i in tmp_ast:
                    if i["type"] not in ["var", "func", "constructor", "destructor"]:
                        print(i)
                        tools.error("invalid usage of struct: '" + name + "'", file)

                if get(pos) == "SEMICOLON":
                    ast.append({"type": "struct", "name": name, "ast": tmp_ast})
                    pos += 1

                else:
                    tools.error(f"expected ';' At the end of the definition of the '{name}' structure", file)

        elif get(pos) == "NOT":
            temp_tokens, pos = collect_tokens(pos + 1)
            ast.append({"type": "not", "value": parser(temp_tokens, file, custom_types)[0]})
            if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) == "ADDROF":
            temp_tokens, pos = collect_tokens(pos + 1)
            ast.append({"type": "addrof", "value": parser(temp_tokens, file, custom_types)[0]})
            if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) in ["NEGATIVE", "POSITIVE"]:
            type = get(pos)
            temp_tokens, pos = collect_tokens(pos + 1)
            ast.append({"type": type.replace("NEGATIVE", "neg").replace("POSITIVE", "pos"), "value": parser(temp_tokens, file, custom_types)[0]})
            if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) in ["PREINCREMENT", "PREDECREMENT"]:
            type = get(pos)
            temp_tokens, pos = collect_tokens(pos + 1)
            ast.append({"type": type.replace("PREINCREMENT", "increment").replace("PREDECREMENT", "decrement"), "value": parser(temp_tokens, file, custom_types)[0], "pre": True})
            if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) == "BITWISENOT":
            if get(pos + 1) == "IDENTIFIER" and get(pos + 2).split("::")[len(get(pos + 2).split("::")) - 1] in custom_types:
                tokens[pos + 2] = "~" + get(pos + 2)
                pos += 1

            else:
                temp_tokens, pos = collect_tokens(pos + 1)
                ast.append({"type": "bitwise not", "value": parser(temp_tokens, file, custom_types)[0]})
                if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) == "FOR":
            if get(pos + 1) == "LPAREN":
                temp_pos = pos + 1
                temp_pass = 0
                temp_part = 0
                temp_tokens = {0: [], 1: [], 2: []}

                while True:
                    if get(temp_pos) == "LPAREN":
                        if temp_pass != 0:
                            temp_tokens[temp_part].append(get(temp_pos))

                        temp_pass += 1
                        temp_pos += 1

                    elif get(temp_pos) == "RPAREN":
                        temp_pass -= 1

                        if temp_pass == 0:
                            if len(temp_tokens[temp_part]) != 0:
                                temp_tokens[temp_part].append("SEMICOLON")

                            break

                        temp_tokens[temp_part].append(get(temp_pos))
                        temp_pos += 1

                    elif get(temp_pos) == "SEMICOLON":
                        if temp_part != 1:
                            if len(temp_tokens[temp_part]) != 0:
                                temp_tokens[temp_part].append(get(temp_pos))

                        temp_part += 1
                        temp_pos += 1

                    else:
                        temp_tokens[temp_part].append(get(temp_pos))
                        temp_pos += 1

                temp_ast, pos = get_func_ast(temp_pos + 1)
                temp_tokens[1].append({"value": "SEMICOLON", "row": 0, "col": 0})
                ast.append({"type": "for", "ast": temp_ast, "init": parser(temp_tokens[0], file, custom_types), "condition": parser(temp_tokens[1], file, custom_types)[0], "update": parser(temp_tokens[2], file, custom_types)})

        elif get(pos) in ["IF", "ELSE", "WHILE"]:
            first_pos = pos

            if get(pos) == "ELSE":
                if get(pos + 1) == "IF":
                    pos += 1

                elif get(pos + 1) == "LPAREN":
                    error("expected '{' but found '('")

            if get(pos + 1) == "LPAREN":
                condition_pos = pos + 1
                condition_pass = 0
                condition_tokens = []

                while True:
                    if get(condition_pos) == "LPAREN":
                        if condition_pass != 0:
                            condition_tokens.append(get(condition_pos))

                        condition_pass += 1
                        condition_pos += 1

                    elif get(condition_pos) == "RPAREN":
                        condition_pass -= 1

                        if condition_pass == 0:
                            if condition_tokens[len(condition_tokens) - 1] in ["AND", "OR"]:
                                error(f"expected a value after: '{condition_tokens[len(condition_tokens) - 1].lower()}'")

                            break

                        condition_tokens.append(get(condition_pos))
                        condition_pos += 1

                    else:
                        condition_tokens.append(get(condition_pos))
                        condition_pos += 1

                pos = condition_pos

            temp_ast, pos = get_func_ast(pos + 1)

            if get(first_pos) == "ELSE":
                if get(first_pos + 1) == "IF": 
                    name = get(first_pos).lower() + " " + get(first_pos + 1).lower()
                else: name = get(first_pos).lower()
            else: name = get(first_pos).lower()

            if (get(first_pos) in ["IF", "WHILE"]) or (get(first_pos) == "ELSE" and get(first_pos + 1) == "IF"):
                condition_tokens.append("SEMICOLON")
                ast.append({"type": name, "ast": temp_ast, "condition": parser(condition_tokens, file, custom_types)[0]})

            else:
                ast.append({"type": name, "ast": temp_ast})

        elif get(pos) == "USING":
            if get(pos + 1) == "NAMESPACE":
                if get(pos + 2) == "IDENTIFIER":
                    if get(pos + 4) == "SEMICOLON":
                        ast.append({"type": "using namespace", "name": get(pos + 3)})
                        pos += 5

        elif get(pos) == "OR":
            left = ast[len(ast) - 1]
            ast.pop(len(ast) - 1)
            temp_tokens, pos = collect_tokens(pos + 1, stop_tokens = ["OR", "AND", "SEMICOLON", "RPAREN"])
            ast.append({"type": "or", "left": left, "right": parser(temp_tokens, file, custom_types)[0]})
            if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) == "AND":
            left = ast[len(ast) - 1]
            ast.pop(len(ast) - 1)
            temp_tokens, pos = collect_tokens(pos + 1, stop_tokens = ["OR", "AND", "SEMICOLON", "RPAREN"])
            ast.append({"type": "and", "left": left, "right": parser(temp_tokens, file, custom_types)[0]})
            if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) == "DO":
            first_pos = pos
            temp_ast, pos = get_func_ast(pos + 1)

            if get(pos) == "WHILE":
                condition_pos = pos + 1
                condition_pass = 0
                condition_tokens = []

                while True:
                    if get(condition_pos) == "LPAREN":
                        if condition_pass != 0:
                            condition_tokens.append(get(condition_pos, True))

                        condition_pass += 1
                        condition_pos += 1

                    elif get(condition_pos) == "RPAREN":
                        condition_pass -= 1

                        if condition_pass == 0:
                            if condition_tokens[len(condition_tokens) - 1] in ["AND", "OR"]:
                                error(f"expected a value after: '{condition_tokens[len(condition_tokens) - 1].lower()}'")

                            break

                        condition_tokens.append(get(condition_pos, True))
                        condition_pos += 1

                    else:
                        condition_tokens.append(get(condition_pos, True))
                        condition_pos += 1

                pos = condition_pos + 1
                condition_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
                ast.append({"type": "do while", "ast": temp_ast, "condition": parser(condition_tokens, file, custom_types)[0]})

                if get(pos) == "SEMICOLON":
                    pos += 1

            else:
                ast.append({"type": "do", "ast": temp_ast})

        elif get(pos) == "LCURLYBRACKET":
            temp_pos = pos + 1
            ignore = 0
            ignore_curly = 0
            array = True

            while True:
                if get(temp_pos) in ["SEMICOLON", "RPAREN", "LPAREN", "RCURLYBRACKET", "LCURLYBRACKET"]:
                    if ignore == 0 and ignore_curly == 0:
                        if get(temp_pos) == "SEMICOLON":
                            array = False
                            break

                    if get(temp_pos) == "RPAREN": ignore -= 1
                    if get(temp_pos) == "LPAREN": ignore += 1
                    if get(temp_pos) == "RCURLYBRACKET": ignore_curly -= 1
                    if get(temp_pos) == "LCURLYBRACKET": ignore_curly += 1

                elif get(temp_pos) == "COMMA":
                    if ignore == 0 and ignore_curly == 0:
                        array = True
                        break

                temp_pos += 1

            if array:
                pos += 1
                values = []

                while True:
                    temp_tokens, pos = collect_tokens(pos, stop_tokens = ["RCURLYBRACKET", "SEMICOLON"])
                    if len(temp_tokens) != 1: values.append(parser(temp_tokens, file, custom_types)[0])

                    if get(pos) == "COMMA":
                        pos += 1

                    else:
                        break

                if get(pos) == "RCURLYBRACKET":
                    pos += 1

                    if get(pos) == "SEMICOLON":
                        pos += 1

                ast.append({"type": "INITLIST", "value": values})

            else:
                temp_ast, pos = get_func_ast(pos)
                ast.append({"type": "do", "ast": temp_ast})

        elif get(pos) == "SWITCH":
            if get(pos + 1) == "LPAREN":
                temp_tokens = []
                ignore = 1
                pos += 2

                while True:
                    if get(pos) == "RPAREN":
                        ignore -= 1
                        if ignore == 0: break
                        temp_tokens.append(get(pos, True))
                        pos += 1

                    elif get(pos) == "LPAREN":
                        temp_tokens.append(get(pos, True))
                        ignore += 1
                        pos += 1

                    else:
                        temp_tokens.append(get(pos, True))
                        pos += 1

                temp_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
                value = parser(temp_tokens, file)[0]
                temp_tokens.clear()

                if get(pos + 1) != "LCURLYBRACKET":
                    error("expected '{'")

                pos += 2
                ignore = 1
                current_case = None
                cases = {}

                while True:
                    if get(pos) == "RCURLYBRACKET":
                        ignore -= 1
                        if ignore == 0: break
                        if current_case == None: error("couldn't find any case")
                        cases[current_case]["ast"].append(get(pos, True))
                        pos += 1

                    elif get(pos) == "LCURLYBRACKET":
                        if current_case == None: error("couldn't find any case")
                        cases[current_case]["ast"].append(get(pos, True))
                        ignore += 1
                        pos += 1

                    elif get(pos) in ["CASE", "DEFAULT"]:
                        if current_case != None: cases[current_case]["ast"] = parser(cases[current_case]["ast"], file, custom_types)
                        current_case = len(cases)
                        if get(pos) == "DEFAULT": current_case = "default"
                        cases[current_case] = {"ast": [], "value": []}
                        pos += 1

                        while current_case != "default":
                            if get(pos) == "COLON":
                                break

                            else:
                                cases[current_case]["value"].append(get(pos))
                                pos += 1

                        else:
                            del cases[current_case]["value"]

                            if get(pos) == "COLON":
                                pos += 1

                            else:
                                error("expected ':'")

                        if "value" in cases[current_case]:
                            cases[current_case]["value"].append({"value": "SEMICOLON", "row": 0, "col": 0})
                            cases[current_case]["value"] = parser(cases[current_case]["value"], file, custom_types)[0]
                            pos += 1

                    else:
                        if current_case == None: error("couldn't find any case")
                        cases[current_case]["ast"].append(get(pos, True))
                        pos += 1

                if current_case != None: cases[current_case]["ast"] = parser(cases[current_case]["ast"], file, custom_types)

                if get(pos) == "RCURLYBRACKET":
                    ast.append({"type": "switch", "value": value, "cases": cases})
                    pos += 1

        elif get(pos) == "LPAREN" and get(pos + 1) in types and get(pos + 2) == "RPAREN":
            temp_tokens = []
            type = get(pos + 1)
            pos += 3
            ignore = 0
            ignore_curly = 0

            while True:
                if get(pos) in ["SEMICOLON"] + operators:
                    if get(pos) in ["PLUS", "MINUS"]:
                        if get(pos) != get(pos + 1):
                            if ignore == 0 and ignore_curly == 0: break

                        else:
                            temp_tokens.append(get(pos, True))
                            pos += 1

                    else:
                        if ignore == 0 and ignore_curly == 0: break

                    temp_tokens.append(get(pos, True))
                    pos += 1

                elif get(pos) == "LPAREN":
                    temp_tokens.append(get(pos, True))
                    pos += 1
                    ignore += 1

                elif get(pos) == "RPAREN":
                    temp_tokens.append(get(pos, True))
                    pos += 1
                    ignore -= 1

                elif get(pos) == "LCURLYBRACKET":
                    temp_tokens.append(get(pos, True))
                    pos += 1
                    ignore_curly += 1

                elif get(pos) == "RCURLYBRACKET":
                    temp_tokens.append(get(pos, True))
                    pos += 1
                    ignore_curly -= 1

                else:
                    temp_tokens.append(get(pos, True))
                    pos += 1

            temp_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
            ast.append({"type": "cast", "cast_type": type, "value": parser(temp_tokens, file, custom_types)[0]})

        elif get(pos) in ["PLUS", "MINUS", "SLASH", "ASTERISK", "MODULUS", "BITWISEOR", "BITWISEXOR", "BITWISEAND", "BITWISELEFT", "BITWISERIGHT"]:
            result, pos = expr(pos, ast[len(ast) - 1])
            ast.append(result)
            ast.pop(len(ast) - 2)

            if get(pos) == "SEMICOLON":
                pos += 1

        elif get(pos) in ["EQUALS" * 2, "NOT" + "EQUALS", "GREATER", "GREATER" + "EQUALS", "LESS", "LESS" + "EQUALS"]:
            temp_tokens = []
            type = get(pos).lower()
            pos += 1

            while True:
                if get(pos) in ["SEMICOLON", "EQUALS" * 2, "NOT" + "EQUALS", "GREATER", "GREATER" + "EQUALS", "LESS", "LESS" + "EQUALS", "OR", "AND", "NOT"]:
                    break

                else:
                    temp_tokens.append(get(pos, True))
                    pos += 1

            temp_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
            ast.append({"type": type, "left": ast[len(ast) - 1], "right": parser(temp_tokens, file, custom_types)[0]})
            ast.pop(len(ast) - 2)

            if get(pos) == "SEMICOLON":
                pos += 1

        elif get(pos) == "RETURN":
            temp_tokens = []
            type = get(pos + 1)
            pos += 1

            while True:
                if get(pos) == "SEMICOLON":
                    temp_tokens.append(get(pos, True))
                    break

                else:
                    temp_tokens.append(get(pos, True))
                    pos += 1

            if get(pos) == "SEMICOLON":
                ast.append({"type": "return", "value": parser(temp_tokens, file, custom_types)[0]})
                pos += 1

        elif get(pos) == "DELETE":
            if get(pos + 3) == "SEMICOLON":
                if get(pos + 1) == "IDENTIFIER":
                    ast.append({"type": get(pos).lower(), "value": get(pos + 2)})
                    pos += 4

        elif get(pos) == "INCLUDE":
            libs = []
            pos += 1

            while get(pos) == "STRING":
                libs.append(get(pos + 1))
                pos += 2

                if get(pos) == "COMMA":
                    pos += 1

            if get(pos) == "SEMICOLON":
                ast.append({"type": "include", "namespace": True, "libs": libs, "names": None, "special_namespace": None})
                pos += 1

            elif get(pos) == "COLON":
                if get(pos + 1) == "ASTERISK":
                    if get(pos + 2) == "SEMICOLON":
                        ast.append({"type": "include", "namespace": False, "libs": libs, "names": None, "special_namespace": None})
                        pos += 3

                else:
                    names = []
                    pos += 1

                    while get(pos) == "STRING":
                        names.append(get(pos + 1))
                        pos += 2

                        if get(pos) == "COMMA":
                            pos += 1

                    if get(pos) == "SEMICOLON":
                        ast.append({"type": "include", "namespace": False, "libs": libs, "names": names, "special_namespace": None})
                        pos += 1

            elif get(pos) == "ARROW":
                if get(pos + 1) == "STRING":
                    if get(pos + 3) == "SEMICOLON":
                        ast.append({"type": "include", "namespace": True, "libs": libs, "names": None, "special_namespace": get(pos + 2)})
                        pos += 4

        elif get(pos) in ["BREAK", "CONTINUE"]:
            if get(pos + 1) == "SEMICOLON":
                ast.append({"type": get(pos).lower()})
                pos += 2

        elif get(pos) == "IDENTIFIER" and get(pos + 1).split("::")[len(get(pos + 1).split()) - 1].replace("~", "") not in custom_types:
            if get(pos + 2) in assignment_operators:
                type = get(pos + 2)
                name = get(pos + 1)
                temp_tokens, pos = collect_tokens(pos + 3, stop_tokens = ["SEMICOLON"])
                value = parser(temp_tokens, file, custom_types)[0]
                cur = {"type": "IDENTIFIER", "value": name}

                if type == "PLUS" + "EQUALS": value = {"type": "add", "left": cur, "right": value}
                if type == "MINUS" + "EQUALS": value = {"type": "sub", "left": cur, "right": value}
                if type == "ASTERISK" + "EQUALS": value = {"type": "mul", "left": cur, "right": value}
                if type == "SLASH" + "EQUALS": value = {"type": "div", "left": cur, "right": value}
                if type == "BITWISEOR" + "EQUALS": value = {"type": "bitwise or", "left": cur, "right": value}
                if type == "BITWISEXOR" + "EQUALS": value = {"type": "bitwise xor", "left": cur, "right": value}
                if type == "BITWISEAND" + "EQUALS": value = {"type": "bitwise and", "left": cur, "right": value}
                if type == "BITWISELEFT" + "EQUALS": value = {"type": "bitwise left", "left": cur, "right": value}
                if type == "BITWISRIGHT" + "EQUALS": value = {"type": "bitwise right", "left": cur, "right": value}

                ast.append({"type": "var", "value_type": None, "name": name, "value": value, "const": False})

                if get(pos) in ["COMMA", "SEMICOLON"]:
                    if get(pos) == "COMMA":
                        if get(pos + 1) == "IDENTIFIER":
                            if get(pos + 3) in assignment_operators:
                                pos += 1

                            else:
                                error("expected assignment operator after identifier")
                        
                        else:
                            error("expected identifier after ','")

                    else:
                        pos += 1

            elif get(pos + 2) in ["POSTINCREMENT", "POSTDECREMENT"]:
                ast.append({"type": get(pos + 2).replace("POSTINCREMENT", "increment").replace("POSTDECREMENT", "decrement"), "value": {"type": "IDENTIFIER", "value": get(pos + 1)}, "pre": False})
                pos += 3
                if get(pos) == "SEMICOLON": pos += 1

            else:
                ast.append({"type": "IDENTIFIER", "value": get(pos + 1)})
                pos += 2

        elif get(pos) == "LBRACKET":
            index, pos = get_index(pos + 1)

            if get(pos) in assignment_operators:
                type = get(pos)
                temp_tokens, pos = collect_tokens(pos + 1, stop_tokens = ["SEMICOLON"])
                value = parser(temp_tokens, file, custom_types)[0]
                last = {"type": "get", "target": ast[len(ast) - 1], "index": index}

                if type == "PLUS" + "EQUALS": value = {"type": "add", "left": last, "right": value}
                if type == "MINUS" + "EQUALS": value = {"type": "sub", "left": last, "right": value}
                if type == "ASTERISK" + "EQUALS": value = {"type": "mul", "left": last, "right": value}
                if type == "SLASH" + "EQUALS": value = {"type": "div", "left": last, "right": value}
                if type == "BITWISEOR" + "EQUALS": value = {"type": "bitwise or", "left": last, "right": value}
                if type == "BITWISEXOR" + "EQUALS": value = {"type": "bitwise xor", "left": last, "right": value}
                if type == "BITWISEAND" + "EQUALS": value = {"type": "bitwise and", "left": last, "right": value}
                if type == "BITWISELEFT" + "EQUALS": value = {"type": "bitwise left", "left": last, "right": value}
                if type == "BITWISRIGHT" + "EQUALS": value = {"type": "bitwise right", "left": last, "right": value}

                ast.append({"type": "set", "target": ast[len(ast) - 1], "index": index, "value": value})
                ast.pop(len(ast) - 2)

                if get(pos) in ["COMMA", "SEMICOLON"]:
                    if get(pos) == "COMMA":
                        if get(pos + 1) == "IDENTIFIER":
                            pos += 1
                        
                        else:
                            error("expected identifier after ','")

                    else:
                        pos += 1

            else:
                ast.append({"type": "get", "target": ast[len(ast) - 1], "index": index})
                ast.pop(len(ast) - 2)
                if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) == "LPAREN":
            last = None

            if len(ast) != 0:
                last = ast[len(ast) - 1]

            if last != None and last["type"] in ["IDENTIFIER", "call", "get"]:
                args, pos = get_call_args(pos)

                if len(tokens) <= pos:
                    pos -= 1
                    error("expected ';'")

                if get(pos) in ["SEMICOLON", "LPAREN", "RPAREN", "RBRACKET", "LBRACKET"] + operators:
                    ast.append({"type": "call", "value": last, "args": args})
                    ast.pop(len(ast) - 2)
                    if get(pos) == "SEMICOLON": pos += 1

                else:
                    error("expected ';'")

            else:
                temp_tokens = []
                ignore = 1
                pos += 1

                while True:
                    if get(pos) == "RPAREN":
                        ignore -= 1

                        if ignore == 0:
                            break

                        temp_tokens.append(get(pos, True))
                        pos += 1

                    elif get(pos) == "LPAREN":
                        temp_tokens.append(get(pos, True))
                        ignore += 1
                        pos += 1

                    else:
                        temp_tokens.append(get(pos, True))
                        pos += 1

                temp_tokens.append("SEMICOLON")
                ast.append(parser(temp_tokens, file, custom_types)[0])
                pos += 1
                
                if get(pos) == "SEMICOLON":
                    pos += 1

        elif (get(pos) in ["VOID", "AUTO", "CONST"] + types) or (get(pos) == "IDENTIFIER" and get(pos + 1).split("::")[len(get(pos + 1).split("::")) - 1].replace("~", "") in custom_types):
            if get(pos) in types and get(pos + 2) in ["SEMICOLON", "COMMA", "LPAREN", "RPAREN"] + operators and get(pos + 1) not in ["LBRACKET"]:
                ast.append({"type": get(pos), "value": get(pos + 1)})
                if get(pos + 2) == "SEMICOLON": pos += 3
                else: pos += 2

            else:
                first_pos = pos
                const = False

                if get(pos) == "CONST":
                    const = True
                    pos += 1

                if (get(pos) in ["VOID", "AUTO"] + types) or (get(pos) == "IDENTIFIER" and get(pos + 1).split("::")[len(get(pos + 1).split()) - 1].replace("~", "") in custom_types):
                    if get(pos) == "IDENTIFIER":
                        type = {"type": "STRUCT_T", "value": get(pos + 1)}
                        pos += 1

                    else:
                        type = get(pos)

                    if get(pos + 1) not in ["IDENTIFIER", "LPAREN", "COMMA", "LBRACKET"]:
                        if type in ["VOID", "AUTO"]: error("can't use void type like this")
                        ast.append({"type": get(pos), "value": get(pos + 1)})
                        if get(pos + 2) == "SEMICOLON": pos += 3
                        else: pos += 2

                    else:
                        if get(pos + 1) == "LBRACKET":
                            if type in ["VOID", "AUTO"]: error("can't use void type like this")
                            temp_size, pos = get_index(pos + 2)
                            size = None
                            if temp_size["type"] != "NULL": size = temp_size
                            type = {"type": "ARRAY_T", "array_type": type, "size": size}

                        else:
                            pos += 1

                        type_end_pos = pos

                        if get(pos) == "IDENTIFIER":
                            name = get(pos + 1)

                            if get(pos + 2) == "LPAREN":
                                args, pos, var_arg = get_def_args(pos + 2)
                                if "type" in type and type["size"] != None: error("size must be none")
                                temp_ast = {}


                                if get(pos) != "SEMICOLON": temp_ast, pos = get_func_ast(pos)
                                else: pos += 1

                                ast.append({"type": "func", "return_type": type, "const": const, "name": name, "args": args, "ast": temp_ast, "var_arg": var_arg})

                            elif get(pos + 2) == "EQUALS":
                                if type in ["VOID"]: error("can't use void type like this")
                                temp_tokens, pos = collect_tokens(pos + 3, stop_tokens = ["SEMICOLON"])
                                ast.append({"type": "var", "value_type": type, "name": name, "value": parser(temp_tokens, file, custom_types)[0], "const": const})
                                
                                if get(pos) in ["SEMICOLON", "COMMA"]:
                                    if get(pos) == "COMMA":
                                        for index, i in enumerate(tokens[first_pos:type_end_pos]):
                                            tokens.insert(pos + index + 1, i)

                                    pos += 1

                            elif get(pos + 2) in ["SEMICOLON", "COMMA"]:
                                if type in ["VOID"]: error("can't use void type like this")

                                if get(pos + 2) == "COMMA":
                                    for index, i in enumerate(tokens[first_pos:type_end_pos]):
                                        tokens.insert(pos + index + 3, i)

                                    pos += 3

                                else:
                                    pos += 2

                                ast.append({"type": "var", "value_type": type, "name": name, "value": None, "const": const})
                                if get(pos) == "SEMICOLON": pos += 1

                            else:
                                error("expected ';'")

                        elif get(pos) == "LPAREN":
                            if type["type"] == "STRUCT_T":
                                args, pos, var_arg = get_def_args(pos)
                                temp_ast = {}

                                if get(pos) != "SEMICOLON":
                                    temp_ast, pos = get_func_ast(pos)
                                else: pos += 1

                                print("destructor" if type["value"][0] == "~" else "constructor")

                                ast.append({"type": "destructor" if type["value"][0] == "~" else "constructor", "args": args, "ast": temp_ast})
                
                else:
                    error("expected type")

        elif get(pos) in ["SEMICOLON", "NULL"]:
            ast.append({"type": "NULL", "value": "NULL"})
            pos += 1

    return ast

class Context:
    def __init__(self, ast, file):
        self.reset(ast, file)

    def reset(self, ast, file):
        self.main_ast = ast
        self.ast = ast
        self.version = None
        self.scope = {
            "global": {
                "system": std.std["system"],
                "__file__": {"type": "var", "value": {"type": "STRING", "value": file}, "const": True},
                "__osname__": {"type": "var", "value": {"type": "STRING", "value": os.name}, "const": True},
                "__machine__": {"type": "var", "value": {"type": "STRING", "value": platform.machine()}, "const": True},
                "__system__": {"type": "var", "value": {"type": "STRING", "value": platform.system()}, "const": True},
                "__arch__": {"type": "var", "value": {"type": "STRING", "value": platform.architecture()[0]}, "const": True},
                "__platform__": {"type": "var", "value": {"type": "STRING", "value": sys.platform}, "const": True},
                "__node__": {"type": "var", "value": {"type": "STRING", "value": platform.node()}, "const": True}
            }
        }
        self.args = []
        self.current_scope = "global"
        self.included = []
        self.include_folders = []
        self.main_file = file
        self.file = file
        self.current_return_type = None
        self.current_array_type = None
        self.cache = {}
        self.include_cache = {}
        self.program_state_var = True
        self.is_thread = False
        self.actual_context = None
        self.is_compiled_var = False
        self.parent_scopes = []
        self.recursions = {}
        self.recursion_limit = 1000
        self.return_state = False
        self.custom_types = []
        self.pass_scope_check = False
        self.namespaces = []

    def update(self):
        self.return_state = False

    def get_unique_name(self):
        value = 0

        while self.is_exists(f"unique>{value}"):
            value += 1

        return f"unique>{value}"

    def set_scope(self, scope):
        self.current_scope = scope

    def get_scope(self):
        return self.current_scope

    def add_scope(self, scope):
        index = 0
        name = scope

        while name in self.scope:
            name = scope + ">" + str(index)
            index += 1
        
        self.scope[name] = {}
        return name

    def delete_scope(self, scope):
        for i in self.scope[scope]:
            if self.scope[scope][i]["type"] == "trigger":
                self.scope[scope][i]["target"](*(self.scope[scope][i]["args"]))
            
            if "value" in self.scope[scope][i] and "callback" in self.scope[scope][i]["value"]:
                self.scope[scope][i]["value"]["callback"](self, self.scope[scope][i]["value"])

        del self.scope[scope]

    def add_parent_scope(self, scope):
        self.parent_scopes.append(scope)

    def rem_parent_scope(self, scope):
        self.parent_scopes.remove(scope)

    def get_current_elements(self):
        tmp = self.scope["global"].copy()

        if self.current_scope != "global":
            tmp.update(self.scope[self.current_scope])

        parent_scopes = self.parent_scopes.copy()
        parent_scopes.reverse()

        for i in parent_scopes:
            tmp.update(self.scope[i])

        return tmp

    def begin_namespace(self, name):
        if not self.is_exists(name):
            self.set(name, {"type": "namespace", "name": name, "scope": {}})

        self.namespaces.append(name)

    def end_namespace(self):
        self.namespaces.pop()

    def create_struct(self, name, type):
        struct = self.get(type["value"])
        object = {"type": "struct_object", "struct_type": type["value"], "parent_scope": self.current_scope, "scope": {"public": {}, "private": {}}}
    
        for j in struct["ast"]:
            if j["type"] in ["func", "var", "constructor", "destructor"]:
                if j["type"] in ["constructor", "destructor"]:
                    j["name"] = "<" + j["type"] + ">"
                    j["type"] = "func"
                    j["return_type"] = "VOID"

                tmp = j["name"]
                j["name"] = self.get_unique_name()
                self.pass_scope_check = True
                tmp_ast = self.ast
                self.ast = [j]
                tmp_ret = self.current_return_type
                if j["type"] == "func": self.current_return_type = j["return_type"]
                else: self.current_return_type = None
                value = interpreter(self)
                self.current_return_type = tmp_ret
                self.ast = tmp_ast
                self.pass_scope_check = False
                tmp_var = self.get(j["name"])
                tmp_var["parent_object"] = object
                object["scope"]["public"][tmp] = tmp_var
                j["name"] = tmp

                if tmp in ["<constructor>", "<destructor>"]:
                    print("aaahhhhh")

        self.set(name, object)

    def parse_key(self, key):
        key = key.split("::")
        namespaces = key[:-1]
        objects = key[len(namespaces)].split(".")
        return namespaces, objects

    def is_exists(self, key, search_current = False):
        namespaces, objects = self.parse_key(key)

        target = objects[0]
        object = None

        if namespaces == []:
            for i in ([self.current_scope] if search_current else list(set([self.current_scope] + self.parent_scopes[::-1] + ["global"]))):
                if i == "global":
                    current = [self.scope["global"]]

                    for j in self.namespaces:
                        if j not in current[len(current) - 1]:
                            tools.error("namespace '" + j + "' was not declared in this scope", self.file)

                        current.append(current[len(current) - 1][j]["scope"])

                    for j in current[::-1]:
                        if target in j:
                            object = j[target]
                            break

                elif target in self.scope[i]:
                    object = self.scope[i][target]

                if object != None: break

        else:
            current = self.scope["global"]

            for i in namespaces:
                if i not in current:
                    tools.error("namespace '" + i + "' was not declared in this scope", self.file)

                current = current[i]["scope"]

            if target not in current:
                return False

            object = current[target]

        if object == None:
            return False

        for i in objects[1:]:
            if "value" in object and type(object["value"]) != list:
                object = object["value"]

            if i not in object["scope"]["public"]:
                return False

            object = object["scope"]["public"][i]

        return True

    def set(self, key, value, force = False):
        namespaces, objects = self.parse_key(key)

        if self.namespaces == []:
            scope = self.scope[self.current_scope]

            if not force:
                if namespaces == []:
                    for i in list(set([self.current_scope] + self.parent_scopes[::-1] + ["global"])):
                        if i == "global":
                            current = [self.scope["global"]]

                            for j in self.namespaces:
                                if j not in current[len(current) - 1]:
                                    tools.error(f"namespace '{j}' was not declared in this scope", self.file)

                                current.append(current[len(current) - 1][j]["scope"])

                            for j in current[::-1]:
                                if objects[0] in j:
                                    scope = j
                                    break

                            if objects[0] in j:
                                break

                        elif objects[0] in self.scope[i]:
                            scope = self.scope[i]
                            break

                else:
                    scope = self.scope["global"]

                    for i in namespaces:
                        scope = scope[i]["scope"]

            key = objects[0]

            if len(objects) != 1:
                object = scope[key]

            for i in objects[1:]:
                key = i
                scope = object["scope"]["public"]
                object = object["scope"]["public"][i]
            
            if key in scope:
                if "value" in scope[key] and "callback" in scope[key]["value"]:
                    scope[key]["value"]["callback"](self, scope[key]["value"])

            if "not assigned" in value:
                del value["not assigned"]
                
            scope[key] = value

        else:
            if namespaces != [] and len(objects) != 1:
                tools.error("invalid usage of namespaces", self.file)

            scope = self.scope["global"]

            for i in self.namespaces:
                scope = scope[i]["scope"]

            scope[objects[0]] = value

    def get(self, key):
        if self.is_exists(key):
            namespaces, objects = self.parse_key(key)

            target = objects[0]
            object = None

            if namespaces == []:
                for i in list(set([self.current_scope] + self.parent_scopes[::-1] + ["global"])):
                    if i == "global":
                        current = [self.scope["global"]]

                        for j in self.namespaces:
                            if j not in current[len(current) - 1]:
                                tools.error("namespace '" + j + "' was not declared in this scope", self.file)

                            current.append(current[len(current) - 1][j]["scope"])

                        for j in current[::-1]:
                            if target in j:
                                object = j[target]
                                break

                    elif target in self.scope[i]:
                        object = self.scope[i][target]

                    if object != None: break

            else:
                current = self.scope["global"]

                for i in namespaces:
                    current = current[i]["scope"]

                object = current[target]

            for i in objects[1:]:
                if "value" in object and type(object["value"]) != list:
                    object = object["value"]

                object = object["scope"]["public"][i]

            return object

        else:
            tools.error(f"'{key}' was not declared in this scope", self.file)

    def delete(self, key):
        if self.is_exists(key):
            if self.current_scope != "global":
                if key in self.scope[self.current_scope]:
                    if "value" in self.scope[self.current_scope][key] and "callback" in self.scope[self.current_scope][key]["value"]:
                        self.scope[self.current_scope][key]["callback"](self, self.scope[self.current_scope][key]["value"])
                    del self.scope[self.current_scope][key]
                    return

            if "value" in self.scope["global"][key] and "callback" in self.scope["global"][key]["value"]:
                self.scope["global"][key]["callback"](self, self.scope["global"][key]["value"])
            del self.scope["global"][key]

        else:
            tools.error(f"'{key}' was not declared in this scope", self.file)

    def is_main_file(self):
        return self.main_file == self.file

    def is_in_function(self):
        return self.current_scope != "global" and not self.pass_scope_check

    def prepare_to_execute(self, key):
        name = key.split(">")[0]

        if name in self.recursions:
            self.recursions[name] += 1

            if self.recursions[name] >= self.recursion_limit:
                tools.error(f"recursion limit exceeded: '{name}'", self.file)

        else:
            self.recursions[name] = 1

        tmp = self.add_scope(key)
        
        self.cache[tmp] = {
            "ast": self.ast, "current_return_type": self.current_return_type,
            "current_scope": self.current_scope, "parent_scopes": self.parent_scopes
        }

        self.ast = self.get(key)["ast"]
        self.current_return_type = self.get(key)["return_type"]
        self.current_scope = tmp
        self.parent_scopes = []
        return self.current_scope

    def end_execute(self):
        name = self.current_scope.split(">")[0]
        self.recursions[name] -= 1

        if self.recursions[name] == 0:
            del self.recursions[name]

        elif self.recursions[name] < 0:
            tools.error("unknown error", self.file)

        self.delete_scope(self.current_scope)
        tmp = self.current_scope
        self.ast, self.current_return_type = self.cache[self.current_scope]["ast"], self.cache[self.current_scope]["current_return_type"]
        self.current_scope, self.parent_scopes = self.cache[self.current_scope]["current_scope"], self.cache[self.current_scope]["parent_scopes"]
        del self.cache[tmp]

    def is_included(self, key):
        return key in self.included

    def is_compiled(self):
        return self.is_compiled_var

    def get_ast(self):
        return self.ast

    def prepare_to_include(self, ast, file):
        self.include_cache[len(self.include_cache)] = {"ast": self.ast, "file": self.file}
        self.ast = ast
        self.file = file

    def end_include(self):
        self.ast, self.file = self.include_cache[len(self.include_cache) - 1]["ast"], self.include_cache[len(self.include_cache) - 1]["file"]
        self.include_cache.pop(len(self.include_cache) - 1)

    def is_base(self):
        return self.current_scope == "global"

    def program_state(self, program_state = None):
        if program_state != None:
            self.program_state_var = program_state

        else:
            return self.program_state_var

def interpreter(context: Context):
    result_report = {}

    for index, i in enumerate(context.get_ast()):
        context.update()
        if isinstance(i, str) or i == None: tools.error(f"unknown exception at runtime (probably caused by an unhandled parser exception)", f"{context.file}:<{i}>")
        if i["type"] == "func":
            if context.current_scope != "global" and not context.pass_scope_check:
                tools.error("a function-definition is not allowed here before", context.file)

            if context.is_exists(i["name"]):
                tools.error("can't overload a function", context.file)

            if not (i["return_type"] in ["VOID", "FLOAT", "INT", "STRING", "BOOL"] or tools.is_array_t(i["return_type"])):
                tools.error("unknown return type for a function: '" + i["return_type"].lower() + "'", context.file)

            context.set(i["name"], {"type": "func", "return_type": i["return_type"], "args": i["args"], "ast": i["ast"], "const": False})
            context.add_scope(i["name"])

            if i["name"] == "main" and i["return_type"] == "INT" and (i["args"] == {"args": {"type": "ARRAY_T", "array_type": "STRING", "size": None}} or i["args"] == {}):
                if context.is_main_file() and not context.is_in_function() and context.program_state():
                    context.prepare_to_execute("main")

                    if i["args"] == {"args": tools.ArrayType(tools.StringType(), size = None)}:
                        context.set("args", tools.Array(context.args), True)

                    error_code = interpreter(context)
                    context.end_execute()

                    if error_code in ["BREAK", "CONTINUE"]:
                        tools.error("can't use '" + error_code.lower() + "' here", context.file)

                    elif error_code["type"] == "NULL":
                        tools.error("non-void functions should return a value", context.file)

                    else:
                        if error_code["type"] == "INT":
                            error_code = error_code["value"]

        elif i["type"] == "struct":
            if context.current_scope != "global" and not context.pass_scope_check:
                tools.error("a structure-definition is not allowed here before", context.file)

            context.set(i["name"], {"type": "struct", "ast": i["ast"]})

        elif i["type"] == "namespace":
            context.begin_namespace(i["name"])
            tmp = context.ast
            context.ast = i["ast"]
            interpreter(context)
            context.ast = tmp
            context.end_namespace()

        elif i["type"] in ["increment", "decrement"]:
            if i["value"]["type"] != "IDENTIFIER":
                tools.error("not implemented", context.file)

            value = i["value"]["value"]

            if context.get(value)["const"]:
                tools.error("assignment of read-only variable '" + value + "'", context.file)

            if context.get(value)["value"]["type"] in ["FLOAT", "INT"]:
                temp = context.get(value)["value"]

                if context.get(value)["value"]["type"] == "INT":
                    context.set(value, {
                        "type": "var", "value": {
                            "type": context.get(value)["value"]["type"],
                            "value": str(int(context.get(value)["value"]["value"]) + (1 if i["type"] == "increment" else -1))},
                            "const": False
                        }
                    )

                elif context.get(value)["value"]["type"] == "FLOAT":
                    context.set(value, {
                        "type": "var", "value": {
                            "type": context.get(value)["value"]["type"],
                            "value": str(float(context.get(value)["value"]["value"].lower().replace("f", "")) + (1 if i["type"] == "increment" else -1)) + "f"},
                            "const": False
                        }
                    )

                else:
                    tools.error("unknown error", context.file)

                if len(context.ast) == 1:
                    if not i["pre"]:
                        return temp

                    else:
                        return context.get(value)["value"]

            else:
                tools.error("'" + value + "' should be an integer or float value", context.file)

        elif i["type"] in ["break", "continue"]:
            if not context.is_in_function(): tools.error("can't use '" + i["type"] + "' here", context.file)
            return i["type"].upper()

        elif "type" in i["type"] and i["type"]["type"] == "STRUCT_T":
            tools.error("invalid usage of structures", context.file)
                
        elif i["type"] == "var":
            if (i["value_type"] != None and "type" in i["value_type"] and i["value_type"]["type"] == "STRUCT_T") \
                or (context.is_exists(i["name"]) and context.get(i["name"])["type"] == "struct_object"):
                if i["value"] != None:
                    tmp_ast = context.ast
                    context.ast = [i["value"]]
                    value = interpreter(context)
                    context.ast = tmp_ast

                    if i["value_type"] == None:
                        i["value_type"] = {"type": "STRUCT_T", "value": context.get(i["name"])["struct_type"]}

                    if value["type"] == "struct_object" and i["value_type"]["value"] == value["struct_type"]:
                        value["const"] = i["const"]
                        context.set(i["name"], value, True)

                    else:
                        tools.error("bad value", context.file)

                else:
                    context.create_struct(i["name"], i["value_type"])

            else:
                size = None

                if i["value_type"] != None and "type" in i["value_type"] and i["value_type"]["type"] == "ARRAY_T":
                    if "type" in i["value_type"]["array_type"] and i["value_type"]["array_type"]["type"] == "STRUCT_T":
                        tools.error("cannot create an array with struct", context.file)

                    if i["value_type"]["size"] != None:
                        tmp_ast = context.ast
                        context.ast = [i["value_type"]["size"]]
                        size = interpreter(context)
                        context.ast = tmp_ast

                if i["value"] == None and "type" in i["value_type"] and i["value_type"]["type"] == "ARRAY_T":
                    value = {"type": "array_object", "array_type": i["value_type"]["array_type"], "size": size, "value": {}, "scope": {"public": {}, "private": {}}}

                else:
                    if i["value"] == None:
                        i["value"] = {"type": i["value_type"], "value": None}

                    tmp_ast = context.ast
                    context.ast = [i["value"]]
                    value = interpreter(context)
                    context.ast = tmp_ast

                if i["value_type"] == None:
                    if context.get(i["name"])["const"]:
                        tools.error("assignment of read-only variable '" + i["name"] + "'", context.file)

                    if value["type"] != context.get(i["name"])["value"]["type"]:
                        tmp_ast = context.ast
                        context.ast = [{"type": "cast", "cast_type": context.get(i["name"])["value"]["type"], "value": value}]
                        value = interpreter(context)
                        context.ast = tmp_ast

                    context.set(i["name"], {"type": "var", "value": value.copy(), "const": context.get(i["name"])["const"]})

                else:
                    if context.is_exists(i["name"], True):
                        tools.error("redefinition of '" + i["name"] + "'", context.file)

                    else:
                        if i["value_type"] == "AUTO":
                            if value == None:
                                tools.error("required a value for auto type", context.file)

                        elif tools.is_array_t(i["value_type"]) and tools.is_array(value):
                            if i["value_type"]["size"] != None:
                                tmp_ast = context.ast
                                context.ast = [{"type": i["value_type"]["array_type"], "value": None}]
                                temp_type = interpreter(context)
                                context.ast = tmp_ast

                                if size["type"] == "INT":
                                    if int(size["value"]) < 0:
                                        tools.error("size must be positive", context.file)

                                    elements = [temp_type] * int(size["value"])

                                else:
                                    tools.error("size must be an integer", context.file)

                            else:
                                if i["value"] == None:
                                    tools.error("size must be defined when no value is given", context.file)

                                elements = []

                            temp = value["value"]

                            if temp == None:
                                temp = []

                            for temp_index, j in enumerate(temp):
                                if i["value_type"]["size"] != None:
                                    if temp_index >= int(size["value"]):
                                        tools.error("'array' index out of range", context.file)

                                else:
                                    elements.append(None)

                                tmp_ast = context.ast
                                context.ast = [j]
                                element = interpreter(context)
                                context.ast = tmp_ast

                                if element["type"] != i["value_type"]["array_type"]:
                                    tmp_ast = context.ast
                                    context.ast = [{"type": "cast", "cast_type": i["value_type"]["array_type"], "value": element}]
                                    element = interpreter(context)
                                    context.ast = tmp_ast

                                elements[temp_index] = element

                            _globals = {}

                            exec(
                                "def func(environ):\n" +
                                "    temp = environ[\"context\"].get(\"" + i["name"] + "\")[\"value\"]\n" +
                                "    return len(temp[\"value\"] if \"value\" in temp else temp)", _globals
                            )

                            value = {
                                "type": "array_object", "array_type": i["value_type"]["array_type"], "size": i["value_type"]["size"], "value": elements, "scope": {
                                    "public": {
                                        "length": {"type": "libfunc", "args": {}, "return_type": "INT", "func": _globals["func"], "const": True}
                                }, "private": {}}
                            }

                        elif value["type"] != i["value_type"] and value["type"] != "NULL":
                            tmp_ast = context.ast
                            context.ast = [{"type": "cast", "cast_type": i["value_type"], "value": value}]
                            value = interpreter(context)
                            context.ast = tmp_ast

                        context.set(i["name"], {"type": "var", "value": value.copy(), "const": i["const"]}, True)

        elif i["type"] == "include":
            for lib in i["libs"]:
                if context.is_included(lib) and not context.is_compiled():
                    # tools.warning("trying to include '" + lib + "' twice", context.file)
                    continue

                context.included.append(lib)
                name, ext = os.path.splitext(lib)

                if ext == ".py":
                    file_path = None
                    
                    for j in context.include_folders:
                        if os.path.exists(j + "/" + lib):
                            file_path = j + "/" + lib
                            break

                    if file_path == None: tools.error("'" + lib + "'" + " " + "was not found", context.file)

                    if os.path.split(file_path)[0] not in sys.path:
                        sys.path.insert(0, os.path.split(file_path)[0])

                    tmp = getattr(importlib.import_module(os.path.split(name)[1]), os.path.split(name)[1])

                    if i["namespace"]:
                        for j in tmp:
                            context.begin_namespace(lib if i["special_namespace"] == None else i["special_namespace"])
                            context.set(j, tmp[j])
                            context.end_namespace()
                    
                    else:
                        for j in tmp:
                            if i["names"] != None:
                                if j not in i["names"]:
                                    found = False

                                    for name in i["names"]:
                                        if j.startswith(name):
                                            found = True
                                            break

                                    if not found:
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
                        tools.error("'" + lib + "'" + " " + "was not found", context.file)

                    file_content = open(file_path, "r").read()
                    ast = None

                    if os.path.splitext(os.path.split(file_path)[1])[0] + ".rsxc" in os.listdir(os.path.split(file_path)[0]):
                        with open(os.path.splitext(file_path)[0] + ".rsxc", "rb") as file:
                            content = tools.load_bytecode(file.read())

                            if "version" in content:
                                if content["version"] == context.version:
                                    if content["file_content"] == hashlib.sha256(file_content.encode()).digest():
                                        ast = content["ast"]
                                        context.custom_types += content["custom_types"]

                    if ast is None:
                        ast = parser(lexer(tools.read_file(file_path), file_path), file_path, context.custom_types)

                        with open(os.path.splitext(file_path)[0] + ".rsxc", "wb") as file:
                            file.write(tools.dump_bytecode(ast, context.custom_types, file_content))

                    context.prepare_to_include(ast, file_path)
                    if i["namespace"]:
                        context.begin_namespace(lib if i["special_namespace"] == None else i["special_namespace"])
                    tmp_ret = context.current_return_type
                    context.current_return_type = None
                    tmp_parent_scopes = context.parent_scopes
                    context.parent_scopes = []
                    interpreter(context)
                    context.parent_scopes = tmp_parent_scopes
                    context.current_return_type = tmp_ret
                    if i["namespace"]: context.end_namespace()
                    context.end_include()

                    if not i["namespace"] and i["names"] != None:
                        tools.error("including by name is not implemented", context.file)

        elif i["type"] == "INITLIST":
            if i["value"] == None:
                tools.error("initializer list error")

            elements = []

            for j in i["value"]:
                tmp_ast = context.ast
                context.ast = [j]
                elements.append(interpreter(context))
                context.ast = tmp_ast

            type = None

            for i in elements:
                if type == None: type = i["type"]
                if i["type"] != type: tools.error("array type mismatch", context.file)

            _globals = {}

            exec(
                "def func(environ):\n" +
                "    return " + str(len(elements)), _globals
            )

            array = {
                "type": "array_object", "array_type": type, "size": len(elements), "value": elements, "scope": {
                    "public": {
                        "length": {"type": "libfunc", "args": {}, "return_type": "INT", "func": _globals["func"], "const": True}
                }, "private": {}}
            }

            return array

        elif i["type"] in ["struct_object", "array_object"]:
            return i

        elif i["type"] in ["IDENTIFIER", "AUTO", "BOOL", "STRING", "INT", "FLOAT", "VOID", "NULL"]:
            if i["type"] == "IDENTIFIER":
                temp = context.get(i["value"])

                if temp["type"] in ["libfunc", "func", "struct"]:
                    return i["value"]

                if temp["type"] in ["struct_object", "array_object"]:
                    return temp

                return temp["value"].copy()

            elif i["type"] == "AUTO":
                return i["value"]

            elif i["value"] == None:
                if i["type"] == "INT":
                    return {"type": "INT", "value": "0"}

                if i["type"] == "FLOAT":
                    return {"type": "FLOAT", "value": "0.0f"}

                if i["type"] == "BOOL":
                    return {"type": "BOOL", "value": "FALSE"}

                if i["type"] == "STRING":
                    return {"type": "STRING", "value": ""}

                else:
                    tools.error("unexpected type", context.file)

            else:
                return i

        elif i["type"] == "get":
            tmp_ast = context.ast
            context.ast = [i["index"]]
            value = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["target"]]
            target = interpreter(context)
            context.ast = tmp_ast

            if target["type"] not in ["array_object", "STRING"]:
                if target["type"] == "IDENTIFIER":
                    tools.error("'" + target["value"] + "' is not subscriptable", context.file)

                else:
                    tools.error("'" + target["type"].lower() +  "' is not subscriptable", context.file)

            if value["type"] == "INT":
                if len(target["value"]) > int(value["value"]) and -(len(target["value"])) <= int(value["value"]):
                    if target["type"] == "STRING":
                        return {"type": "STRING", "value": target["value"][int(value["value"])]}

                    return target["value"][int(value["value"])]

                else:
                    tools.error("'" + target["type"].lower() + "' index out of range", context.file)

            else:
                tools.error("index must be an integer", context.file)

        elif i["type"] == "set":
            tmp_ast = context.ast
            context.ast = [i["index"]]
            value = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["target"]]
            target = interpreter(context)
            context.ast = tmp_ast

            if target["type"] not in ["array_object"]:
                if target["type"] == "IDENTIFIER":
                    tools.error("'" + target["value"] + "' does not support item assignment", context.file)

                else:
                    tools.error("'" + target["type"].lower() +  "' does not support item assignment", context.file)

            if value["type"] == "INT":
                if len(target["value"]) > int(value["value"]) and -(len(target["value"])) <= int(value["value"]):
                    tmp_ast = context.ast
                    context.ast = [i["value"]]
                    temp_value = interpreter(context)
                    context.ast = tmp_ast

                    if target["array_type"] == temp_value["type"]:
                        target["value"][int(value["value"])] = temp_value

                    else:
                        tmp_ast = context.ast
                        context.ast = [{"type": "cast", "cast_type": target["array_type"], "value": temp_value}]
                        target["value"][int(value["value"])] = interpreter(context)
                        context.ast = tmp_ast

                else:
                    tools.error("'" + target["type"].lower() + "' index out of range", context.file)

            else:
                tools.error("index must be an integer", context.file)

        elif i["type"] == "neg":
            tmp_ast = context.ast
            context.ast = [i["value"]]
            value = interpreter(context)
            context.ast = tmp_ast

            if value["type"] == "INT":
                return {"type": value["type"], "value": str(-int(value["value"]))}

            elif value["type"] == "FLOAT":
                return {"type": value["type"], "value": str(-float(value["value"]))}

            else:
                tools.error("'-' operator can only use with integers and floats", context.file)

        elif i["type"] == "pos":
            tmp_ast = context.ast
            context.ast = [i["value"]]
            value = interpreter(context)
            context.ast = tmp_ast

            if value["type"] == "INT":
                return {"type": value["type"], "value": str(abs(int(value["value"])))}

            elif value["type"] == "FLOAT":
                return {"type": value["type"], "value": str(abs(float(value["value"])))}

            else:
                tools.error("'+' operator can only use with integers and floats", context.file)

        elif i["type"] == "not":
            tmp_ast = context.ast
            context.ast = [i["value"]]
            value = interpreter(context)
            context.ast = tmp_ast

            if value["type"] == "BOOL":
                if value["value"] == "TRUE":
                    return {"type": value["type"], "value": "FALSE"}

                elif value["value"] == "FALSE":
                    return {"type": value["type"], "value": "TRUE"}

                else:
                    tools.error("unexpected type", context.file)

            elif value["type"] == "INT":
                if value["value"] == "0":
                    return {"type": value["type"], "value": "TRUE"}

                else:
                    return {"type": value["type"], "value": "FALSE"}

            else:
                tools.error("expected 'int' or 'bool' value for '!' operator, not '" + value["type"].lower() + "'", context.file)

        elif i["type"] == "bitwise not":
            tmp_ast = context.ast
            context.ast = [i["value"]]
            value = interpreter(context)
            context.ast = tmp_ast

            if value["type"] == "INT":
                return {"type": value["type"], "value": str(~int(value["value"]))}

            else:
                tools.error("'~' operator can only use with integers", context.file)

        elif i["type"] == "bitwise left":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] == "INT" and right["type"] == "INT":
                return {"type": "INT", "value": str(int(left["value"]) << int(right["value"]))}

            else:
                tools.error("can't perform bitwise left operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "bitwise right":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] == "INT" and right["type"] == "INT":
                return {"type": "INT", "value": str(int(left["value"]) >> int(right["value"]))}

            else:
                tools.error("can't perform bitwise right operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "bitwise or":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] == "INT" and right["type"] == "INT":
                return {"type": "INT", "value": str(int(left["value"]) | int(right["value"]))}

            elif left["type"] == "BOOL" and right["type"] == "BOOL":
                return {"type": "BOOL", "value": str((True if left["value"] == "TRUE" else False) | (True if right["value"] == "TRUE" else False))}

            else:
                tools.error("can't perform bitwise or operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "bitwise and":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] == "INT" and right["type"] == "INT":
                return {"type": "INT", "value": str(int(left["value"]) & int(right["value"]))}

            elif left["type"] == "BOOL" and right["type"] == "BOOL":
                return {"type": "BOOL", "value": str((True if left["value"] == "TRUE" else False) & (True if right["value"] == "TRUE" else False))}

            else:
                tools.error("can't perform bitwise and operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "bitwise xor":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] == "INT" and right["type"] == "INT":
                return {"type": "INT", "value": str(int(left["value"]) ^ int(right["value"]))}

            elif left["type"] == "BOOL" and right["type"] == "BOOL":
                return {"type": "BOOL", "value": str((True if left["value"] == "TRUE" else False) ^ (True if right["value"] == "TRUE" else False))}

            else:
                tools.error("can't perform bitwise xor operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "cast":
            tmp_ast = context.ast
            context.ast = [i["value"]]
            value = interpreter(context)
            context.ast = tmp_ast
            
            if i["cast_type"] == "STRING":
                if value["type"] == "STRING":
                    return value

                elif value["type"] == "INT":
                    return {"type": "STRING", "value": str(value["value"])}

                elif value["type"] == "FLOAT":
                    return {"type": "STRING", "value": str(value["value"]).lower().replace("f", "")}

                elif value["type"] == "BOOL":
                    return {"type": "STRING", "value": str(value["value"]).lower()}

                elif value["type"] == "NULL":
                    return {"type": "STRING", "value": str(value["value"]).lower()}

                else:
                    tools.error("can't cast '" + value["type"].lower() + "' into '" + i["cast_type"].lower() + "'", context.file)

            elif i["cast_type"] == "INT":
                if value["type"] == "INT":
                    return value
                    
                elif value["type"] == "FLOAT":
                    return {"type": "INT", "value": str(int(float(value["value"].lower().replace("f", ""))))}

                elif value["type"] == "NULL":
                    return {"type": "INT", "value": "0"}

                elif value["type"] == "BOOL":
                    if value["value"] == "TRUE":
                        return {"type": "INT", "value": "1"}

                    elif value["value"] == "FALSE":
                        return {"type": "INT", "value": "0"}

                    else:
                        tools.error("unexpected error", context.file)
                    
                else:
                    tools.error("can't cast '" + value["type"].lower() + "' into '" + i["cast_type"].lower() + "'", context.file)

            elif i["cast_type"] == "FLOAT":
                if value["type"] == "FLOAT":
                    return value

                elif value["type"] == "INT":
                    return {"type": "FLOAT", "value": str(value["value"]) + ".0f"}

                else:
                    tools.error("can't cast '" + value["type"].lower() + "' into '" + i["cast_type"].lower() + "'", context.file)

            elif i["cast_type"] == "BOOL":
                if value["type"] == "BOOL":
                    return value

                elif value["type"] == "INT":
                    if value["value"] == "0":
                        return {"type": "BOOL", "value": "FALSE"}

                    else:
                        return {"type": "BOOL", "value": "TRUE"}

                else:
                    tools.error("can't cast '" + value["type"].lower() + "' into '" + i["cast_type"].lower() + "'", context.file)

            else:
                tools.error("can't cast '" + str(value["type"]).lower() + "' into '" + str(i["cast_type"]).lower() + "'", context.file)

        elif i["type"] == "switch":
            tmp_ast = context.ast
            context.ast = [i["value"]]
            value = interpreter(context)
            context.ast = tmp_ast
            match = False
            break_var = False

            cur = context.add_scope("__switch__")
            tmp = context.get_scope()
            context.add_parent_scope(tmp)
            context.set_scope(cur)

            for j in i["cases"]:
                if j != "default":
                    tmp_ast = context.ast
                    context.ast = [i["cases"][j]["value"]]
                    case_value = interpreter(context)
                    context.ast = tmp_ast

                    if value == case_value:
                        tmp_ast = context.ast
                        context.ast = i["cases"][j]["ast"]
                        tmp_ret = context.current_return_type
                        context.current_return_type = None
                        response = interpreter(context)
                        context.current_return_type = tmp_ret
                        context.ast = tmp_ast
                        match = True
                        
                        if response != None:
                            if "type" in response:
                                if response["type"] != "NULL":
                                    if context.return_state:
                                        context.set_scope(tmp)
                                        context.delete_scope(cur)
                                        context.rem_parent_scope(tmp)
                                        return response

                        if response == "BREAK":
                            context.set_scope(tmp)
                            context.delete_scope(cur)
                            context.rem_parent_scope(tmp)
                            break_var = True
                            break

            if break_var: continue
            if match == False:
                if "default" in i["cases"]:
                    tmp_ast = context.ast
                    context.ast = i["cases"]["default"]["ast"]
                    tmp_ret = context.current_return_type
                    context.current_return_type = None
                    response = interpreter(context)
                    context.current_return_type = tmp_ret
                    context.ast = tmp_ast

            context.set_scope(tmp)
            if cur in context.scope: context.delete_scope(cur)
            if tmp in context.parent_scopes: context.rem_parent_scope(tmp)

        elif i["type"] == "or":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] == "BOOL" and right["type"] == "BOOL":
                left = True if left["value"] == "TRUE" else False
                right = True if right["value"] == "TRUE" else False

                if left or right:
                    return {"type": "BOOL", "value": "TRUE"}

                else:
                    return {"type": "BOOL", "value": "FALSE"}

            else:
                tools.error("can't perform or operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "and":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] == "BOOL" and right["type"] == "BOOL":
                left = True if left["value"] == "TRUE" else False
                right = True if right["value"] == "TRUE" else False

                if left and right:
                    return {"type": "BOOL", "value": "TRUE"}

                else:
                    return {"type": "BOOL", "value": "FALSE"}

            else:
                tools.error("can't perform and operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "notequals":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                left = float(left["value"])
                right = float(right["value"])

            if left != right:
                return {"type": "BOOL", "value": "TRUE"}

            else:
                return {"type": "BOOL", "value": "FALSE"}

        elif i["type"] == "equalsequals":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                left = float(left["value"])
                right = float(right["value"])

            if left == right:
                return {"type": "BOOL", "value": "TRUE"}

            else:
                return {"type": "BOOL", "value": "FALSE"}

        elif i["type"] == "less":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    left = float(left["value"].replace("f", ""))
                    right = float(right["value"].replace("f", ""))

                else:
                    left = int(left["value"])
                    right = int(right["value"])

                if left < right:
                    return {"type": "BOOL", "value": "TRUE"}

                else:
                    return {"type": "BOOL", "value": "FALSE"}

            else:
                tools.error("can't perform less operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "lessequals":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    left = float(left["value"].replace("f", ""))
                    right = float(right["value"].replace("f", ""))

                else:
                    left = int(left["value"])
                    right = int(right["value"])

                if left <= right:
                    return {"type": "BOOL", "value": "TRUE"}

                else:
                    return {"type": "BOOL", "value": "FALSE"}

            else:
                tools.error("can't perform less operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "greater":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    left = float(left["value"].replace("f", ""))
                    right = float(right["value"].replace("f", ""))

                else:
                    left = int(left["value"])
                    right = int(right["value"])

                if left > right:
                    return {"type": "BOOL", "value": "TRUE"}

                else:
                    return {"type": "BOOL", "value": "FALSE"}

            else:
                tools.error("can't perform less operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "greaterequals":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    left = float(left["value"].replace("f", ""))
                    right = float(right["value"].replace("f", ""))

                else:
                    left = int(left["value"])
                    right = int(right["value"])

                if left >= right:
                    return {"type": "BOOL", "value": "TRUE"}

                else:
                    return {"type": "BOOL", "value": "FALSE"}

            else:
                tools.error("can't perform less operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "add":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    return {"type": "FLOAT", "value": str(float(left["value"].replace("f", "")) + float(right["value"].replace("f", "")))}

                else:
                    return {"type": "INT", "value": str(int(left["value"]) + int(right["value"]))}
                    
            elif left["type"] == "STRING" and right["type"] == "STRING":
                return {"type": "STRING", "value": str(left["value"] + right["value"])}

            else:
                tools.error("can't perform add operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "sub":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    return {"type": "FLOAT", "value": str(float(left["value"].replace("f", "")) - float(right["value"].replace("f", "")))}

                else:
                    return {"type": "INT", "value": str(int(left["value"]) - int(right["value"]))}

            else:
                tools.error("can't perform subtract operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "mul":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast
            
            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    return {"type": "FLOAT", "value": str(float(left["value"].replace("f", "")) * float(right["value"].replace("f", "")))}

                else:
                    return {"type": "INT", "value": str(int(left["value"]) * int(right["value"]))}

            elif left["type"] == "STRING" and right["type"] == "INT":
                return {"type": "STRING", "value": left["value"] * int(right["value"])}

            else:
                tools.error("can't perform multiply operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "div":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if float(right["value"].replace("f", "")) == 0.0:
                    tools.error("division by zero", context.file)

                if isfloat:
                    return {"type": "FLOAT", "value": str(float(left["value"].replace("f", "")) / float(right["value"].replace("f", "")))}

                else:
                    return {"type": "FLOAT", "value": str(int(left["value"]) / int(right["value"]))}

            else:
                tools.error("can't perform divide operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "mod":
            tmp_ast = context.ast
            context.ast = [i["left"]]
            left = interpreter(context)
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["right"]]
            right = interpreter(context)
            context.ast = tmp_ast

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    return {"type": "FLOAT", "value": str(float(left["value"].replace("f", "")) % float(right["value"].replace("f", "")))}

                else:
                    return {"type": "INT", "value": str(int(left["value"]) % int(right["value"]))}

            else:
                tools.error("can't perform remainder operation with '" + left["type"].lower() + "' and '" + right["type"].lower() + "' types", context.file)

        elif i["type"] == "for":
            cur = context.add_scope("__for__")
            tmp = context.get_scope()
            context.set_scope(cur)
            context.add_parent_scope(tmp)

            tmp_ast = context.ast
            context.ast = i["init"]
            tmp_ret = context.current_return_type
            context.current_return_type = None
            response = interpreter(context)
            context.current_return_type = tmp_ret
            context.ast = tmp_ast

            tmp_ast = context.ast
            context.ast = [i["condition"]]
            condition = interpreter(context)
            context.ast = tmp_ast

            while condition["type"] == "BOOL" and condition["value"] == "TRUE":
                context.update()

                tmp_scp = context.add_scope("__for_inner__")
                context.add_parent_scope(cur)
                context.set_scope(tmp_scp)

                tmp_ast = context.ast
                context.ast = i["ast"]
                tmp_ret = context.current_return_type
                context.current_return_type = None
                response = interpreter(context)
                context.current_return_type = tmp_ret
                context.ast = tmp_ast
                tmp_ret_state = context.return_state

                context.delete_scope(tmp_scp)
                context.rem_parent_scope(cur)
                context.set_scope(cur)

                tmp_ast = context.ast
                context.ast = i["update"]
                tmp_ret = context.current_return_type
                context.current_return_type = None
                interpreter(context)
                context.current_return_type = tmp_ret
                context.ast = tmp_ast

                if response != None:
                    if "type" in response:
                        if response["type"] != "NULL":
                            if tmp_ret_state:
                                context.rem_parent_scope(tmp)
                                context.delete_scope(cur)
                                context.set_scope(tmp)
                                return response

                tmp_ast = context.ast
                context.ast = [i["condition"]]
                condition = interpreter(context)
                context.ast = tmp_ast

                if response == "BREAK":
                    context.rem_parent_scope(tmp)
                    context.delete_scope(cur)
                    context.set_scope(tmp)
                    break

            context.set_scope(tmp)
            if cur in context.scope: context.delete_scope(cur)
            if tmp in context.parent_scopes: context.rem_parent_scope(tmp)

        elif i["type"] == "do":
            cur = context.add_scope("__dowhile__")
            tmp = context.get_scope()
            context.add_parent_scope(tmp)
            context.set_scope(cur)

            tmp_ast = context.ast
            context.ast = i["ast"]
            tmp_ret = context.current_return_type
            context.current_return_type = None
            response = interpreter(context)
            context.current_return_type = tmp_ret
            context.ast = tmp_ast

            if response in ["BREAK", "CONTINUE"]:
                context.delete_scope(cur)
                context.set_scope(tmp)
                context.rem_parent_scope(tmp)
                return response

            elif response != None:
                if "type" in response:
                    if response["type"] != "NULL":
                        if context.return_state:
                            context.delete_scope(cur)
                            context.set_scope(tmp)
                            context.rem_parent_scope(tmp)
                            return response

            context.set_scope(tmp)
            if cur in context.scope: context.delete_scope(cur)
            if tmp in context.parent_scopes: context.rem_parent_scope(tmp)

        elif i["type"] == "do while":
            cur = context.add_scope("__dowhile__")
            tmp = context.get_scope()
            context.add_parent_scope(tmp)
            context.set_scope(cur)

            tmp_ast = context.ast
            context.ast = i["ast"]
            tmp_ret = context.current_return_type
            context.current_return_type = None
            response = interpreter(context)
            context.current_return_type = tmp_ret
            context.ast = tmp_ast

            if response in ["BREAK", "CONTINUE"]:
                context.delete_scope(cur)
                context.set_scope(tmp)
                context.rem_parent_scope(tmp)
                return response

            elif response != None:
                if "type" in response:
                    if response["type"] != "NULL":
                        if context.return_state:
                            context.delete_scope(cur)
                            context.set_scope(tmp)
                            context.rem_parent_scope(tmp)
                            return response

            context.set_scope(tmp)
            context.rem_parent_scope(tmp)
            tmp_ast = context.ast
            context.ast = [i["condition"]]
            condition = interpreter(context)
            context.ast = tmp_ast
            context.add_parent_scope(tmp)
            context.set_scope(cur)

            while condition["type"] == "BOOL" and condition["value"] == "TRUE":
                context.update()

                tmp_ast = context.ast
                context.ast = i["ast"]
                tmp_ret = context.current_return_type
                context.current_return_type = None
                response = interpreter(context)
                context.current_return_type = tmp_ret
                context.ast = tmp_ast

                if response != None:
                    if "type" in response:
                        if response["type"] != "NULL":
                            if context.return_state:
                                context.set_scope(tmp)
                                context.delete_scope(cur)
                                context.rem_parent_scope(tmp)
                                return response

                context.set_scope(tmp)
                context.rem_parent_scope(tmp)
                tmp_ast = context.ast
                context.ast = [i["condition"]]
                condition = interpreter(context)
                context.ast = tmp_ast
                context.add_parent_scope(tmp)
                context.set_scope(cur)

                context.delete_scope(cur)
                cur = context.add_scope("__dowhile__")
                context.set_scope(cur)

                if response == "BREAK":
                    context.delete_scope(cur)
                    context.set_scope(tmp)
                    context.rem_parent_scope(tmp)
                    break

            context.set_scope(tmp)
            if cur in context.scope: context.delete_scope(cur)
            if tmp in context.parent_scopes: context.rem_parent_scope(tmp)

        elif i["type"] == "while":
            tmp_ast = context.ast
            context.ast = [i["condition"]]
            result_report[index] = interpreter(context)
            context.ast = tmp_ast

            cur = context.add_scope("__while__")
            tmp = context.get_scope()
            context.add_parent_scope(tmp)
            context.set_scope(cur)

            while result_report[index]["type"] == "BOOL" and result_report[index]["value"] == "TRUE":
                context.update()

                tmp_ast = context.ast
                context.ast = i["ast"]
                tmp_ret = context.current_return_type
                context.current_return_type = None
                response = interpreter(context)
                context.current_return_type = tmp_ret
                context.ast = tmp_ast

                if response != None:
                    if "type" in response:
                        if response["type"] != "NULL":
                            if context.return_state:
                                context.delete_scope(cur)
                                context.set_scope(tmp)
                                context.rem_parent_scope(tmp)
                                return response

                context.set_scope(tmp)
                context.rem_parent_scope(tmp)
                tmp_ast = context.ast
                context.ast = [i["condition"]]
                result_report[index] = interpreter(context)
                context.ast = tmp_ast
                context.set_scope(cur)
                context.add_parent_scope(tmp)

                context.delete_scope(cur)
                cur = context.add_scope("__while__")
                context.set_scope(cur)

                if response == "BREAK":
                    context.set_scope(tmp)
                    context.delete_scope(cur)
                    context.rem_parent_scope(tmp)
                    break

            context.set_scope(tmp)
            if cur in context.scope: context.delete_scope(cur)
            if tmp in context.parent_scopes: context.rem_parent_scope(tmp)

        elif i["type"] == "if":
            tmp_ast = context.ast
            context.ast = [i["condition"]]
            result_report[index] = interpreter(context)
            context.ast = tmp_ast

            cur = context.add_scope("__if__")
            tmp = context.get_scope()
            context.add_parent_scope(tmp)
            context.set_scope(cur)

            if result_report[index]["type"] == "BOOL" and result_report[index]["value"] == "TRUE":
                context.update()

                tmp_ast = context.ast
                context.ast = i["ast"]
                tmp_ret = context.current_return_type
                context.current_return_type = None
                response = interpreter(context)
                context.current_return_type = tmp_ret
                context.ast = tmp_ast

                if response in ["BREAK", "CONTINUE"]:
                    context.set_scope(tmp)
                    context.delete_scope(cur)
                    context.rem_parent_scope(tmp)
                    return response

                elif response != None:
                    if "type" in response:
                        if context.return_state:
                            context.set_scope(tmp)
                            context.delete_scope(cur)
                            context.rem_parent_scope(tmp)
                            return response

            context.set_scope(tmp)
            if cur in context.scope: context.delete_scope(cur)
            if tmp in context.parent_scopes: context.rem_parent_scope(tmp)

        elif i["type"] == "else if":
            if context.ast[index]["type"] in ["if", "else if"] and (index - 1 in result_report):
                if result_report[index - 1]["type"] == "BOOL" and result_report[index - 1]["value"] == "FALSE":
                    tmp_ast = context.ast
                    context.ast = [i["condition"]]
                    result_report[index] = interpreter(context)
                    context.ast = tmp_ast

                    cur = context.add_scope("__elseif__")
                    tmp = context.get_scope()
                    context.add_parent_scope(tmp)
                    context.set_scope(cur)

                    if result_report[index]["type"] == "BOOL" and result_report[index]["value"] == "TRUE":
                        context.update()

                        tmp_ast = context.ast
                        context.ast = i["ast"]
                        tmp_ret = context.current_return_type
                        context.current_return_type = None
                        response = interpreter(context)
                        context.current_return_type = tmp_ret
                        context.ast = tmp_ast

                        if response in ["BREAK", "CONTINUE"]:
                            context.set_scope(tmp)
                            context.delete_scope(cur)
                            context.rem_parent_scope(tmp)
                            return response

                        elif response != None:
                            if "type" in response:
                                if context.return_state:
                                    context.set_scope(tmp)
                                    context.delete_scope(cur)
                                    context.rem_parent_scope(tmp)
                                    return response

                    context.set_scope(tmp)
                    if cur in context.scope: context.delete_scope(cur)
                    if tmp in context.parent_scopes: context.rem_parent_scope(tmp)

                else:
                    result_report[index] = {"type": "BOOL", "value": "TRUE"}

            else:
                tools.error("couldn't find any statements", context.file)

        elif i["type"] == "else":
            cur = context.add_scope("__else__")
            tmp = context.get_scope()
            context.add_parent_scope(tmp)
            context.set_scope(cur)

            if context.ast[index - 1]["type"] in ["if", "else if", "while"] and (index - 1 in result_report):
                if result_report[index - 1]["type"] == "BOOL" and result_report[index - 1]["value"] == "FALSE":
                    context.update()

                    tmp_ast = context.ast
                    context.ast = i["ast"]
                    tmp_ret = context.current_return_type
                    context.current_return_type = None
                    response = interpreter(context)
                    context.current_return_type = tmp_ret
                    context.ast = tmp_ast
                    
                    if response in ["BREAK", "CONTINUE"]:
                        context.set_scope(tmp)
                        context.delete_scope(cur)
                        context.rem_parent_scope(tmp)
                        return response

                    elif response != None:
                        if "type" in response:
                            if context.return_state:
                                context.set_scope(tmp)
                                context.delete_scope(cur)
                                context.rem_parent_scope(tmp)
                                return response

                context.set_scope(tmp)
                if cur in context.scope: context.delete_scope(cur)
                if tmp in context.parent_scopes: context.rem_parent_scope(tmp)

            else:
                tools.error("couldn't find any statements", context.file)

        elif i["type"] == "using namespace":
            for j in context.get_current_elements():
                if i["name"] + "::" in j:
                    context.set(j.replace(i["name"] + "::", ""), context.get(j))

        elif i["type"] == "return":
            if context.is_main_file() and not context.is_in_function():
                tools.error("return can only be used in functions", context.file)

            if context.current_return_type == "VOID":
                if i["value"]["type"] != "NULL":
                    tools.error("can't return any value from void functions", context.file)

            tmp_ast = context.ast
            context.ast = [i["value"]]
            returned = interpreter(context)
            context.ast = tmp_ast

            if context.current_return_type != None and returned["type"] == "array_object" and context.current_return_type["type"] == "ARRAY_T":
                if returned["array_type"] != context.current_return_type["array_type"]:
                    tools.error("array type mismatch", context.file)

            elif returned["type"] != context.current_return_type and context.current_return_type != None and returned["type"] != "NULL":
                tmp_ast = context.ast
                context.ast = [{"type": "cast", "cast_type": context.current_return_type, "value": returned}]
                returned = interpreter(context)
                context.ast = tmp_ast

            context.return_state = True
            return returned

        elif i["type"] == "delete":
            context.delete(i["value"])

        elif i["type"] == "call":
            tmp_ast = context.ast
            context.ast = [i["value"]]
            name = interpreter(context)
            context.ast = tmp_ast
            tmp_var = context.get(name)

            tmp = []
            raws = []

            for j in i["args"]:
                tmp_ast = context.ast
                context.ast = [j]
                tmp.append(interpreter(context))
                context.ast = tmp_ast

            for index, j in enumerate(tmp_var["args"].values()):
                if "type" in j:
                    if j["type"] in ["ARRAY_T", "RAW_ARRAY_T"] and tmp[index]["type"] == "array_object":
                        if j["array_type"] != tmp[index]["array_type"] and j["array_type"] != None:
                            tools.error("array types mismatch", context.file)

                        if j["type"] == "RAW_ARRAY_T": raws.append(index)

                    elif j["type"] in ["STRUCT_T", "RAW_STRUCT_T"] and tmp[index]["type"] == "struct_object":
                        if j["value"] != tmp[index]["struct_type"] and j["value"] != None:
                            tools.error("struct types mismatch", context.file)

                        if j["type"] == "RAW_STRUCT_T": raws.append(index)

                    else:
                        tools.error("argument type mismatch for '" + name + "'", context.file)

                elif tmp[index]["type"] != j and tmp[index]["type"] not in ["NULL"]:
                    tmp_ast = context.ast
                    context.ast = [{"type": "cast", "cast_type": j, "value": tmp[index]}]
                    tmp[index] = interpreter(context)
                    context.ast = tmp_ast

            if len(i["args"]) != len(tmp_var["args"]):
                tools.error("argument count didn't match for" + " " + "'" + name + "'", context.file)

            if tmp_var["type"] == "libfunc":
                new_tmp = {}

                for index, j in enumerate(tmp):
                    new_tmp[list(tmp_var["args"].keys())[index]] = \
                        tools.rsx_to_py_value(j, context) if index not in raws else j

                enviroment = {
                    "args": new_tmp,
                    "args_pure": {j: tmp[index] for index, j in enumerate(tmp_var["args"])},
                    "file": context.file,
                    "scope": context.scope,
                    "context": context,
                    "include_folders": context.include_folders
                }

                returned = tmp_var["func"](enviroment)

                if not ("type" in tmp_var["return_type"] and tmp_var["return_type"]["type"] in ["RAW_STRUCT_T", "RAW_ARRAY_T"]):
                    returned = tools.py_to_rsx_value(returned)

                if "type" in tmp_var["return_type"] and tmp_var["return_type"]["type"] in ["ARRAY_T", "RAW_ARRAY_T"]:
                    if "array_type" in returned and returned["array_type"] not in [tmp_var["return_type"]["array_type"], "NULL"]:
                        tools.error("expected '" + str(tmp_var["return_type"]["array_type"]).lower() + " array' got '" + \
                            str(returned["array_type"]).lower() + " array' from: '" + name + "'", context.file)

                elif "type" in tmp_var["return_type"] and tmp_var["return_type"]["type"] in ["STRUCT_T", "RAW_STRUCT_T"]:
                    if returned["type"] != "struct_object" or (returned["struct_type"] != tmp_var["return_type"]["value"] and tmp_var["return_type"]["value"] != None):
                        tools.error("expected struct '" + str(tmp_var["return_type"]["value"]).lower() + "' got struct '" + \
                                    str(returned["struct_type"]).lower() + "' from: '" + name + "'", context.file)

                elif returned["type"] not in [tmp_var["return_type"], "NULL"]:
                    tools.error("expected '" + str(tmp_var["return_type"]).lower() + "' got '" + str(returned["type"]).lower() + "' from: '" + name + "'", context.file)

                if len(context.ast) == 1:
                    return returned

            elif tmp_var["type"] == "func":
                context.prepare_to_execute(name)

                for index, j in enumerate(tmp_var["args"].keys()):
                    if tmp[index]["type"] in [tmp_var["args"][j], "NULL"]:
                        tmp_ast = context.ast
                        gen_ast = {"type": "var", "name": j, "value_type": tmp[index]["type"], "value": tmp[index], "const": False}
                        context.ast = [gen_ast]
                        tmp_ret = context.current_return_type
                        context.current_return_type = None
                        interpreter(context)
                        context.current_return_type = tmp_ret
                        context.ast = tmp_ast

                    elif tmp_var["args"][j]["type"] == "ARRAY_T" and tmp[index]["type"] == "array_object" and tmp[index]["array_type"] == tmp_var["args"][j]["array_type"]:
                        context.set(j, tmp[index])

                    elif tmp[index]["type"] == "struct_object":
                        context.set(j, tmp[index])

                    else:
                        tools.error("argument type mismatch for '" + name + "'", context.file)

                if "parent_object" in tmp_var:
                    curr = tmp_var["parent_object"]["scope"]["public"]

                    for i in curr:
                        context.set(i, curr[i])

                returned = interpreter(context)

                if "parent_object" in tmp_var:
                    curr = tmp_var["parent_object"]["scope"]["public"]

                    for i in curr:
                        tmp_var["parent_object"]["scope"]["public"][i] = context.get(i)

                context.end_execute()
                context.return_state = False

                if returned == None:
                    returned = {"type": "NULL", "value": "NULL"}

                if returned == {"type": "VOID", "value": "VOID"}:
                    returned = {"type": "NULL", "value": "NULL"}

                if returned in ["BREAK", "CONTINUE"]:
                    tools.error("'break' or 'continue' keyword used in wrong place", context.file)

                if returned["type"] not in [tmp_var["return_type"], "NULL"] and not \
                    (returned["type"] == "array_object" and tmp_var["return_type"]["type"] == "ARRAY_T" and returned["array_type"] == tmp_var["return_type"]["array_type"]):
                    tools.error("expected '" + str(tmp_var["return_type"]).lower() + "' got '" + str(returned["type"]).lower() + "' from: '" + name + "'", context.file)

                if len(context.ast) == 1:
                    return returned

            else:
                tools.error("expected a function, '" + name + "' is not a function", context.file)

        else:
            if "type" in i["type"]:
                tools.warning("undeclared '" + i["type"]["type"] + "' type was passed", context.file)

            else:
                tools.warning("undeclared '" + i["type"] + "' was passed", context.file)

    if context.is_base() and context.is_main_file():
        if context.program_state():
            if not context.is_exists("main"):
                tools.error("no entry point", context.file)

            if context.get("main")["return_type"] != "INT":
                tools.error("no entry point", context.file)

            if (context.get("main")["args"] != {"args": {"type": "ARRAY_T", "array_type": "STRING", "size": None}} and context.get("main")["args"] != {}):
                tools.error("no entry point", context.file)

            if error_code != None:
                if error_code != "0":
                    print(f"program exit with code {error_code}")

    else:
        if context.is_in_function() and context.current_return_type != None and context.current_return_type != "VOID":
            tools.error("non-void functions should return a value", context.file)

help = """
R# Interpreter - RSX

- help: for this page
- version: for the version of RSX
- run [file] [args]: for running a RSX program
- build [file] [args]: for running a RSX program

file for run/build commands: file path (example: main.rsx)
args for run/build commands: -[timeit/console/noconsole/gettok/getast/bytecode]=[true/false] (example: -timeit=true)
                             -[I/rmI]=[library_path] (example: -Iinclude)
"""

def main():
    argv = sys.argv
    start_time = time.time()
    version = tools.get_version()

    include_folders = ["./", f"{tools.get_dir()}/include/"]
    if sys.platform == "win32" and tools.is_compiled(): include_folders.append("C:\\RSX\\include\\")
    console = True
    bytecode = True
    timeit = False
    get_tokens = False
    get_ast = False
    mode = None
    file = None
    program_args = []

    for i in argv[1:]:
        if i[0] == "-":
            arg = i[1:].split("=")

            if arg[0][0] == "I":
                include_folders.insert(0, arg[0][1:])

            elif arg[0][:3] == "rmI":
                include_folders.pop(include_folders.index(arg[0][3:]))

            elif arg[0] == "timeit":
                if arg[1] == "true": timeit = True
                if arg[1] == "false": timeit = False

            elif arg[0] == "noconsole":
                if arg[1] == "true": console = False
                if arg[1] == "false": console = True

            elif arg[0] == "console":
                if arg[1] == "true": console = True
                if arg[1] == "false": console = False

            elif arg[0] == "gettok":
                if arg[1] == "true": get_tokens = True
                if arg[1] == "false": get_tokens = False

            elif arg[0] == "getast":
                if arg[1] == "true": get_ast = True
                if arg[1] == "false": get_ast = False

            elif arg[0] == "bytecode":
                if arg[1] == "true": bytecode = True
                if arg[1] == "false": bytecode = False

            else:
                tools.error(f"unknown operation '{i}'", file)

        elif i in ["version", "run", "build", "format", "help"]:
            if mode == None: mode = i
            else: tools.error("mode already setted", file)

        else:
            if file == None: file = i
            program_args.append(i)

    if mode == None: mode = "run"
    if file == None and mode not in ["version", "help", "format"]: tools.error("no input files", "rsx", "fatal error", True)
    if file != None and mode not in ["version", "help", "format"]:
        if not os.path.isfile(file):
            tools.error("file not found", "rsx", "fatal error", True)

    if mode == "run":
        if os.path.splitext(file)[1] not in [".rsx", ".rsxd", ".rsxc", ".rsxp"]:
            tools.error(f"invalid extension: '{os.path.splitext(file)[1]}'", file)

        ast = None

        if os.path.splitext(file)[1] == ".rsxc":
            with open(os.path.splitext(file)[0] + ".rsxc", "rb") as f:
                content = pickle.loads(f.read())

                if "version" not in content:
                    tools.error("broken bytecode file", file)

                if content["version"] != version:
                    tools.error("bytecode version didn't match [bytecode: " + content["version"] + f", current: {version}]", file)

                ast = content["ast"]
                custom_types = content["custom_types"]

        else:
            file_content = tools.read_file(file)

            if os.path.splitext(file)[0] + ".rsxc" in os.listdir() and bytecode:
                with open(os.path.splitext(file)[0] + ".rsxc", "rb") as f:
                    content = tools.load_bytecode(f.read())

                    if "version" in content:
                        if content["version"] == version:
                            if content["file_content"] == hashlib.sha256(file_content.encode()).digest():
                                ast = content["ast"]
                                custom_types = content["custom_types"]

            if ast == None:
                tokens = lexer(file_content, file)
                if get_tokens: print(tokens)
                custom_types = []
                ast = parser(tokens, file, custom_types)

                if bytecode:
                    with open(os.path.splitext(file)[0] + ".rsxc", "wb") as f: f.write(tools.dump_bytecode(ast, custom_types, file_content))

        if get_ast: print(ast)
        context = Context(ast, file)
        context.custom_types = custom_types
        context.version = version
        context.include_folders = include_folders
        context.args = program_args
        interpreter(context)

    elif mode == "build":
        if os.path.splitext(file)[1] not in [".rsx", ".rsxd", ".rsxc", ".rsxp"]:
            tools.error(f"invalid extension: '{os.path.splitext(file)[1]}'", file)

        context = tools.auto_include(
            file = file,
            include_folders = include_folders
        )

        if get_tokens: print(tokens)
        if get_ast: print(ast)

        builder.build_program(
            console = console,
            context = context
        )

    elif mode == "format":
        content = tools.read_file(file)

        with open(file, "w") as f:
            f.write(tools.tokens_to_string(lexer(content, file)))

    elif mode == "version":
        tools.set_text_attr(12)
        print(f"RSX {version}", flush = True)
        tools.set_text_attr(7)

    elif mode == "help":
        print(help)

    else:
        tools.error("unknown error", file)

    if timeit:
        print("finished in:", time.time() - start_time)

    return 0

if __name__ == "__main__":
    try: sys.exit(main())
    except KeyboardInterrupt: ...