import sys, os, time
import platform

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
    import rsxpy.preprocessor as preprocessor

except ImportError:
    sys.path.append(os.path.split(os.getcwd())[0])

    import rsxpy.tools as tools
    import rsxpy.std as std
    import rsxpy.builder as builder
    import rsxpy.preprocessor as preprocessor

keywords = {
    "auto": "AUTO",
    "void": "VOID",
    "bool": "BOOL",
    "int": "INT",
    "float": "FLOAT",
    "string": "STRING",
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
    # "class": "CLASS",
    # "public": "PUBLIC",
    # "private": "PRIVATE",
    # "protected": "PROTECTED",
    # "try": "TRY",
    # "throw": "THROW",
    # "catch": "CATCH",
    "const": "CONST",
    "using": "USING",
    # "struct": "STRUCT",
    # "new": "NEW",
    "delete": "DELETE",
    "do": "DO",
    "namespace": "NAMESPACE",
    "break": "BREAK",
    "continue": "CONTINUE",
    "include": "INCLUDE"
}

constants = {
    "true": "BOOL",
    "false": "BOOL"
}

operators = {
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
    row, col = 1, 1

    lines[file] = data.split("\n")

    def error(message, file = file, type = "error", terminated = False):
        print(f"{file}:{row}:{col}:", end = " ", flush = True)
        tools.set_text_attr(12)
        print(f"{type}:", end = " ", flush = True)
        tools.set_text_attr(7)
        print(message, end = "\n", flush = True)
        if terminated: print("program terminated.")
        sys.exit(-1)

    def warning(message, file = file, type = "warning"):
        print(f"{file}:{row}:{col}:", end = " ", flush = True)
        tools.set_text_attr(13)
        print(f"{type}:", end = " ", flush = True)
        tools.set_text_attr(7)
        print(message, end = "\n", flush = True)

    def get(index, data = data):
        try: return data[index]
        except: return ""

    last_char = ""
    last_pos = 0

    while len(data) > pos:
        temp = 0

        for i in data[last_pos:pos]:
            if row - last_row - temp <= 0:
                if i in "\r\n":
                    temp += 1
                    row += 1
                    col = 0

            else:
                if i in "\r\n":
                    col = 0

            col += 1

        last_row = row
        last_pos = pos

        while char.isspace():
            pos += 1
            col += 1
            char = get(pos)

        if char.isalpha() or char in ["_"]:
            id_str = ""

            while char.isalnum() or char in [".", "_"] or (char == ":" and (get(pos + 1) == ":" or get(pos - 1) == ":") and get(pos + 2) != ":"):
                if char == ":" and id_str == "default": break
                id_str += char
                pos += 1
                char = get(pos)

            if id_str in keywords:
                if id_str in constants:
                    tokens.append({"value": constants[id_str], "row": row, "col": col})

                tokens.append({"value": keywords[id_str], "row": row, "col": col})

            else:
                tokens.append({"value": "IDENTIFIER", "row": row, "col": col})
                tokens.append({"value": id_str, "row": row, "col": col})

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
                    tokens.append({"value": "FLOAT", "row": row, "col": col})

                    if num_str.count("f") not in [0, 1]:
                        error("more than one 'f' found in a float")

                    num_str = num_str.replace("f", "")

                elif num_str.count(".") == 0:
                    tokens.append({"value": "INT", "row": row, "col": col})

                    if num_str.count("f") != 0:
                        error("used 'f' in an integer value")

                else:
                    error("more than one '.' found in a value")

                tokens.append({"value": num_str, "row": row, "col": col})
            
            elif base in ["hexadecimal", "binary", "octal"]:
                base_int = int(base.replace("hexadecimal", "16").replace("binary", "2").replace("octal", "8"))
                tokens.append({"value": "INT", "row": row, "col": col})
                tokens.append({"value": str(int(num_str, base_int)), "row": row, "col": col})

            else:
                error("unknown number system")

        elif char in ["\"", "'"]:
            op = char
            pos += 1
            char = get(pos)
            string = ""

            while char and char != op:
                if char in "\r\n":
                    error("unterminated string literal")

                if char == "\\" and get(pos + 1) == "\"":
                    string += "\""
                    pos += 2
                    char = get(pos)

                if char == "\\" and get(pos + 1) == "\'":
                    string += "\'"
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

            tokens.append({"value": "STRING", "row": row, "col": col})
            tokens.append({"value": string.replace("mavish", "♥ mavish ♥"), "row": row, "col": col})
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
                    tokens.append({"value": operators[char], "row": row, "col": col})
                    pos += 1
                    char = get(pos)

            elif char in operators:
                if tokens[len(tokens) - 1]["value"] in ["GREATER", "LESS", "NOT", "EQUALS", "PLUS", "MINUS", "ASTERISK", "SLASH", "MODULUS"] and char == "=" and last_char != " ":
                    tokens.append({"value": tokens[len(tokens) - 1]["value"] + operators[char], "row": row, "col": col})
                    tokens.pop(len(tokens) - 2)

                elif tokens[len(tokens) - 1]["value"] == "MINUS" and char == ">" and last_char != " ":
                    tokens.append({"value": "ARROW", "row": row, "col": col})
                    tokens.pop(len(tokens) - 2)

                elif tokens[len(tokens) - 1]["value"] in ["GREATER", "LESS"] and char in [">", "<"]:
                    if char == "<": tokens.append({"value": "BITWISELEFT", "row": row, "col": col})
                    elif char == ">": tokens.append({"value": "BITWISERIGHT", "row": row, "col": col})
                    tokens.pop(len(tokens) - 2)

                elif char == last_char == "|":
                    tokens.append({"value": "OR", "row": row, "col": col})
                    tokens.pop(len(tokens) - 2)

                elif char == "|":
                    tokens.append({"value": "BITWISEOR", "row": row, "col": col})

                elif char == last_char == "&":
                    tokens.append({"value": "AND", "row": row, "col": col})
                    tokens.pop(len(tokens) - 2)

                elif char == "&":
                    tokens.append({"value": "BITWISEAND", "row": row, "col": col})

                elif char == "~":
                    tokens.append({"value": "BITWISENOT", "row": row, "col": col})

                elif char == "^":
                    tokens.append({"value": "BITWISEXOR", "row": row, "col": col})

                elif char == "." and get(pos + 1) == "." and get(pos + 2) == "." and get(pos + 3) != ".":
                    tokens.append({"value": "THREEDOT", "row": row, "col": col})
                    pos += 2

                elif char in ["-", "+"] and get(pos + 1) in ["-", "+"] and char == get(pos + 1) and tokens[len(tokens) - 2]["value"] == "IDENTIFIER":
                    tokens.append({"value": char.replace("+", "POSTINCREMENT").replace("-", "POSTDECREMENT"), "row": row, "col": col})
                    pos += 1

                elif char in ["-", "+"] and get(pos + 1) in ["-", "+"] and char == get(pos + 1):
                    tokens.append({"value": char.replace("+", "PREINCREMENT").replace("-", "PREDECREMENT"), "row": row, "col": col})
                    pos += 1

                elif char in ["-", "+"] and get(pos + 1) not in [" ", char]:
                    tokens.append({"value": char.replace("-", "NEGATIVE").replace("+", "POSITIVE"), "row": row, "col": col})

                else:
                    tokens.append({"value": operators[char], "row": row, "col": col})

                pos += 1
                char = get(pos)

                if char in "\r\n":
                    row += 1
                    pos += 1
                    char = get(pos)

            else:
                error(f"unknown operator '{char}'")

            last_char = char
    
    return tokens

def parser(tokens, file):
    ast = []
    pos = 0

    last_token = {"token": None, "value": None}

    types = ["BOOL", "INT", "FLOAT", "STRING"]
    operators = ["PLUS", "MINUS", "SLASH", "ASTERISK", "MODULUS", "EQUALS" * 2, "NOT" + "EQUALS", "GREATER", "GREATER" + "EQUALS", "LESS", "LESS" + "EQUALS", "AND", "OR", "NOT", "BITWISEOR", "BITWISEXOR", "BITWISEAND", "BITWISENOT", "BITWISELEFT", "BITWISERIGHT"]
    assignment_operators = ["EQUALS", "PLUS" + "EQUALS", "MINUS" + "EQUALS", "ASTERISK" + "EQUALS", "SLASH" + "EQUALS", "MODULUS" + "EQUALS", "BITWISEOR" + "EQUALS", "BITWISEXOR" + "EQUALS", "BITWISEAND" + "EQUALS", "BITWISELEFT" + "EQUALS", "BITWISERIGHT" + "EQUALS"]

    def error(message = None, file = file, type = "error", terminated = False):
        row, col = None, None

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
                        args.append(parser(temp_tokens, file)[0])
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
                        if arg_type == "ARRAY":
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
                    arg_type = "ARRAY"

                else:
                    current_pos += 1

            elif get(current_pos) == "IDENTIFIER":
                arg_name = get(current_pos + 1)
                current_pos += 2

            elif get(current_pos) == "THREEDOT":
                var_arg = True
                current_pos += 1

            elif get(current_pos) == "COMMA":
                if arg_name != None and arg_type != None:
                    if arg_type == "ARRAY":
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

        return parser(temp_tokens, file), current_pos + 1

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
            index = parser(temp_tokens, file)[0]
            temp_pos += 1

        return index, temp_pos

    def collect_tokens(temp_pos, stop_tokens = ["SEMICOLON"] + operators):
        temp_tokens = []
        ignore = 0
        ignore_curly = 0

        while True:
            if get(temp_pos) in stop_tokens:
                if ignore == 0 and ignore_curly == 0: break
                if get(temp_pos) == "RPAREN": ignore -= 1
                if get(temp_pos) == "LPAREN": ignore += 1
                if get(temp_pos) == "RCURLYBRACKET": ignore_curly -= 1
                if get(temp_pos) == "LCURLYBRACKET": ignore_curly += 1

                temp_tokens.append(get(temp_pos, True))
                temp_pos += 1

            elif get(temp_pos) == "COMMA":
                if ignore == 0 and ignore_curly == 0: break
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
        result = parser(temp_tokens, file)[0]
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
        if last_token["token"] == None or get(pos) != last_token["token"]:
            last_token = {"token": get(pos), "value": 0}

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
                    pos += 1

        elif get(pos) == "NOT":
            temp_tokens, pos = collect_tokens(pos + 1)
            ast.append({"type": "not", "value": parser(temp_tokens, file)[0]})
            if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) in ["NEGATIVE", "POSITIVE"]:
            type = get(pos)
            temp_tokens, pos = collect_tokens(pos + 1)
            ast.append({"type": type.replace("NEGATIVE", "neg").replace("POSITIVE", "pos"), "value": parser(temp_tokens, file)[0]})
            if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) in ["PREINCREMENT", "PREDECREMENT"]:
            type = get(pos)
            temp_tokens, pos = collect_tokens(pos + 1)
            ast.append({"type": type.replace("PREINCREMENT", "increment").replace("PREDECREMENT", "decrement"), "value": parser(temp_tokens, file)[0], "pre": True})
            if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) == "BITWISENOT":
            temp_tokens, pos = collect_tokens(pos + 1)
            ast.append({"type": "bitwise not", "value": parser(temp_tokens, file)[0]})
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
                ast.append({"type": "for", "ast": temp_ast, "init": parser(temp_tokens[0], file), "condition": parser(temp_tokens[1], file)[0], "update": parser(temp_tokens[2], file)})

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
                ast.append({"type": name, "ast": temp_ast, "condition": parser(condition_tokens, file)[0]})

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
            ast.append({"type": "or", "left": left, "right": parser(temp_tokens, file)[0]})
            if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) == "AND":
            left = ast[len(ast) - 1]
            ast.pop(len(ast) - 1)
            temp_tokens, pos = collect_tokens(pos + 1, stop_tokens = ["OR", "AND", "SEMICOLON", "RPAREN"])
            ast.append({"type": "and", "left": left, "right": parser(temp_tokens, file)[0]})
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

                    elif get(condition_pos) in ["LCURLYBRACKET"]:
                        error("expected ')'")

                    else:
                        condition_tokens.append(get(condition_pos, True))
                        condition_pos += 1

                pos = condition_pos + 1
                condition_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
                ast.append({"type": "do while", "ast": temp_ast, "condition": parser(condition_tokens, file)[0]})

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
                    values.append(parser(temp_tokens, file)[0])

                    if get(pos) == "COMMA":
                        pos += 1

                    else:
                        break

                if get(pos) == "RCURLYBRACKET":
                    pos += 1

                    if get(pos) == "SEMICOLON":
                        pos += 1

                ast.append({"type": "ARRAY", "array_type": None, "size": None, "value": values})

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
                        if current_case != None: cases[current_case]["ast"] = parser(cases[current_case]["ast"], file)
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
                            cases[current_case]["value"] = parser(cases[current_case]["value"], file)[0]
                            pos += 1

                    else:
                        if current_case == None: error("couldn't find any case")
                        cases[current_case]["ast"].append(get(pos, True))
                        pos += 1

                if current_case != None: cases[current_case]["ast"] = parser(cases[current_case]["ast"], file)

                if get(pos) == "RCURLYBRACKET":
                    ast.append({"type": "switch", "value": value, "cases": cases})
                    pos += 1

        elif get(pos) == "LPAREN" and get(pos + 1) in ["STRING", "BOOL", "INT", "FLOAT"] and get(pos + 2) == "RPAREN":
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
            ast.append({"type": "cast", "cast_type": type, "value": parser(temp_tokens, file)[0]})

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
            ast.append({"type": type, "left": ast[len(ast) - 1], "right": parser(temp_tokens, file)[0]})
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
                ast.append({"type": "return", "value": parser(temp_tokens, file)[0]})
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

        elif get(pos) == "IDENTIFIER":
            last = None

            if len(ast) != 0:
                last = ast[len(ast) - 1]

            if get(pos + 2) in assignment_operators:
                type = get(pos + 2)
                name = get(pos + 1)
                temp_tokens, pos = collect_tokens(pos + 3, stop_tokens = ["SEMICOLON"])
                value = parser(temp_tokens, file)[0]

                if type == "PLUS" + "EQUALS": value = {"type": "add", "left": last, "right": value}
                if type == "MINUS" + "EQUALS": value = {"type": "sub", "left": last, "right": value}
                if type == "ASTERISK" + "EQUALS": value = {"type": "mul", "left": last, "right": value}
                if type == "SLASH" + "EQUALS": value = {"type": "div", "left": last, "right": value}
                if type == "BITWISEOR" + "EQUALS": value = {"type": "bitwise or", "left": last, "right": value}
                if type == "BITWISEXOR" + "EQUALS": value = {"type": "bitwise xor", "left": last, "right": value}
                if type == "BITWISEAND" + "EQUALS": value = {"type": "bitwise and", "left": last, "right": value}
                if type == "BITWISELEFT" + "EQUALS": value = {"type": "bitwise left", "left": last, "right": value}
                if type == "BITWISRIGHT" + "EQUALS": value = {"type": "bitwise right", "left": last, "right": value}

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
                value = parser(temp_tokens, file)[0]

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
                ast.append(parser(temp_tokens, file)[0])
                pos += 1
                
                if get(pos) == "SEMICOLON":
                    pos += 1

        elif get(pos) in ["VOID", "AUTO", "CONST"] + types:
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

                if get(pos) in types:
                    type = get(pos)
                    size, array_type = None, None

                    if get(pos + 1) not in ["IDENTIFIER", "LPAREN", "COMMA", "LBRACKET"]:
                        ast.append({"type": get(pos), "value": get(pos + 1)})
                        if get(pos + 2) == "SEMICOLON": pos += 3
                        else: pos += 2

                    else:
                        if get(pos + 1) == "LBRACKET":
                            temp_size, pos = get_index(pos + 2)
                            if temp_size["type"] != "NULL": size = temp_size
                            array_type = type
                            type = "ARRAY"

                        else:
                            pos += 1

                        type_end_pos = pos

                        if get(pos) == "IDENTIFIER":
                            name = get(pos + 1)

                            if get(pos + 2) == "LPAREN":
                                args, pos, var_arg = get_def_args(pos + 2)

                                if size != None: error("size must be none")

                                if get(pos) == "SEMICOLON":
                                    ast.append({"type": "func", "return_type": type, "array_type": array_type, "const": const, "name": name, "args": args, "ast": None, "var_arg": var_arg})
                                    pos += 1

                                else:
                                    temp_ast, pos = get_func_ast(pos)
                                    ast.append({"type": "func", "return_type": type, "array_type": array_type, "const": const, "name": name, "args": args, "ast": temp_ast, "var_arg": var_arg})

                            elif get(pos + 2) == "EQUALS":
                                name = get(pos + 1)
                                temp_tokens, pos = collect_tokens(pos + 3, stop_tokens = ["SEMICOLON"])
                                ast.append({"type": "var", "value_type": type, "array_type": array_type, "size": size, "name": name, "value": parser(temp_tokens, file)[0], "const": const})
                                
                                if get(pos) in ["SEMICOLON", "COMMA"]:
                                    if get(pos) == "COMMA":
                                        for index, i in enumerate(tokens[first_pos:type_end_pos]):
                                            tokens.insert(pos + index + 1, i)

                                    pos += 1

                            elif get(pos + 2) in ["SEMICOLON", "COMMA"]:
                                if get(pos + 2) == "COMMA":
                                    for index, i in enumerate(tokens[first_pos:type_end_pos]):
                                        tokens.insert(pos + index + 3, i)

                                    pos += 3

                                else:
                                    pos += 2

                                ast.append({"type": "var", "value_type": type, "array_type": array_type, "size": size, "name": name, "value": None, "const": const})
                                if get(pos) == "SEMICOLON": pos += 1

                            else:
                                error("expected ';'")
                
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
                "__OSNAME__": {"type": "var", "value": {"type": "STRING", "value": os.name}, "const": True},
                "__MACHINE__": {"type": "var", "value": {"type": "STRING", "value": platform.machine()}, "const": True},
                "__SYSTEM__": {"type": "var", "value": {"type": "STRING", "value": platform.system()}, "const": True},
                "__ARCH__": {"type": "var", "value": {"type": "STRING", "value": platform.architecture()[0]}, "const": True},
                "__PLATFORM__": {"type": "var", "value": {"type": "STRING", "value": sys.platform}, "const": True},
                "__NODE__": {"type": "var", "value": {"type": "STRING", "value": platform.node()}, "const": True}
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
        self.recorded = {}
        self.program_state_var = True
        self.is_thread = False
        self.actual_context = None
        self.is_compiled_var = False
        self.parent_scopes = []
        self.recursions = {}
        self.recursion_limit = 1000

    def update(self):
        ...

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

    def is_exists(self, key):
        tmp = self.scope["global"].copy()

        if self.current_scope != "global":
            tmp.update(self.scope[self.current_scope])

        return key in tmp

    def set(self, key, value, force = False, record_pass = False):
        if not record_pass and self.current_scope == "global":
            if len(self.recorded) != 0:
                for i in self.recorded:
                    self.recorded[i][key] = value

        if force:
            self.scope[self.current_scope][key] = value
            return

        tmp = self.parent_scopes.copy()
        tmp.reverse()

        if self.is_thread:
            if key in self.actual_context.scope["global"] and key not in self.scope[self.current_scope]:
                found = False

                for i in tmp:
                    if key in self.scope[i]:
                        found = True

                if not found:
                    self.actual_context.scope["global"][key] = value
                    return

        if key in self.scope[self.current_scope]:
            self.scope[self.current_scope][key] = value
            return

        elif key in self.scope["global"]:
            self.scope["global"][key] = value
            return
        
        for i in tmp:
            if key in self.scope[i]:
                self.scope[i][key] = value
                return

        self.scope[self.current_scope][key] = value

    def get(self, key):
        if self.is_exists(key):
            if self.current_scope != "global":
                if key in self.scope[self.current_scope]:
                    return self.scope[self.current_scope][key]

            if self.is_thread:
                if self.actual_context.scope["global"][key] != self.scope["global"][key]:
                    self.scope["global"][key] = self.actual_context.scope["global"][key]

            return self.scope["global"][key]

        else:
            if len(self.parent_scopes) != 0:
                tmp_scope = self.current_scope
                self.current_scope = self.parent_scopes[len(self.parent_scopes) - 1]
                tmp = self.parent_scopes.copy()
                self.parent_scopes.pop(len(self.parent_scopes) - 1)
                res = self.get(key)
                self.parent_scopes = tmp
                self.current_scope = tmp_scope
                return res

            else:
                tools.error(f"'{key}' was not declared in this scope", self.file)

    def delete(self, key, record_pass = False):
        if self.is_exists(key):
            if not record_pass and self.current_scope == "global":
                if len(self.recorded) != 0:
                    for i in self.recorded:
                        del self.recorded[i][key]

            if self.current_scope != "global":
                if key in self.scope[self.current_scope]:
                    del self.scope[self.current_scope][key]
                    return

            if self.is_thread:
                if key in self.actual_context.scope["global"]:
                    del self.actual_context.scope["global"][key]

            del self.scope["global"][key]

        else:
            tools.error(f"'{key}' was not declared in this scope", self.file)

    def is_main_file(self):
        return self.main_file == self.file

    def is_in_function(self):
        return self.current_scope != "global"

    def prepare_to_execute(self, key):
        name = key.split(">")[0]

        if name in self.recursions:
            self.recursions[name] += 1

            if self.recursions[name] >= self.recursion_limit:
                tools.error(f"recursion limit exceeded: '{name}'", self.file)

        else:
            self.recursions[name] = 1

        tmp = self.current_scope
        self.current_scope = self.add_scope(key)
        self.cache[self.current_scope] = {"ast": self.ast, "current_return_type": self.current_return_type, "current_array_type": self.current_array_type, "current_scope": tmp, "parent_scopes": self.parent_scopes}
        self.ast = self.get(key)["ast"]
        self.parent_scopes = []
        self.current_return_type = self.get(key)["return_type"]
        self.current_array_type = self.get(key)["array_type"]
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
        self.ast, self.current_return_type, self.current_array_type = self.cache[self.current_scope]["ast"], self.cache[self.current_scope]["current_return_type"], self.cache[self.current_scope]["current_array_type"]
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

    def record(self):
        self.recorded[len(self.recorded)] = {}
        return len(self.recorded) - 1

    def end_record(self, num):
        tmp = self.recorded[num].copy()
        del self.recorded[num]
        return tmp

