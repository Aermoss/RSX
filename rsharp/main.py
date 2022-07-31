import sys, os, time
import platform

from numba import njit, jit
from numba.core import types
from numba.typed import Dict

from functools import cache

sys.setrecursionlimit(5000)
sys.dont_write_bytecode = True

import importlib, pickle
import ctypes, ctypes.util
import difflib, hashlib

import rsharp.tools as tools
import rsharp.std as std
import rsharp.builder as builder

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
    # "const": "CONST",
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
    "%": "MODULUS"
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
    last_col = 0

    while len(data) > pos:
        col = last_col

        for i in data[last_pos:pos]:
            if i in "\r\n":
                row += 1
                col = 0

            col += 1

        last_pos = pos
        last_col = col

        while char.isspace():
            pos += 1
            col += 1
            char = get(pos)

        if char.isalpha() or char in ["_"]:
            id_str = ""

            while char.isalnum() or char in [".", ":", "_"]:
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

        elif char.isdigit() or char == ".":
            num_str = ""
            last_char = get(pos - 1)

            if char == ".":
                num_str += "0"

            while char.isdigit() or char in [".", "f"]:
                num_str += char
                pos += 1
                char = get(pos)

            if num_str.count(".") == 1:
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

            if tokens[len(tokens) - 2]["value"] == "MINUS" and last_char != " ":
                tokens.pop(len(tokens) - 2)
                num_str = "-" + num_str

            tokens.append({"value": num_str, "row": row, "col": col})

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

                elif char == last_char == "|":
                    tokens.append({"value": "OR", "row": row, "col": col})
                    tokens.pop(len(tokens) - 2)

                elif char == last_char == "&":
                    tokens.append({"value": "AND", "row": row, "col": col})
                    tokens.pop(len(tokens) - 2)

                else:
                    tokens.append({"value": operators[char], "row": row, "col": col})

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
        ignore = 0

        while True:
            if get(current_pos) == "LPAREN":
                if ignore != 0:
                    temp_tokens.append(get(current_pos, True))

                ignore += 1
                current_pos += 1

            elif get(current_pos) == "RPAREN":
                ignore -= 1

                if ignore == 0:
                    if len(temp_tokens) != 0:
                        temp_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
                        args.append(parser(temp_tokens, file)[0])
                        temp_tokens.clear()

                    break

                temp_tokens.append(get(current_pos, True))
                current_pos += 1

            elif get(current_pos) == "COMMA":
                if ignore == 1:
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
        args, arg_type, arg_name = {}, None, None
        ignore = 0

        while True:
            if get(current_pos) == "LPAREN":
                ignore += 1
                current_pos += 1

            elif get(current_pos) == "RPAREN":
                ignore -= 1

                if ignore == 0:
                    if arg_name != None and arg_type != None:
                        args[arg_name] = arg_type
                        arg_type, arg_name = None, None

                    break

                current_pos += 1

            elif get(current_pos) in ["BOOL", "INT", "FLOAT", "STRING"]:
                arg_type = get(current_pos)
                current_pos += 1

            elif get(current_pos) == "IDENTIFIER":
                arg_name = get(current_pos + 1)
                current_pos += 2

            elif get(current_pos) == "COMMA":
                if arg_name != None and arg_type != None:
                    args[arg_name] = arg_type
                    arg_type, arg_name = None, None

                current_pos += 1

        return args, current_pos + 1

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

    def collect_tokens(temp_pos, stop_tokens = ["SEMICOLON", "PLUS", "MINUS", "SLASH", "ASTERISK", "EQUALS" * 2, "NOT" + "EQUALS", "GREATER", "GREATER" + "EQUALS", "LESS", "LESS" + "EQUALS", "AND", "OR", "NOT"]):
        temp_tokens = []
        ignore = 0

        while True:
            if get(temp_pos) in stop_tokens:
                if ignore == 0: break

            elif get(temp_pos) == "LPAREN":
                temp_tokens.append(get(temp_pos, True))
                ignore += 1
                temp_pos += 1

            elif get(temp_pos) == "RPAREN":
                temp_tokens.append(get(temp_pos, True))
                ignore -= 1
                temp_pos += 1

            else:
                temp_tokens.append(get(temp_pos, True))
                temp_pos += 1

        temp_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
        return temp_tokens, temp_pos

    def factor(temp_pos, result = None):
        token = get(temp_pos)

        if result != None: return result, temp_pos

        if token == "LPAREN":
            if get(temp_pos + 1) in ["STRING", "BOOL", "INT", "FLOAT"] and get(temp_pos + 2) == "RPAREN":
                type = get(temp_pos + 1)
                temp_pos += 3
                result, temp_pos = expr(temp_pos)
                return {"type": "cast", "cast_type": type, "value": result}, temp_pos

            else:
                temp_pos += 1
                result, temp_pos = expr(temp_pos)
                if get(temp_pos) != "RPAREN": error(f"expected 'RPAREN' but found '{token}'")
                temp_pos += 1
                return result, temp_pos

        if token in ["INT", "FLOAT", "STRING"]:
            temp_pos += 2
            return {"type": token, "value": get(temp_pos - 1)}, temp_pos

        elif token in ["PLUS", "MINUS"]:
            temp_pos += 1
            return factor(temp_pos, result)

        elif token == "IDENTIFIER":
            name = get(temp_pos + 1)

            if get(temp_pos + 2) == "LPAREN":
                args, temp_pos = get_call_args(temp_pos + 2)
                return {"type": "call", "name": name, "args": args}, temp_pos

            else:
                temp_pos += 2
                return {"type": "IDENTIFIER", "value": name}, temp_pos

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

        while get(temp_pos) in ["PLUS", "MINUS"]:
            type = get(temp_pos)
            temp_pos += 1
            right, temp_pos = term(temp_pos)
            result = {"type": type.replace("PLUS", "add").replace("MINUS", "sub"), "left": result, "right": right}

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

                    elif get(temp_pos) in ["LCURLYBRACKET"]:
                        error("expected ')'")

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

                    elif get(condition_pos) in ["LCURLYBRACKET"]:
                        error("expected ')'")

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
            temp_tokens, pos = collect_tokens(pos, ["OR", "AND", "SEMICOLON"])
            ast.append({"type": "or", "left": left, "right": parser(temp_tokens, file)[0]})
            if get(pos) == "SEMICOLON": pos += 1

        elif get(pos) == "AND":
            left = ast[len(ast) - 1]
            ast.pop(len(ast) - 1)
            temp_tokens, pos = collect_tokens(pos, ["OR", "AND", "SEMICOLON"])
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

            while True:
                if get(pos) in ["SEMICOLON", "PLUS", "MINUS", "SLASH", "ASTERISK", "MODULUS", "EQUALS" * 2, "NOT" + "EQUALS", "GREATER", "GREATER" + "EQUALS", "LESS", "LESS" + "EQUALS", "AND", "OR", "NOT"]:
                    if ignore == 0: break
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

                else:
                    temp_tokens.append(get(pos, True))
                    pos += 1

            temp_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
            ast.append({"type": "cast", "cast_type": type, "value": parser(temp_tokens, file)[0]})

        elif get(pos) == "LPAREN":
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

            temp_tokens.append({"value": "SEMICOLON", "row": 0, "col": 0})
            ast.append(parser(temp_tokens, file)[0])
            pos += 1

        elif get(pos) in ["PLUS", "MINUS", "SLASH", "ASTERISK", "MODULUS"]:
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
            if get(pos + 3) == "SEMICOLON":
                if get(pos + 1) == "STRING":
                    ast.append({"type": get(pos).lower(), "all": False, "value": get(pos + 2)})
                    pos += 4

            elif get(pos + 3) == "COLON":
                if get(pos + 5) == "SEMICOLON":
                    if get(pos + 4) == "ASTERISK":
                        if get(pos + 1) == "STRING":
                            ast.append({"type": "include", "all": True, "value": get(pos + 2)})
                            pos += 6

        elif get(pos) in ["BREAK", "CONTINUE"]:
            if get(pos + 1) == "SEMICOLON":
                ast.append({"type": get(pos).lower()})
                pos += 2

        elif get(pos) == "IDENTIFIER":
            if get(pos + 2) in ["PLUS", "MINUS"] and get(pos + 3) in ["PLUS", "MINUS"]:
                if get(pos + 2) == get(pos + 3):
                    name = get(pos + 1)
                    type = get(pos + 2)
                    pos += 4

                    if get(pos) in ["SEMICOLON", "LPAREN", "RPAREN", "PLUS", "MINUS", "SLASH", "ASTERISK", "MODULUS", "EQUALS" * 2, "NOT" + "EQUALS", "GREATER", "GREATER" + "EQUALS", "LESS", "LESS" + "EQUALS", "OR", "AND", "NOT"]:
                        ast.append({"type": type.replace("PLUS", "increment").replace("MINUS", "decrement"), "value": name})
                        if get(pos) == "SEMICOLON": pos += 1

                    else:
                        error("expected ';'")

            elif get(pos + 2) in ["EQUALS", "PLUS" + "EQUALS", "MINUS" + "EQUALS", "ASTERISK" + "EQUALS", "SLASH" + "EQUALS", "MODULUS" + "EQUALS"]:
                temp_tokens = []
                name = get(pos + 1)
                type = get(pos + 2)
                pos += 3

                while True:
                    if get(pos) == "SEMICOLON":
                        temp_tokens.append(get(pos))
                        break

                    else:
                        temp_tokens.append(get(pos))
                        pos += 1

                value = parser(temp_tokens, file)[0]

                if type == "PLUS" + "EQUALS": value = {"type": "add", "left": {"type": "IDENTIFIER", "value": name}, "right": value}
                if type == "MINUS" + "EQUALS": value = {"type": "sub", "left": {"type": "IDENTIFIER", "value": name}, "right": value}
                if type == "ASTERISK" + "EQUALS": value = {"type": "mul", "left": {"type": "IDENTIFIER", "value": name}, "right": value}
                if type == "SLASH" + "EQUALS": value = {"type": "div", "left": {"type": "IDENTIFIER", "value": name}, "right": value}
                if type == "MODULUS" + "EQUALS": value = {"type": "mod", "left": {"type": "IDENTIFIER", "value": name}, "right": value}

                if get(pos) == "SEMICOLON":
                    ast.append({"type": "var", "value_type": None, "name": name, "value": value})
                    pos += 1

            elif get(pos + 2) == "LPAREN":
                name = get(pos + 1)
                args, pos = get_call_args(pos + 2)

                if get(pos) in ["SEMICOLON", "LPAREN", "RPAREN", "PLUS", "MINUS", "SLASH", "ASTERISK", "MODULUS", "EQUALS" * 2, "NOT" + "EQUALS", "GREATER", "GREATER" + "EQUALS", "LESS", "LESS" + "EQUALS", "OR", "AND", "NOT"]:
                    ast.append({"type": "call", "name": name, "args": args})
                    if get(pos) == "SEMICOLON": pos += 1

                else:
                    error("expected ';'")

            else:
                if get(pos + 2) in ["SEMICOLON", "LPAREN", "RPAREN", "PLUS", "MINUS", "SLASH", "ASTERISK", "MODULUS", "EQUALS" * 2, "NOT" + "EQUALS", "GREATER", "GREATER" + "EQUALS", "LESS", "LESS" + "EQUALS", "OR", "AND", "NOT"]:
                    ast.append({"type": "IDENTIFIER", "value": get(pos + 1)})
                    if get(pos + 2) == "SEMICOLON": pos += 3
                    else: pos += 2

        elif get(pos) in ["VOID", "BOOL", "INT", "FLOAT", "STRING", "AUTO"]:
            if get(pos + 2) in ["SEMICOLON", "LPAREN", "RPAREN", "PLUS", "MINUS", "SLASH", "ASTERISK", "MODULUS", "EQUALS" * 2, "NOT" + "EQUALS", "GREATER", "GREATER" + "EQUALS", "LESS", "LESS" + "EQUALS", "OR", "AND", "NOT"]:
                ast.append({"type": get(pos), "value": get(pos + 1)})
                if get(pos + 2) == "SEMICOLON": pos += 3
                else: pos += 2

            else:
                if "." in get(pos + 2):
                    error("invalid character", suggest = False)

                if ":" in get(pos + 2):
                    error("invalid character", suggest = False)

                type = get(pos)
                name = get(pos + 2)

                if get(pos + 3) == "EQUALS":
                    temp_tokens = []
                    pos += 4

                    while True:
                        if get(pos) == "SEMICOLON":
                            temp_tokens.append(get(pos))
                            break

                        else:
                            temp_tokens.append(get(pos))
                            pos += 1

                    if get(pos) == "SEMICOLON":
                        ast.append({"type": "var", "value_type": type, "name": name, "value": parser(temp_tokens, file)[0]})
                        pos += 1

                elif get(pos + 3) == "SEMICOLON":
                    if get(pos + 1) == "IDENTIFIER":
                        ast.append({"type": "var", "value_type": type, "name": name, "value": {"type": type, "value": None}})
                        pos += 4

                elif get(pos + 3) == "LPAREN":
                    args, pos = get_def_args(pos + 3)

                    if get(pos) == "SEMICOLON":
                        ast.append({"type": "func", "return_type": type, "name": name, "args": args, "ast": []})
                        pos += 1

                    else:
                        temp_ast, pos = get_func_ast(pos)
                        ast.append({"type": "func", "return_type": type, "name": name, "args": args, "ast": temp_ast})

        elif get(pos) in ["SEMICOLON", "NULL"]:
            ast.append({"type": "NULL", "value": "NULL"})
            pos += 1

    return ast

def interpreter(ast, file, isbase, islib, functions, variables, return_type, library_functions, include_folders, svariables = {}, sfunctions = {}, already_included = [], pre_included = []):
    variables["__file__"] = {"type": "STRING", "value": file}
    
    def error(msg, file = file, type = "error", terminated = False):
        print(f"{file}:", end = " ", flush = True)
        tools.set_text_attr(12)
        print(f"{type}: ", end = "", flush = True)
        tools.set_text_attr(7)
        print(msg, end = "\n", flush = True)
        if terminated: print("program terminated.")
        sys.exit(-1)

    def warning(message, file = file, type = "warning"):
        print(f"{file}:", end = " ", flush = True)
        tools.set_text_attr(13)
        print(f"{type}: ", end = "", flush = True)
        tools.set_text_attr(7)
        print(message, end = "\n", flush = True)

    def define_standards(file, functions, variables, library_functions, include_folders):
        library_functions.update(std.std["functions"])
        variables["__OSNAME__"] = {"type": "STRING", "value": os.name}
        variables["__MACHINE__"] = {"type": "STRING", "value": platform.machine()}
        variables["__SYSTEM__"] = {"type": "STRING", "value": platform.system()}
        variables["__ARCH__"] = {"type": "STRING", "value": platform.architecture()[0]}
        variables["__PLATFORM__"] = {"type": "STRING", "value": sys.platform}
        variables["__NODE__"] = {"type": "STRING", "value": platform.node()}

    def proccess_string(string):
        return string.replace("\\n", "\n").replace("\\\\", "\\").replace("\\t", "\t").replace("\\\"", "\"").replace("mavish", "♥ mavish ♥")

    if isbase or islib:
        if isbase:
            found_main = False

        define_standards(file, functions, variables, library_functions, include_folders)

    result_report = {}

    for index, i in enumerate(ast):
        if i["type"] == "func":
            if i["name"] in functions or i["name"] in library_functions:
                error("can't overload a function")

            if i["name"] in variables:
                error("can't overload a function with a variable")

            if i["return_type"] not in ["VOID", "FLOAT", "INT", "STRING", "BOOL"]:
                error("unknown type for function: '" + i["return_type"].lower() + "'")

            functions[i["name"]] = {"type": i["return_type"], "args": i["args"], "ast": i["ast"]}

            if i["name"] == "main" and i["return_type"] == "INT" and i["args"] == {} and not found_main:
                if isbase:
                    found_main = True
                    error_code = interpreter(functions[i["name"]]["ast"], file, False, False, functions, variables, i["return_type"], library_functions, include_folders, variables.copy(), functions.copy())
                    
                    if error_code in ["BREAK", "CONTINUE"]:
                        error("cant use '" + error_code.lower() + "' here")

                    elif error_code["type"] == "NULL":
                        error("non-void functions should return a value")

                    else:
                        if error_code["type"] == "INT":
                            error_code = error_code["value"]

        elif i["type"] == "namespace":
            temp_variables, temp_functions, temp_library_functions = interpreter(i["ast"], file, False, False, functions.copy(), variables.copy(), None, library_functions.copy(), include_folders)
            
            for j in temp_variables:
                if j not in variables:
                    variables[i["name"] + "::" + j] = temp_variables[j]

            for j in temp_functions:
                if j not in functions:
                    functions[i["name"] + "::" + j] = temp_functions[j]

            for j in temp_library_functions:
                if j not in library_functions:
                    library_functions[i["name"] + "::" + j] = temp_library_functions[j]

        elif i["type"] in ["increment", "decrement"]:
            if i["value"] not in variables:
                error("'" + i["value"] + "' was not declared in this scope")

            else:
                if variables[i["value"]]["type"] in ["FLOAT", "INT"]:
                    if variables[i["value"]]["type"] == "INT":
                        variables[i["value"]]["value"] = str(int(variables[i["value"]]["value"]) + (1 if i["type"] == "increment" else -1))

                    elif variables[i["value"]]["type"] == "FLOAT":
                        variables[i["value"]]["value"] = str(float(variables[i["value"]]["value"].lower().replace("f", "")) + (1 if i["type"] == "increment" else -1)) + "f"

                    else:
                        error("unknown error")

                else:
                    error("'" + i["value"] + "' should be an integer or float value")
                
            if len(ast) == 1:
                return variables[i["value"]]

        elif i["type"] in ["break", "continue"]:
            if isbase: error("cant use '" + i["type"] + "' here")
            return i["type"].upper()
                
        elif i["type"] == "var":
            value = interpreter([i["value"]], file, False, False, functions, variables, "VOID", library_functions, include_folders)

            if i["value_type"] == None:
                if i["name"] in variables:
                    if value["type"] != variables[i["name"]]["type"]:
                        value = interpreter([{"type": "cast", "cast_type": variables[i["name"]]["type"], "value": value}], file, False, False, functions, variables, "VOID", library_functions, include_folders)
                        
                    variables[i["name"]] = value.copy()

                else:
                    error("'" + i["name"] + "' was not declared")

            else:
                if i["name"] in variables:
                    error("redefinition of '" + i["name"] + "'")

                else:
                    if i["value_type"] == "AUTO":
                        if value == None:
                            error("aaaaugh")

                    elif value["type"] != i["value_type"]:
                        value = interpreter([{"type": "cast", "cast_type": i["value_type"], "value": value}], file, False, False, functions, variables, "VOID", library_functions, include_folders)
                        
                    variables[i["name"]] = value.copy()

        elif i["type"] == "include":
            if i["value"] in already_included:
                warning("trying to include '" + i["value"] + "' twice")
                continue

            if i["value"] in pre_included:
                continue

            already_included.append(i["value"])

            name, ext = os.path.splitext(i["value"])

            if ext == ".py":
                file_path = None
                
                for j in include_folders:
                    if os.path.exists(j + "/" + i["value"]):
                        file_path = j + "/" + i["value"]
                        break

                if file_path == None: error("'" + i["value"] + "'" + " " + "was not found")

                if os.path.split(file_path)[0] not in sys.path:
                    sys.path.append(os.path.split(file_path)[0])

                temp = getattr(importlib.import_module(os.path.split(name)[1]), os.path.split(name)[1])

                if not i["all"]:
                    library = {"functions": {}, "variables": {}}

                    for j in temp["functions"].keys():
                        library["functions"][os.path.split(name)[1] + "::" + j] = temp["functions"][j]

                    library_functions.update(library["functions"])
                
                else:
                    library_functions.update(temp["functions"])

            else:
                file_path = None

                if ext == ".rsxh":
                    for j in include_folders:
                        if os.path.exists(j + "/" + i["value"]):
                            file_path = j + "/" + i["value"]
                            break

                else:
                    for j in include_folders:
                        if os.path.exists(j + "/" + i["value"] + "/" + "init.rsxh"):
                            file_path = j + "/" + i["value"] + "/" + "init.rsxh"
                            break

                if file_path == None:
                    error("'" + i["value"] + "'" + " " + "was not found")

                temp = interpreter(parser(lexer(tools.read_file(file_path), file_path), file_path), file_path, False, True, {}, {}, None, {}, include_folders)

                if not i["all"]:
                    library = {"functions": {}, "variables": {}, "library_functions": {}}

                    for j in temp[0].keys():
                        library["variables"][os.path.split(i["value"])[1] + "::" + j] = temp[0][j]

                    for j in temp[1].keys():
                        library["functions"][os.path.split(i["value"])[1] + "::" + j] = temp[1][j]

                    for j in temp[2].keys():
                        library["library_functions"][os.path.split(i["value"])[1] + "::" + j] = temp[2][j]

                    variables.update(library["variables"])
                    functions.update(library["functions"])
                    library_functions.update(library["library_functions"])
                
                else:
                    variables.update(temp[0])
                    functions.update(temp[1])
                    library_functions.update(temp[2])

        elif i["type"] in ["IDENTIFIER", "AUTO", "BOOL", "STRING", "INT", "FLOAT", "VOID", "NULL"]:
            if i["type"] == "IDENTIFIER":
                if i["value"] in variables:
                    return variables[i["value"]].copy()

                else:
                    error("'" + i["value"] + "' was not declared in this scope")

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
                    error("unexpected type")

            else:
                return i

        elif i["type"] == "not":
            value = interpreter([i["value"]], file, False, False, functions, variables, "VOID", library_functions, include_folders)

            if value["type"] == "BOOL":
                if value["value"] == "TRUE":
                    return {"type": "BOOL", "value": "FALSE"}

                elif value["value"] == "FALSE":
                    return {"type": "BOOL", "value": "TRUE"}

                else:
                    error("unexpected type")

            else:
                error("'!' operator can only use with bools")

        elif i["type"] == "cast":
            value = interpreter([i["value"]], file, False, False, functions, variables, "VOID", library_functions, include_folders)
            
            if i["cast_type"] == "STRING":
                if value["type"] == "STRING":
                    return value

                elif value["type"] == "INT":
                    return {"type": "STRING", "value": str(value["value"])}

                elif value["type"] == "FLOAT":
                    return {"type": "STRING", "value": str(value["value"]).lower().replace("f", "")}

                elif value["type"] == "BOOL":
                    return {"type": "STRING", "value": str(value["value"]).lower()}

                else:
                    error("can't cast '" + value["type"].lower() + "' into '" + i["cast_type"].lower() + "'")

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
                        error("unexpected error")
                    
                else:
                    error("can't cast '" + value["type"].lower() + "' into '" + i["cast_type"].lower() + "'")

            elif i["cast_type"] == "FLOAT":
                if value["type"] == "FLOAT":
                    return value

                elif value["type"] == "INT":
                    return {"type": "FLOAT", "value": str(value["value"]) + ".0f"}

                else:
                    error("can't cast '" + value["type"].lower() + "' into '" + i["cast_type"].lower() + "'")

            elif i["cast_type"] == "BOOL":
                if value["type"] == "BOOL":
                    return value

                elif value["type"] == "INT":
                    if value["value"] == "1":
                        return {"type": "BOOL", "value": "TRUE"}

                    elif value["value"] == "0":
                        return {"type": "BOOL", "value": "FALSE"}

                    else:
                        error("unexpected value")

                else:
                    error("can't cast '" + value["type"].lower() + "' into '" + i["cast_type"].lower() + "'")

            else:
                error("can't cast '" + value["type"].lower() + "' into '" + i["cast_type"].lower() + "'")

        elif i["type"] == "switch":
            value = interpreter([i["value"]], file, False, False, functions, variables, None, library_functions, include_folders)
            match = False

            for j in i["cases"]:
                if j != "default":
                    case_value = interpreter([i["cases"][j]["value"]], file, False, False, functions, variables, None, library_functions, include_folders)

                    if value == case_value:
                        match = True
                        interpreter(i["cases"][j]["ast"], file, False, False, functions, variables, None, library_functions, include_folders)
                        break

            if match == False:
                if "default" in i["cases"]:
                    interpreter(i["cases"]["default"]["ast"], file, False, False, functions, variables, None, library_functions, include_folders)

        elif i["type"] == "or":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

            if left["type"] == "BOOL" and right["type"] == "BOOL":
                left = True if left["value"] == "TRUE" else False
                right = True if right["value"] == "TRUE" else False

                if left or right:
                    return {"type": "BOOL", "value": "TRUE"}

                else:
                    return {"type": "BOOL", "value": "FALSE"}

            else:
                error("can't perform or operation with '" + left["type"] + "' and '" + right["type"] + "' types")

        elif i["type"] == "and":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

            if left["type"] == "BOOL" and right["type"] == "BOOL":
                left = True if left["value"] == "TRUE" else False
                right = True if right["value"] == "TRUE" else False

                if left and right:
                    return {"type": "BOOL", "value": "TRUE"}

                else:
                    return {"type": "BOOL", "value": "FALSE"}

            else:
                error("can't perform and operation with '" + left["type"] + "' and '" + right["type"] + "' types")

        elif i["type"] == "notequals":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

            if left != right:
                return {"type": "BOOL", "value": "TRUE"}

            else:
                return {"type": "BOOL", "value": "FALSE"}

        elif i["type"] == "equalsequals":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

            if left == right:
                return {"type": "BOOL", "value": "TRUE"}

            else:
                return {"type": "BOOL", "value": "FALSE"}

        elif i["type"] == "less":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

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
                error("can't perform less operation with '" + left["type"] + "' and '" + right["type"] + "' types")

        elif i["type"] == "lessequals":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

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
                error("can't perform less operation with '" + left["type"] + "' and '" + right["type"] + "' types")

        elif i["type"] == "greater":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

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
                error("can't perform less operation with '" + left["type"] + "' and '" + right["type"] + "' types")

        elif i["type"] == "greaterequals":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

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
                error("can't perform less operation with '" + left["type"] + "' and '" + right["type"] + "' types")

        elif i["type"] == "add":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    return {"type": "FLOAT", "value": str(float(left["value"].replace("f", "")) + float(right["value"].replace("f", "")))}

                else:
                    return {"type": "INT", "value": str(int(left["value"]) + int(right["value"]))}
                    
            elif left["type"] == "STRING" and right["type"] == "STRING":
                return {"type": "STRING", "value": str(left["value"] + right["value"])}

            else:
                error("can't perform add operation with '" + left["type"] + "' and '" + right["type"] + "' types")

        elif i["type"] == "sub":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    return {"type": "FLOAT", "value": str(float(left["value"].replace("f", "")) - float(right["value"].replace("f", "")))}

                else:
                    return {"type": "INT", "value": str(int(left["value"]) - int(right["value"]))}

            else:
                error("can't perform subtract operation with '" + left["type"] + "' and '" + right["type"] + "' types")

        elif i["type"] == "mul":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    return {"type": "FLOAT", "value": str(float(left["value"].replace("f", "")) * float(right["value"].replace("f", "")))}

                else:
                    return {"type": "INT", "value": str(int(left["value"]) * int(right["value"]))}

            elif left["type"] == "STRING" and right["type"] == "INT":
                return {"type": "STRING", "value": left["value"] * int(right["value"])}

            else:
                error("can't perform multiply operation with '" + left["type"] + "' and '" + right["type"] + "' types")

        elif i["type"] == "div":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if float(left["value"].replace("f", "")) == 0.0 or float(right["value"].replace("f", "")) == 0.0:
                    error("divide by zero")

                if isfloat:
                    return {"type": "FLOAT", "value": str(float(left["value"].replace("f", "")) / float(right["value"].replace("f", "")))}

                else:
                    return {"type": "FLOAT", "value": str(int(left["value"]) / int(right["value"]))}

            else:
                error("can't perform divide operation with '" + left["type"] + "' and '" + right["type"] + "' types")

        elif i["type"] == "mod":
            left = interpreter([i["left"]], file, False, False, functions, variables, None, library_functions, include_folders)
            right = interpreter([i["right"]], file, False, False, functions, variables, None, library_functions, include_folders)

            if left["type"] in ["FLOAT", "INT"] and right["type"] in ["FLOAT", "INT"]:
                isfloat = left["type"] == "FLOAT" or right["type"] == "FLOAT"

                if isfloat:
                    return {"type": "FLOAT", "value": str(float(left["value"].replace("f", "")) % float(right["value"].replace("f", "")))}

                else:
                    return {"type": "INT", "value": str(int(left["value"]) % int(right["value"]))}

            else:
                error("can't perform remainder operation with '" + left["type"] + "' and '" + right["type"] + "' types")

        elif i["type"] == "for":
            sec_temp_variables, sec_temp_functions, sec_temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            interpreter(i["init"], file, False, False, functions, variables, None, library_functions, include_folders)
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            condition = interpreter([i["condition"]], file, False, False, functions, variables, None, library_functions, include_folders) if len(i["condition"]) != 0 else True

            while condition["type"] == "BOOL" and condition["value"] == "TRUE":
                response = interpreter(i["ast"], file, False, False, functions, variables, None, library_functions, include_folders)
                interpreter(i["update"], file, False, False, functions, variables, "PASS", library_functions, include_folders)
                if response != None:
                    if "type" in response:
                        if response["type"] != "NULL":
                            return response
                condition = interpreter([i["condition"]], file, False, False, functions, variables, None, library_functions, include_folders) if len(i["condition"]) != 0 else True

                for j in list(set(variables) - set(temp_variables)): del variables[j]
                for j in list(set(functions) - set(temp_functions)): del functions[j]
                for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]
                if response == "BREAK": break

            for j in list(set(variables) - set(sec_temp_variables)): del variables[j]
            for j in list(set(functions) - set(sec_temp_functions)): del functions[j]
            for j in list(set(library_functions) - set(sec_temp_library_functions)): del library_functions[j]

        elif i["type"] == "do":
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            response = interpreter(i["ast"], file, False, False, functions, variables, "PASS", library_functions, include_folders)
            if response != None:
                if "type" in response:
                    if response["type"] != "NULL":
                        return response

            for j in list(set(variables) - set(temp_variables)): del variables[j]
            for j in list(set(functions) - set(temp_functions)): del functions[j]
            for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]

            if response == "BREAK": break

        elif i["type"] == "do while":
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            interpreter(i["ast"], file, False, False, functions, variables, None, library_functions, include_folders)
            result_report[index] = interpreter([i["condition"]], file, False, False, functions, variables, None, library_functions, include_folders)

            while result_report[index]["type"] == "BOOL" and result_report[index]["value"] == "TRUE":
                response = interpreter(i["ast"], file, False, False, functions, variables, "PASS", library_functions, include_folders)
                if response != None:
                    if "type" in response:
                        if response["type"] != "NULL":
                            return response
                result_report[index] = interpreter([i["condition"]], file, False, False, functions, variables, None, library_functions, include_folders)

                for j in list(set(variables) - set(temp_variables)): del variables[j]
                for j in list(set(functions) - set(temp_functions)): del functions[j]
                for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]
                if response == "BREAK": break

            for j in list(set(variables) - set(temp_variables)): del variables[j]
            for j in list(set(functions) - set(temp_functions)): del functions[j]
            for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]

        elif i["type"] == "while":
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            result_report[index] = interpreter([i["condition"]], file, False, False, functions, variables, None, library_functions, include_folders)

            while result_report[index]["type"] == "BOOL" and result_report[index]["value"] == "TRUE":
                response = interpreter(i["ast"], file, False, False, functions, variables, "PASS", library_functions, include_folders)
                if response != None:
                    if "type" in response:
                        if response["type"] != "NULL":
                            return response
                result_report[index] = interpreter([i["condition"]], file, False, False, functions, variables, None, library_functions, include_folders)

                for j in list(set(variables) - set(temp_variables)): del variables[j]
                for j in list(set(functions) - set(temp_functions)): del functions[j]
                for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]
                if response == "BREAK": break

        elif i["type"] == "if":
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            result_report[index] = interpreter([i["condition"]], file, False, False, functions, variables, None, library_functions, include_folders)

            if result_report[index]["type"] == "BOOL" and result_report[index]["value"] == "TRUE":
                response = interpreter(i["ast"], file, False, False, functions, variables, "PASS", library_functions, include_folders)
                if response in ["BREAK", "CONTINUE"]: return response
                if response != None:
                    if "type" in response:
                        if response["type"] != "NULL":
                            return response

                for j in list(set(variables) - set(temp_variables)): del variables[j]
                for j in list(set(functions) - set(temp_functions)): del functions[j]
                for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]

        elif i["type"] == "else if":
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()

            if ast[index]["type"] in ["if", "else if"] and (index - 1 in result_report):
                if result_report[index - 1]["type"] == "BOOL" and result_report[index - 1]["value"] == "FALSE":
                    result_report[index] = interpreter([i["condition"]], file, False, False, functions, variables, None, library_functions, include_folders)

                    if result_report[index]["type"] == "BOOL" and result_report[index]["value"] == "TRUE":
                        response = interpreter(i["ast"], file, False, False, functions, variables, "PASS", library_functions, include_folders)
                        if response in ["BREAK", "CONTINUE"]: return response
                        if response != None:
                            if "type" in response:
                                if response["type"] != "NULL":
                                    return response

                        for j in list(set(variables) - set(temp_variables)): del variables[j]
                        for j in list(set(functions) - set(temp_functions)): del functions[j]
                        for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]

                else:
                    result_report[index] = True

            else:
                error("couldn't find any statements")

        elif i["type"] == "else":
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()

            if ast[index - 1]["type"] in ["if", "else if", "while"] and (index - 1 in result_report):

                if result_report[index - 1]["type"] == "BOOL" and result_report[index - 1]["value"] == "FALSE":
                    response = interpreter(i["ast"], file, False, False, functions, variables, "PASS", library_functions, include_folders)
                    if response in ["BREAK", "CONTINUE"]: return response
                    if response != None:
                        if "type" in response:
                            if response["type"] != "NULL":
                                return response

                    for j in list(set(variables) - set(temp_variables)): del variables[j]
                    for j in list(set(functions) - set(temp_functions)): del functions[j]
                    for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]

            else:
                error("couldn't find any statements")

        elif i["type"] == "using namespace":
            for j in library_functions.copy():
                if i["name"] + "::" in j:
                    library_functions[j.replace(i["name"] + "::", "")] = library_functions[j]

            for j in functions.copy():
                if i["name"] + "::" in j:
                    functions[j.replace(i["name"] + "::", "")] = functions[j]

            for j in variables.copy():
                if i["name"] + "::" in j:
                    variables[j.replace(i["name"] + "::", "")] = variables[j]

        elif i["type"] == "return":
            if isbase or islib:
                error("return can only be used in functions")

            if return_type == "VOID":
                if i["value"]["type"] != None:
                    error("can't return any value in non-void functions")

            returned = interpreter([i["value"]], file, False, False, functions, variables, "VOID", library_functions, include_folders)

            if returned["type"] != return_type and return_type not in ["PASS"]:
                error("expected '" + return_type.lower() + "' got '" + returned["type"].lower() + "'")
            
            return returned

        elif i["type"] == "delete":
            if i["value"] in variables:
                del variables[i["value"]]

            elif i["value"] in functions:
                del functions[i["value"]]

            elif i["value"] in library_functions:
                del library_functions[i["value"]]

            else:
                error("'" + i["value"] + "' was not declared in this scope")

        elif i["type"] == "call":
            if isbase or islib:
                error("functions only can be called in functions")

            elif i["name"] in library_functions:
                if len(i["args"]) == len(library_functions[i["name"]]["args"]):  
                    temp = []

                    for j in i["args"]:
                        temp.append(interpreter([j], file, False, False, functions, variables, None, library_functions, include_folders))

                    for index, j in enumerate(library_functions[i["name"]]["args"].values()):
                        if temp[index]["type"] != j and temp[index]["type"] not in ["NULL"]:
                            temp[index] = interpreter([{"type": "cast", "cast_type": j, "value": temp[index]}], file, False, False, functions, variables, "INT", library_functions, include_folders)
                        
                    new_temp = {}

                    for index, j in enumerate(temp):
                        name = list(library_functions[i["name"]]["args"].keys())[index]

                        if j["type"] == "INT":
                            new_temp[name] = int(j["value"])

                        elif j["type"] == "FLOAT":
                            new_temp[name] = float(j["value"].lower().replace("f", ""))

                        elif j["type"] == "BOOL":
                            if j["value"] == "TRUE": new_temp[name] = True
                            elif j["value"] == "FALSE": new_temp[name] = False
                            else: error("unknown value")

                        elif j["type"] == "STRING":
                            new_temp[name] = j["value"]

                        elif j["type"] == "NULL":
                            new_temp[name] = None

                        else:
                            error("unknown type")

                    enviroment = {
                        "args": new_temp,
                        "file": file,
                        "functions": functions,
                        "variables": variables,
                        "library_functions": library_functions,
                        "include_folders": include_folders
                    }

                    returned = library_functions[i["name"]]["func"](enviroment)

                    if returned == None: returned = {"type": "NULL", "value": "NULL"}
                    elif type(returned) == int: returned = {"type": "INT", "value": str(returned)}
                    elif type(returned) == float: returned = {"type": "FLOAT", "value": str(returned) + "f"}
                    elif type(returned) == bool: returned = {"type": "BOOL", "value": str(returned).upper()}
                    elif type(returned) == str: returned = {"type": "STRING", "value": str(returned)}
                    else: error("unknown type")

                    if returned["type"].replace("NULL", "VOID") != library_functions[i["name"]]["type"]:
                        warning("expected '" + library_functions[i["name"]]["type"].lower() + "' got '" + returned["type"].lower() + "'")

                    if len(ast) == 1:
                        return returned

                else:
                    error("argument count didn't match for" + " " + "'" + i["name"] + "'")

            elif i["name"] in functions:
                if len(i["args"]) == len(functions[i["name"]]["args"]):
                    temp = []

                    for j in i["args"]:
                        temp.append(interpreter([j], file, False, False, functions, variables, None, library_functions, include_folders))

                    for index, j in enumerate(functions[i["name"]]["args"].values()):
                        if temp[index]["type"] != j and temp[index]["type"] not in ["NULL"]:
                            temp[index] = interpreter([{"type": "cast", "cast_type": j, "value": temp[index]}], file, False, False, functions, variables, None, library_functions, include_folders)

                    temp_vars = svariables.copy()

                    for index, j in enumerate(functions[i["name"]]["args"].keys()):
                        if functions[i["name"]]["args"][j] == temp[index]["type"]:
                            temp_vars[j] = temp[index]

                    if i["name"] not in sfunctions:
                        sfunctions[i["name"]] = functions[i["name"]]

                    returned = interpreter(functions[i["name"]]["ast"], file, False, False, sfunctions.copy(), temp_vars, functions[i["name"]]["type"], library_functions, include_folders, variables.copy(), functions.copy())

                    if returned in ["BREAK", "CONTINUE"]:
                        error("'break' or 'continue' keyword used in wrong place")

                    if returned["type"].replace("NULL", "VOID") != functions[i["name"]]["type"]:
                        warning("expected '" + functions[i["name"]]["type"].lower() + "' got '" + returned["type"].lower() + "'")

                    if len(ast) == 1:
                        return returned

                else:
                    error("argument count didn't match for" + " " + "'" + i["name"] + "'")

            else:
                error("'" + i["name"] + "'" + " " + "was not declared in this scope")

        else:
            warning("undeclared" + " " + "'" + i["type"] + "'" + " " + "was passed")

    if isbase:
        if not found_main:
            error("no entry point")

        if error_code != None:
            if error_code != "0":
                print(f"program exit with code {error_code}")

    else:
        if return_type != None and return_type != "VOID" and return_type != "PASS":
            error("non-void functions should return a value")

        elif return_type == None:
            return variables, functions, library_functions