def interpreter(context: Context):
    result_report = {}

    for index, i in enumerate(context.get_ast()):
        context.update()
        if isinstance(i, str) or i == None: tools.error(f"unknown exception at runtime (probably caused by an unhandled parser exception)", f"{context.file}:<{i}>")
        if i["type"] == "func":
            if context.current_scope != "global":
                tools.error("a function-definition is not allowed here before", context.file)

            if context.is_exists(i["name"]):
                tools.error("can't overload a function", context.file)

            if i["return_type"] not in ["VOID", "FLOAT", "INT", "STRING", "BOOL", "ARRAY"]:
                tools.error("unknown type for a function: '" + i["return_type"].lower() + "'", context.file)

            context.set(i["name"], {"type": "func", "return_type": i["return_type"], "array_type": i["array_type"], "args": i["args"], "ast": i["ast"], "const": False})
            context.add_scope(i["name"])

            if i["name"] == "main" and i["return_type"] == "INT" and (i["args"] == {"args": {"type": "ARRAY", "array_type": "STRING", "size": None}} or i["args"] == {}):
                if context.is_main_file() and not context.is_in_function() and context.program_state:
                    context.prepare_to_execute("main")

                    if i["args"] == {"args": {"type": "ARRAY", "array_type": "STRING", "size": None}}:
                        elements = []

                        for j in context.args:
                            elements.append({"type": "STRING", "value": j})

                        value = {"type": "ARRAY", "array_type": "STRING", "value": elements}
                        __args_func = lambda environ: len(environ["context"].get("args")["value"]["value"])
                        context.set("args.length", {"type": "libfunc", "args": {}, "return_type": "INT", "func": __args_func, "const": True}, True)
                        context.set("args", {"type": "var", "value": value.copy(), "const": True}, True)

                    error_code = interpreter(context)
                    context.end_execute()
                    
                    if error_code in ["BREAK", "CONTINUE"]:
                        tools.error("can't use '" + error_code.lower() + "' here", context.file)

                    elif error_code["type"] == "NULL":
                        tools.error("non-void functions should return a value", context.file)

                    else:
                        if error_code["type"] == "INT":
                            error_code = error_code["value"]

        elif i["type"] == "namespace":
            tmp = context.ast
            context.ast = i["ast"]
            num = context.record()
            interpreter(context)
            tmp_scope = context.end_record(num)
            context.ast = tmp
            
            for j in tmp_scope:
                context.set(i["name"] + "::" + j, tmp_scope[j])
                context.delete(j)

        elif i["type"] in ["increment", "decrement"]:
            if i["value"]["type"] != "IDENTIFIER":
                tools.error("not implemented", context.file)

            value = i["value"]["value"]

            if context.get(value)["const"]:
                tools.error("assignment of read-only variable '" + value + "'", context.file)

            if context.get(value)["value"]["type"] in ["FLOAT", "INT"]:
                temp = context.get(value)["value"]

                if context.get(value)["value"]["type"] == "INT":
                    context.set(value,
                        {"type": "var", "value": {"type": context.get(value)["value"]["type"], "value": str(int(context.get(value)["value"]["value"]) + (1 if i["type"] == "increment" else -1))}, "const": False})

                elif context.get(value)["value"]["type"] == "FLOAT":
                    context.set(value,
                        {"type": "var", "value": {"type": context.get(value)["value"]["type"], "value": str(float(context.get(value)["value"]["value"].lower().replace("f", "")) + (1 if i["type"] == "increment" else -1)) + "f"}, "const": False})

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
                
        elif i["type"] == "var":
            if i["value"] == None:
                i["value"] = {"type": i["value_type"], "array_type": i["array_type"], "size": i["size"], "value": None}

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
                if context.is_exists(i["name"]):
                    tools.error("redefinition of '" + i["name"] + "'", context.file)

                else:
                    if i["value_type"] == "AUTO":
                        if value == None:
                            tools.error("required a value for auto type", context.file)

                    elif value["type"] != i["value_type"] and value["type"] != "NULL":
                        tmp_ast = context.ast
                        context.ast = [{"type": "cast", "cast_type": i["value_type"], "value": value}]
                        value = interpreter(context)
                        context.ast = tmp_ast

                    elif i["value_type"] == "ARRAY":
                        if i["size"] != None:
                            tmp_ast = context.ast
                            context.ast = [i["size"]]
                            size = interpreter(context)
                            context.ast = tmp_ast

                            tmp_ast = context.ast
                            context.ast = [{"type": i["array_type"], "value": None}]
                            temp_type = interpreter(context)
                            context.ast = tmp_ast

                            if size["type"] == "INT":
                                elements = [temp_type] * int(size["value"])

                            else:
                                tools.error("size must be an integer", context.file)

                        else:
                            elements = []

                        temp = value["value"]

                        if temp == None:
                            temp = []

                        for temp_index, j in enumerate(temp):
                            if i["size"] != None:
                                if temp_index >= int(size["value"]):
                                    tools.error("'array' index out of range", context.file)

                            else:
                                elements.append(None)

                            tmp_ast = context.ast
                            context.ast = [j]
                            element = interpreter(context)
                            context.ast = tmp_ast

                            if element["type"] != i["array_type"]:
                                tmp_ast = context.ast
                                context.ast = [{"type": "cast", "cast_type": i["array_type"], "value": element}]
                                element = interpreter(context)
                                context.ast = tmp_ast

                            elements[temp_index] = element

                        name = i["name"]
                        temp_globals = {}
                        value = {"type": "ARRAY", "array_type": i["array_type"], "size": i["size"], "value": elements}
                        exec(f"__{name}_func = lambda environ: len(environ[\"context\"].get(\"{name}\")[\"value\"][\"value\"])", temp_globals)
                        context.set(i["name"] + ".length", {"type": "libfunc", "args": {}, "return_type": "INT", "func": temp_globals[f"__{name}_func"], "const": i["const"]}, True)

                    context.set(i["name"], {"type": "var", "value": value.copy(), "const": i["const"]}, True)

        elif i["type"] == "include":
            for lib in i["libs"]:
                if context.is_included(lib) and not context.is_compiled():
                    tools.warning("trying to include '" + lib + "' twice", context.file)
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
                            context.set((lib if i["special_namespace"] == None else i["special_namespace"]) + "::" + j, tmp[j])
                            context.delete(j)
                    
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

                    if ast is None:
                        ast = parser(lexer(preprocessor.preprocessor(tools.read_file(file_path), context.include_folders), file_path), file_path)

                        with open(os.path.splitext(file_path)[0] + ".rsxc", "wb") as file:
                            file.write(tools.dump_bytecode(ast, file_content))

                    context.prepare_to_include(ast, file_path)
                    num = context.record()
                    tmp_ret = context.current_return_type
                    context.current_return_type = None
                    tmp_parent_scopes = context.parent_scopes
                    context.parent_scopes = []
                    interpreter(context)
                    context.parent_scopes = tmp_parent_scopes
                    context.current_return_type = tmp_ret
                    tmp = context.end_record(num)
                    context.end_include()

                    if i["namespace"]:
                        for j in tmp:
                            context.set((lib if i["special_namespace"] == None else i["special_namespace"]) + "::" + j, tmp[j])
                            context.delete(j)

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
                                        context.delete(j)
                                        continue

                            context.set(j, tmp[j])

        elif i["type"] == "ARRAY":
            if i["value"] == None:
                return {"type": "ARRAY", "array_type": i["array_type"], "size": i["size"], "value": []}

            else:
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

                return {"type": "ARRAY", "array_type": type, "size": len(elements), "value": elements}

        elif i["type"] in ["IDENTIFIER", "AUTO", "BOOL", "STRING", "INT", "FLOAT", "VOID", "NULL"]:
            if i["type"] == "IDENTIFIER":
                temp = context.get(i["value"])

                if temp["type"] in ["libfunc", "func"]:
                    return i["value"]

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

            if target["type"] not in ["ARRAY", "STRING"]:
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

            if target["type"] not in ["ARRAY"]:
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

            else:
                tools.error("'!' operator can only use with booleans", context.file)

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
                    if value["value"] == "1":
                        return {"type": "BOOL", "value": "TRUE"}

                    elif value["value"] == "0":
                        return {"type": "BOOL", "value": "FALSE"}

                    else:
                        tools.error("unexpected value", context.file)

                else:
                    tools.error("can't cast '" + value["type"].lower() + "' into '" + i["cast_type"].lower() + "'", context.file)

            else:
                tools.error("can't cast '" + value["type"].lower() + "' into '" + i["cast_type"].lower() + "'", context.file)

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

                if float(left["value"].replace("f", "")) == 0.0 or float(right["value"].replace("f", "")) == 0.0:
                    tools.error("divide by zero", context.file)

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

            context.rem_parent_scope(tmp)
            context.delete_scope(cur)
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
                        if response["type"] != "NULL":
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
                                if response["type"] != "NULL":
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
                            if response["type"] != "NULL":
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

            if returned["type"] == "ARRAY" and context.current_return_type == "ARRAY":
                if returned["array_type"] != context.current_array_type:
                    tools.error("type mismatch", context.file)

            elif returned["type"] != context.current_return_type and context.current_return_type != None:
                tmp_ast = context.ast
                context.ast = [{"type": "cast", "cast_type": context.current_return_type, "value": returned}]
                returned = interpreter(context)
                context.ast = tmp_ast

            return returned

        elif i["type"] == "delete":
            if context.get(i["value"])["type"] == "ARRAY":
                context.delete(i["value"] + ".length")

            context.delete(i["value"])

        elif i["type"] == "call":
            tmp_ast = context.ast
            context.ast = [i["value"]]
            name = interpreter(context)
            context.ast = tmp_ast
            tmp_var = context.get(name)

            if tmp_var["type"] == "libfunc":
                if len(i["args"]) == len(tmp_var["args"]):  
                    tmp = []

                    for j in i["args"]:
                        tmp_ast = context.ast
                        context.ast = [j]
                        tmp.append(interpreter(context))
                        context.ast = tmp_ast

                    for index, j in enumerate(tmp_var["args"].values()):
                        if "type" in j:
                            if j["type"] == tmp[index]["type"]:
                                if j["array_type"] != tmp[index]["array_type"]:
                                    tools.error("array types mismatch", context.file)

                            else:
                                tools.error("argument type mismatch for '" + i["name"] + "'", context.file)

                        elif tmp[index]["type"] != j and tmp[index]["type"] not in ["NULL"]:
                            tmp_ast = context.ast
                            context.ast = [{"type": "cast", "cast_type": j, "value": tmp[index]}]
                            tmp[index] = interpreter(context)
                            context.ast = tmp_ast

                    new_tmp = {}

                    for index, j in enumerate(tmp):
                        name = list(tmp_var["args"].keys())[index]
                        new_tmp[name] = tools.rsx_to_py_value(j)

                    enviroment = {
                        "args": new_tmp,
                        "file": context.file,
                        "scope": context.scope,
                        "context": context,
                        "include_folders": context.include_folders
                    }

                    returned = tmp_var["func"](enviroment)
                    returned = tools.py_to_rsx_value(returned)

                    if returned["type"] not in [tmp_var["return_type"], "NULL"]:
                        tools.error("expected '" + tmp_var["return_type"].lower() + "' got '" + returned["type"].lower() + "'", context.file)

                    if len(context.ast) == 1:
                        return returned

                else:
                    tools.error("argument count didn't match for" + " " + "'" + name + "'", context.file)

            elif tmp_var["type"] == "func":
                if len(i["args"]) == len(tmp_var["args"]):
                    tmp = []

                    for j in i["args"]:
                        tmp_ast = context.ast
                        context.ast = [j]
                        tmp.append(interpreter(context))
                        context.ast = tmp_ast

                    for index, j in enumerate(tmp_var["args"].values()):
                        if "type" in j:
                            if j["type"] == tmp[index]["type"]:
                                if j["array_type"] != tmp[index]["array_type"]:
                                    tools.error("array types mismatch", context.file)

                            else:
                                tools.error("argument type mismatch for '" + i["name"] + "'", context.file)

                        elif tmp[index]["type"] != j and tmp[index]["type"] not in ["NULL"]:
                            tmp_ast = context.ast
                            context.ast = [{"type": "cast", "cast_type": j, "value": tmp[index]}]
                            tmp[index] = interpreter(context)
                            context.ast = tmp_ast

                    context.prepare_to_execute(name)

                    for index, j in enumerate(tmp_var["args"].keys()):
                        if tmp[index]["type"] in [tmp_var["args"][j], "NULL"] or (tmp[index]["type"] == tmp_var["args"][j]["type"] == "ARRAY" and tmp[index]["array_type"] == tmp_var["args"][j]["array_type"]):
                            tmp_ast = context.ast
                            gen_ast = {"type": "var", "name": j, "value_type": tmp[index]["type"], "value": tmp[index], "const": False}

                            if tmp[index]["type"] == "ARRAY":
                                gen_ast["array_type"] = tmp[index]["array_type"]
                                gen_ast["size"] = tmp[index]["size"]

                            context.ast = [gen_ast]
                            tmp_ret = context.current_return_type
                            context.current_return_type = None
                            interpreter(context)
                            context.current_return_type = tmp_ret
                            context.ast = tmp_ast

                        else:
                            tools.error("argument type mismatch for '" + i["name"] + "'", context.file)

                    returned = interpreter(context)
                    context.end_execute()

                    if returned == None:
                        returned = {"type": "NULL", "value": "NULL"}

                    if returned == {"type": "VOID", "value": "VOID"}:
                        returned = {"type": "NULL", "value": "NULL"}

                    if returned in ["BREAK", "CONTINUE"]:
                        tools.error("'break' or 'continue' keyword used in wrong place", context.file)

                    if returned["type"] != tmp_var["return_type"]:
                        tools.error("expected '" + tmp_var["return_type"].lower() + "' got '" + returned["type"].lower() + "'", context.file)

                    if len(context.ast) == 1:
                        return returned

                else:
                    tools.error("argument count didn't match for" + " " + "'" + i["name"] + "'", context.file)

            else:
                tools.error("argument type mismatch for '" + i["name"] + "'", context.file)

        else:
            tools.warning("undeclared" + " " + "'" + i["type"] + "'" + " " + "was passed", context.file)

    if context.is_base() and context.is_main_file():
        if context.program_state():
            if not context.is_exists("main"):
                tools.error("no entry point", context.file)

            if context.get("main")["return_type"] != "INT":
                tools.error("no entry point", context.file)

            if (context.get("main")["args"] != {"args": {"type": "ARRAY", "array_type": "STRING", "size": None}} and context.get("main")["args"] != {}):
                tools.error("no entry point", context.file)

            if error_code != None:
                if error_code != "0":
                    print(f"program exit with code {error_code}")

    else:
        if context.is_in_function() and context.current_return_type != None and context.current_return_type != "VOID":
            tools.error("non-void functions should return a value", context.file)