def main():
    argv = sys.argv
    start_time = time.time()
    version = "0.0.11a"

    include_folders = [f"{tools.get_dir()}/include/", "./"]
    if sys.platform == "win32": include_folders.append("C:\\RSharp\\include\\")
    console = True
    bytecode = True
    timeit = False
    get_tokens = False
    get_ast = False
    mode = None
    file = None

    for i in argv[1:]:
        if i[0] == "-":
            arg = i[1:].split("=")

            if arg[0][0] == "I":
                include_folders.append(arg[0][1:])

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

        elif i in ["version", "run", "build"]:
            if mode == None: mode = i
            else: tools.error("mode already setted", file)

        else:
            if file == None: file = i
            else: tools.error("file already setted", file)

    if mode == None: mode = "run"
    if file == None and mode != "version": tools.error("no input files", "rsharp", "fatal error", True)
    if file != None and mode != "version":
        if not os.path.isfile(file):
            tools.error("file not found", "rsharp", "fatal error", True)

    if mode == "run":
        if os.path.splitext(file)[1] not in [".rsx", ".rsxd", ".rsxc", ".rsxp"]:
            tools.error(f"invalid extension: '{os.path.splitext(file)[1]}'", file)

        ast = None

        if os.path.splitext(file)[1] == ".rsxc":
            with open(os.path.splitext(file)[0] + ".rsxc", "rb") as f:
                ast = pickle.loads(f.read())["ast"]

        else:
            file_content = tools.read_file(file)

            if os.path.splitext(file)[0] + ".rsxc" in os.listdir() and bytecode:
                with open(os.path.splitext(file)[0] + ".rsxc", "rb") as f:
                    content = pickle.loads(f.read())

                    if "version" not in content:
                        tools.error("bytecode version didn't match [bytecode: " + content["version"] + f", current: {version}]", file)

                    if content["version"] != version:
                        tools.error("bytecode version didn't match [bytecode: " + content["version"] + f", current: {version}]", file)

                    if content["file_content"] == hashlib.sha256(file_content.encode()).digest():
                        ast = content["ast"]

            if ast == None:
                tokens = lexer(file_content, file)
                if get_tokens: print(tokens)
                ast = parser(tokens, file)

                if bytecode:
                    content = {"ast": ast, "file_content": hashlib.sha256(file_content.encode()).digest(), "version": version}
                    with open(os.path.splitext(file)[0] + ".rsxc", "wb") as f: f.write(pickle.dumps(content))

        if get_ast: print(ast)
        interpreter(ast, file, True, False, {}, {}, None, {}, include_folders)

    elif mode == "build":
        if os.path.splitext(file)[1] not in [".rsx", ".rsxd", ".rsxc", ".rsxp"]:
            tools.error(f"invalid extension: '{os.path.splitext(file)[1]}'", file)

        variables, functions, library_functions, files, tokens, ast = tools.auto_include(
            file = file,
            include_folders = include_folders
        )

        if get_tokens: print(tokens)
        if get_ast: print(ast)

        builder.build_program(
            path = file,
            include_folders = include_folders,
            console = console,
            variables = variables,
            functions = functions,
            library_functions = library_functions,
            pre_included = files,
        )

    elif mode == "version":
        tools.set_text_attr(12)
        print(f"R# {version}", flush = True)
        tools.set_text_attr(7)

    else:
        tools.error("unknown error", file)

    if timeit:
        print("finished in:", time.time() - start_time)

    return 0

if __name__ == "__main__":
    try: sys.exit(main())
    except KeyboardInterrupt: ...