help = """
- help: for this page
- version: for the version of R#
- run [file] [args]: for running a R# program
- build [file] [args]: for running a R# program

file for run/build commands: file path (example: main.rsx)
args for run/build commands: -[timeit/console/noconsole/gettok/getast/bytecode]=[true/false] (example: -timeit=true)
                             -[I/rmI]=[library_path] (example: -Iinclude)
"""

def main():
    argv = sys.argv
    start_time = time.time()
    version = "0.1.0"

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

        elif i in ["version", "run", "build", "help"]:
            if mode == None: mode = i
            else: tools.error("mode already setted", file)

        else:
            if file == None: file = i
            program_args.append(i)

    if mode == None: mode = "run"
    if file == None and mode not in ["version", "help"]: tools.error("no input files", "rsx", "fatal error", True)
    if file != None and mode not in ["version", "help"]:
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

        else:
            file_content = preprocessor.preprocessor(tools.read_file(file), include_folders)

            if os.path.splitext(file)[0] + ".rsxc" in os.listdir() and bytecode:
                with open(os.path.splitext(file)[0] + ".rsxc", "rb") as f:
                    content = tools.load_bytecode(f.read())

                    if "version" in content:
                        if content["version"] == version:
                            if content["file_content"] == hashlib.sha256(file_content.encode()).digest():
                                ast = content["ast"]

            if ast == None:
                tokens = lexer(file_content, file)
                if get_tokens: print(tokens)
                ast = parser(tokens, file)

                if bytecode:
                    with open(os.path.splitext(file)[0] + ".rsxc", "wb") as f: f.write(tools.dump_bytecode(ast, file_content))

        if get_ast: print(ast)
        context = Context(ast, file)
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

    elif mode == "version":
        tools.set_text_attr(12)
        print(f"R# {version}", flush = True)
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