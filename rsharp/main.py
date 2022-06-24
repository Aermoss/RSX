import sys, os

from sympy import posify

sys.dont_write_bytecode = True

import importlib
import ctypes, ctypes.util
import difflib, json
import string as strlib

import rsharp.transpiler as transpiler
import rsharp.tools as tools
import rsharp.std as std
import rsharp.builder as builder

def lexer(data, file, create_json):
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

    def check_str(value):
        temp_value = []
        should_done = False

        for index, i in enumerate(value):
            if i in strlib.ascii_letters + strlib.digits + "_" + "." + ":":
                if not should_done:
                    if index == 0:
                        if i in strlib.digits:
                            error("invalid character")

                    temp_value.append(i)

                else:
                    error("invalid character")

            elif i == " ":
                should_done = True

            else:
                error("invalid character")

        return "".join(temp_value)

    temp = []
    string = ""
    token = ""
    state = None
    row = 0
    col = 0

    lines = data.split("\n")

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
        # "switch": "SWITCH",
        # "case": "CASE",
        # "class": "CLASS",
        # "public": "PUBLIC",
        # "private": "PRIVATE",
        # "protected": "PROTECTED",
        # "try": "TRY",
        # "throw": "THROW",
        # "catch": "CATCH",
        # "const": "CONST",
        # "using": "USING",
        # "struct": "STRUCT",
        # "new": "NEW",
        "delete": "DELETE",
        "do": "DO",
        "namespace": "NAMESPACE",
        "break": "BREAK",
        "continue": "CONTINUE",
        "include": "INCLUDE"
    }

    tokens = {
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
        "*": "MULTIPLY",
        "/": "DIVIDE",
        ">": "GREATER",
        "<": "LESS",
        "!": "NOT",
        "|": "VERTICALBAR",
        "&": "AMPERSAND",
        "\"": "QUOTATIONMARK"
    }

    passed_token = [" ", "\n", "\t", "\""]

    row += 1

    for char in data:
        if state == "comment":
            if char == "\n":
                state = None

        elif state == "multicomment":
            if char in ["*", "/"]:
                string += tokens[char]

            if char in ["\n", " "]:
                string = ""

            if "MULTIPLYDIVIDE" in string:
                state = None
                string = ""

        elif char in ["-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]:
            if char in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."] and token != "":
                token += char

            elif state != "string" and state != "name":
                state = "number"

            else:
                string += token
                string += char
                token = ""
            
            if state == "number":
                string += char

        elif char in ["!", "<", ">", "=", "-", "+", "*", "/", "|", "&"]:
            if state == "string":
                if token != "":
                    string += token
                    token = ""

                string += char

            else:
                if char in ["=", "<", ">", "=", "|", "&", "!"] and token != "":
                    if string != "":
                        token = string + token
                        string = ""

                    token = check_str(token)

                    temp.append("NAME")
                    temp.append(token)
                    token = ""

                state = "token"
                string += tokens[char]

                if string == "DIVIDEDIVIDE":
                    state = "comment"
                    string = ""
                    token = ""

                if string == "DIVIDEMULTIPLY":
                    state = "multicomment"
                    string = ""
                    token = ""

                if string == "NOT":
                    temp.append("NOT")
                    string = ""
                    state = None

                if string == "VERTICALBARVERTICALBAR":
                    temp.append("OR")
                    string = ""
                    state = None

                if string == "AMPERSANDAMPERSAND":
                    temp.append("AND")
                    string = ""
                    state = None

        elif char in tokens:
            if char in ["\"", "(", ")", ";", ":", "=", "{"]:
                if (token != "" or string != "") and char in ["(", ")", ";", ":", "=", "{", "}"]:
                    if state == "string":
                        if token != "":
                            string += token
                            token = ""

                        string += char

                    if string == "PLUSPLUS":
                        temp.append("INCREMENT")
                        temp.append(token)
                        string = ""
                        token = ""
                        state = None

                    elif string == "--":
                        temp.append("DECREMENT")
                        temp.append(token)
                        string = ""
                        token = ""
                        state = None

                    if state == "name" and char == ":":
                        string += char

                    elif token != "" and char == ":":
                        token += char

                    if char == ";":
                        if state == "token":
                            if string != "":
                                temp.append(string)
                                string = ""
                                state = None

                            elif token != "":
                                temp.append(token)
                                token = ""
                                state = None

                    if string != "":
                        if state == "number":
                            if "." in string:
                                if string[0] == ".":
                                    string = "0" + string

                                if string[0] == "-" and string[1] == ".":
                                    string = "-" + "0" + string[1:]

                                temp.append("FLOAT")
                                temp.append(string)

                            else:
                                temp.append("INT")
                                temp.append(string)

                            state = None
                            string = ""
                                
                        elif state == "name":
                            if char != ":":
                                string = check_str(string)

                                temp.append("NAME")
                                temp.append(string)
                                
                                state = None
                                string = ""

                    if token != "":
                        if char == "(":
                            if state != "string":
                                temp.append("CALL")
                                temp.append(token)

                                token = ""
                                state = None

                        else:
                            if token != "":
                                if char != ":":
                                    token = check_str(token)

                                    temp.append("NAME")
                                    temp.append(token)
                                    
                                    token = ""
                                    state = None

                elif char in ["\"", "("]:
                    if state == "string" or (char == "(" and state != None):
                        if token != "":
                            string += token
                            token = ""

                        if string != "":
                            temp.append(state.upper())
                            temp.append(string)

                        string = ""
                        state = None

                    elif char == "(":
                        ...

                    else:
                        state = "string"

                        if string != "":
                            temp.append(string)
                            string = ""

                else:
                    if state == "string":
                        string += char

            if char not in passed_token:
                if char in [",", ")", "}"]:
                    if state == "number":
                        if "." in string:
                            if string[0] == ".":
                                string = "0" + string

                            if string[0] == "-" and string[1] == ".":
                                string = "-" + "0" + string[1:]

                            temp.append("FLOAT")
                            temp.append(string)

                        else:
                            temp.append("INT")
                            temp.append(string)

                        string = ""
                        state = None
                        temp.append(tokens[char])

                    elif state == "string":
                        if char != ")": string += char

                    else:
                        if token != "":
                            temp.append("NAME")
                            temp.append(token)
                            token = ""

                        if string != "":
                            temp.append("NAME")
                            temp.append(string)
                            string = ""

                        state = None
                        temp.append(tokens[char])

                else:
                    if state != "string" and state != "name":
                        if token != "" and char == ":":
                            continue

                        temp.append(tokens[char])

        else:
            token += char

            if token in passed_token:
                if state != "string":
                    token = ""

                    if string != "":
                        if state == "name":
                            temp.append("NAME")
                            temp.append(string)

                        if state == "token":
                            if string[0] == "-":
                                string = "MINUS" + string[1:]

                            temp.append(string)

                        elif state == "number":
                            if string == "-":
                                temp.append("MINUS")

                            else:
                                if "." in string:
                                    if string[0] == ".":
                                        string = "0" + string

                                    if string[0] == "-" and string[1] == ".":
                                        string = "-" + "0" + string[1:]

                                    temp.append("FLOAT")
                                    temp.append(string)

                                else:
                                    temp.append("INT")
                                    temp.append(string)

                        string = ""
                        state = None

            elif state == "name" or state == "string":
                string += token
                token = ""

            elif char == "f" and state == "number":
                string += token
                token = ""

            elif char in [" ", "\n", ",", "(", ")", "{", "}", "[", "]"]:
                current = col
                found = False

                while len(lines[row - 1]) >= current and lines[row - 1][current] in ["=", "<", ">", "|", "&", ")", "}", "]", "!", ",", "+", "-", "*", "/", " "]:
                    if lines[row - 1][current] in ["=", "<", ">", "|", "&", ")", "}", "]", "!", ",", "+", "-", "*", "/"]:
                        found = True

                    current += 1

                if token != "" and not found:
                    if state == None:
                        print(f"{file}:{row}:{col}: ", end = "", flush = True)
                        set_text_attr(12)
                        print("error: ", end = "", flush = True)
                        set_text_attr(7)
                        print(f"unexpected token: '{token[:-1]}'", end = "\n", flush = True)

                        print(lines[row - 1][:col - 1 - len(token[:-1])], end = "", flush = True)
                        set_text_attr(12)
                        print(lines[row - 1][col - 1 - len(token[:-1]):col - 1], end = "", flush = True)
                        set_text_attr(7)
                        print(lines[row - 1][col - 1:], end = "\n", flush = True)
                        set_text_attr(12)
                        print(" " * (col - 1 - len(token[:-1])) + "^" + (len(token[:-1]) - 1) * "~", end = "\n", flush = True)
                        set_text_attr(7)

                        similar = difflib.get_close_matches(token, keywords)

                        if len(similar) > 0:
                            print("did you mean", end = " ", flush = True)
                            set_text_attr(10)
                            print(similar[0], end = "", flush = True)
                            set_text_attr(7)
                            print("?")

                        sys.exit(-1)

            elif token in keywords:
                if string != "":
                    temp.append(string)
                    string = ""

                if keywords[token] in ["VOID", "INT", "FLOAT", "BOOL", "STRING", "CLASS", "AUTO", "NAMESPACE"]:
                    state = "name"

                elif keywords[token] in ["TRUE", "FALSE"]:
                    temp.append("BOOL")

                elif keywords[token] in ["NULL"]:
                    temp.append("NULL")

                temp.append(keywords[token])
                token = ""

        if char == "\n" and state != "string":
            row += 1
            col = 0

        col += 1

    if create_json:
        name = os.path.splitext(os.path.split(file)[1])[0]

        if name == "init":
            dirs = os.path.split(file)[0].split("/")
            name = dirs[len(dirs) - 1]

        with open(f"{name}_token.json", "w") as file:
            file.write(json.dumps({"tokens": temp}, indent = 4))

    return temp

def parse_condition(condition_tokens, file, variables, functions):
    pos = 0

    last_token = {"token": None, "value": None}

    def set_text_attr(color):
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32. SetConsoleTextAttribute(console_handle, color)

    def error(message = "failed to parse the condition", file = file, type = "error", terminated = False, suggest = False):
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(12)
        print(f"{type}: ", end = "", flush = True)
        set_text_attr(7)
        print(message + ", current token: " + get(pos), end = "\n", flush = True)
        if terminated: print("program terminated.")
        sys.exit(-1)

    def warning(message, file = file, type = "warning"):
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(13)
        print(f"{type}: ", end = "", flush = True)
        set_text_attr(7)
        print(message, end = "\n", flush = True)

    def get(index):
        try: return condition_tokens[index]
        except: None

    new_tokens = []

    while len(condition_tokens) > pos:
        if last_token["token"] == None or get(pos) != last_token["token"]:
            last_token = {"token": get(pos), "value": 0}

        elif get(pos) == last_token["token"]: last_token["value"] += 1
        if last_token["value"] >= 1000: error()

        if get(pos) == "NAME":
            new_tokens.append(variables[get(pos + 1)]["type"])
            new_tokens.append(variables[get(pos + 1)]["value"])
            pos += 2

        elif get(pos) == "CALL":
            error("function calls in conditions are not implemented")

        else:
            new_tokens.append(get(pos))
            pos += 1

    condition_tokens = new_tokens.copy()
    new_tokens.clear()
    pos = 0

    while len(condition_tokens) > pos:
        if last_token["token"] == None or get(pos) != last_token["token"]:
            last_token = {"token": get(pos), "value": 0}

        elif get(pos) == last_token["token"]: last_token["value"] += 1
        if last_token["value"] >= 1000: error()

        if get(pos) == "LPAREN":
            condition_pos = pos
            condition_pass = 0
            temp_condition_tokens = []

            while True:
                if get(condition_pos) == "LPAREN":
                    condition_pass += 1

                elif get(condition_pos) == "RPAREN":
                    condition_pass -= 1

                    if condition_pass == 0:
                        break

                    condition_pos += 1

                else:
                    temp_condition_tokens.append(get(condition_pos))
                    condition_pos += 1

            new_tokens.append("BOOL")
            new_tokens.append(parse_condition(temp_condition_tokens, file, variables, functions))
            pos = condition_pos + 1

        else:
            new_tokens.append(get(pos))
            pos += 1

    condition_tokens = new_tokens.copy()
    new_tokens.clear()
    pos = 0

    while len(condition_tokens) > pos:
        if last_token["token"] == None or get(pos) != last_token["token"]:
            last_token = {"token": get(pos), "value": 0}

        elif get(pos) == last_token["token"]: last_token["value"] += 1
        if last_token["value"] >= 1000: error()

        if get(pos) == "NOT" and get(pos + 1) != "EQUALS":
            if get(pos + 1) == "BOOL":
                new_tokens.append("BOOL")

                if get(pos + 2) == "TRUE":
                    new_tokens.append("FALSE")

                elif get(pos + 2) == "FALSE":
                    new_tokens.append("TRUE")

                else:
                    error("unexpected value")

            pos += 3

        else:
            new_tokens.append(get(pos))
            pos += 1

    condition_tokens = new_tokens.copy()
    new_tokens.clear()
    pos = 0

    while len(condition_tokens) > pos:
        if last_token["token"] == None or get(pos) != last_token["token"]:
            last_token = {"token": get(pos), "value": 0}

        elif get(pos) == last_token["token"]: last_token["value"] += 1
        if last_token["value"] >= 1000: error()

        if get(pos) == "EQUALSEQUALS":
            left_type = get(pos - 2)
            left_value = get(pos - 1)
            right_type = get(pos + 1)
            right_value = get(pos + 2)

            new_tokens.append("BOOL")

            if left_type in ["INT", "FLOAT"] and right_type in ["INT", "FLOAT"]:
                if (left_type == "INT" and right_type == "FLOAT") or (left_type == "FLOAT" and right_type == "INT"):
                    if right_type == "FLOAT":
                        right_value = float(right_value.replace("f", ""))
                        left_value = float(left_value)

                    elif left_type == "FLOAT":
                        right_value = float(right_value)
                        left_value = float(left_value.replace("f", ""))

                elif (left_type == "INT" and right_type == "INT") or (left_type == "FLOAT" and right_type == "FLOAT"):
                    if left_type == "INT" and right_type == "INT":
                        left_value = int(left_value)
                        right_value = int(right_value)

                    elif left_type == "FLOAT" and right_type == "FLOAT":
                        left_value = float(left_value.replace("f", ""))
                        right_value = float(right_value.replace("f", ""))

                else:
                    error("unexpected error")
                    
                if left_value == right_value:
                    new_tokens.append("TRUE")

                else:
                    new_tokens.append("FALSE")

            elif left_type != right_type:
                new_tokens.append("FALSE")

            elif left_type == "BOOL" and right_type == "BOOL":
                if left_value != right_value:
                    new_tokens.append("FALSE")

                else:
                    new_tokens.append("TRUE")

            elif left_type == "STRING" and right_type == "STRING":
                if left_value != right_value:
                    new_tokens.append("FALSE")

                else:
                    new_tokens.append("TRUE")

            else:
                error("unexpected error")

            pos += 3

        elif get(pos) == "NOT" and get(pos + 1) == "EQUALS":
            left_type = get(pos - 2)
            left_value = get(pos - 1)
            right_type = get(pos + 2)
            right_value = get(pos + 3)

            new_tokens.append("BOOL")

            if left_type in ["INT", "FLOAT"] and right_type in ["INT", "FLOAT"]:
                if (left_type == "INT" and right_type == "FLOAT") or (left_type == "FLOAT" and right_type == "INT"):
                    if right_type == "FLOAT":
                        right_value = float(right_value.replace("f", ""))
                        left_value = float(left_value)

                    elif left_type == "FLOAT":
                        right_value = float(right_value)
                        left_value = float(left_value.replace("f", ""))

                elif (left_type == "INT" and right_type == "INT") or (left_type == "FLOAT" and right_type == "FLOAT"):
                    if left_type == "INT" and right_type == "INT":
                        left_value = int(left_value)
                        right_value = int(right_value)

                    elif left_type == "FLOAT" and right_type == "FLOAT":
                        left_value = float(left_value.replace("f", ""))
                        right_value = float(right_value.replace("f", ""))

                else:
                    error("unexpected error")

                if left_value != right_value:
                    new_tokens.append("TRUE")

                else:
                    new_tokens.append("FALSE")

            elif left_type != right_type:
                new_tokens.append("TRUE")

            elif left_type == "BOOL" and right_type == "BOOL":
                if left_value != right_value:
                    new_tokens.append("TRUE")

                else:
                    new_tokens.append("FALSE")

            elif left_type == "STRING" and right_type == "STRING":
                if left_value != right_value:
                    new_tokens.append("TRUE")

                else:
                    new_tokens.append("FALSE")

            else:
                error("unexpected error")

            pos += 4

        elif get(pos) in ["LESS", "LESSEQUALS", "GREATER", "GREATEREQUALS"]:
            left_type = get(pos - 2)
            left_value = get(pos - 1)
            right_type = get(pos + 1)
            right_value = get(pos + 2)

            new_tokens.append("BOOL")

            if left_type in ["INT", "FLOAT"] and right_type in ["INT", "FLOAT"]:
                if (left_type == "INT" and right_type == "FLOAT") or (left_type == "FLOAT" and right_type == "INT"):
                    if right_type == "FLOAT":
                        right_value = float(right_value.replace("f", ""))
                        left_value = float(left_value)

                    elif left_type == "FLOAT":
                        right_value = float(right_value)
                        left_value = float(left_value.replace("f", ""))

                elif (left_type == "INT" and right_type == "INT") or (left_type == "FLOAT" and right_type == "FLOAT"):
                    if left_type == "INT" and right_type == "INT":
                        left_value = int(left_value)
                        right_value = int(right_value)

                    elif left_type == "FLOAT" and right_type == "FLOAT":
                        left_value = float(left_value.replace("f", ""))
                        right_value = float(right_value.replace("f", ""))

                else:
                    error("unexpected error")

                if get(pos) == "LESS": condition = left_value < right_value
                elif get(pos) == "LESSEQUALS": condition = left_value <= right_value
                elif get(pos) == "GREATER": condition = left_value > right_value
                elif get(pos) == "GREATEREQUALS": condition = left_value >= right_value
                else: error("unexpected error")

                if condition:
                    new_tokens.append("TRUE")

                else:
                    new_tokens.append("FALSE")

            else:
                error("unexpected type")

            pos += 3

        elif get(pos) in ["INT", "FLOAT", "STRING", "BOOL"]:
            if not ((get(pos + 2) in ["EQUALSEQUALS", "LESS", "LESSEQUALS", "GREATER", "GREATEREQUALS"]) or (get(pos + 2) == "NOT" and get(pos + 3) == "EQUALS")):
                new_tokens.append(get(pos))
                new_tokens.append(get(pos + 1))

            pos += 2

        elif get(pos) in ["AND", "OR"]:
            new_tokens.append(get(pos))
            pos += 1

        else:
            error("unexpected token")

    condition_tokens = new_tokens.copy()
    new_tokens.clear()
    pos = 0

    while len(condition_tokens) > pos:
        if last_token["token"] == None or get(pos) != last_token["token"]:
            last_token = {"token": get(pos), "value": 0}

        elif get(pos) == last_token["token"]: last_token["value"] += 1
        if last_token["value"] >= 1000: error()

        if get(pos) == "AND":
            left_type = get(pos - 2)
            left_value = get(pos - 1)
            right_type = get(pos + 1)
            right_value = get(pos + 2)

            new_tokens.append("BOOL")

            if left_type == "BOOL" and right_type == "BOOL":
                if left_value == "TRUE" and right_value == "TRUE":
                    new_tokens.append("TRUE")

                else:
                    new_tokens.append("FALSE")

            else:
                error("unexpected type")

            pos += 3

            for index, i in enumerate(condition_tokens):
                if index >= pos:
                    new_tokens.append(get(index))

            condition_tokens = new_tokens.copy()
            new_tokens.clear()
            pos = 0

        elif get(pos) == "OR":
            left_type = get(pos - 2)
            left_value = get(pos - 1)
            right_type = get(pos + 1)
            right_value = get(pos + 2)

            new_tokens.append("BOOL")

            if left_type == "BOOL" and right_type == "BOOL":
                if left_value == "TRUE" or right_value == "TRUE":
                    new_tokens.append("TRUE")

                else:
                    new_tokens.append("FALSE")

            else:
                error("unexpected type")

            pos += 3

            for index, i in enumerate(condition_tokens):
                if index >= pos:
                    new_tokens.append(get(index))

            condition_tokens = new_tokens.copy()
            new_tokens.clear()
            pos = 0

        elif get(pos) == "BOOL":
            if get(pos + 2) not in ["AND", "OR"]:
                new_tokens.append(get(pos))
                new_tokens.append(get(pos + 1))

            pos += 2

        else:
            error("unexpected token")

    if len(new_tokens) == 2:
        if new_tokens[0] == "BOOL":
            if new_tokens[1] == "TRUE":
                return True

            elif new_tokens[1] == "FALSE":
                return False

            else:
                error("unexpected value")

        else:
            error("unexpected type")

    else:
        error("unexpected error")

def parser(tokens, file, create_json):
    ast = []
    pos = 0

    last_token = {"token": None, "value": None}

    def set_text_attr(color):
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32. SetConsoleTextAttribute(console_handle, color)

    def error(message = "failed to generate the ast", file = file, type = "error", terminated = False, suggest = False):
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(12)
        print(f"{type}: ", end = "", flush = True)
        set_text_attr(7)
        print(message + ", current token: " + get(pos), end = "\n", flush = True)
        if terminated: print("program terminated.")

        if suggest:
            if last_token["token"] in ["CALL", "RETURN", "STRING", "AUTO", "INT", "FLOAT", "BOOL", "NAME"]:
                print("did you forget to put a semicolon?")

        sys.exit(-1)

    def warning(message, file = file, type = "warning"):
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(13)
        print(f"{type}: ", end = "", flush = True)
        set_text_attr(7)
        print(message, end = "\n", flush = True)

    def get(index):
        try: return tokens[index]
        except: error()

    def get_call_args(current_pos):
        temp_tokens = []
        args = []
        ignore = 0

        while True:
            if get(current_pos) == "LPAREN":
                if ignore != 0:
                    temp_tokens.append("LPAREN")

                ignore += 1
                current_pos += 1

            elif get(current_pos) == "RPAREN":
                ignore -= 1

                if ignore == 0:
                    if len(temp_tokens) != 0:
                        temp_tokens.append("SEMICOLON")
                        args.append(parser(temp_tokens, file, create_json)[0])
                        temp_tokens.clear()

                    break

                temp_tokens.append("RPAREN")
                current_pos += 1

            elif get(current_pos) == "COMMA":
                if ignore == 1:
                    if len(temp_tokens) != 0:
                        temp_tokens.append("SEMICOLON")
                        args.append(parser(temp_tokens, file, create_json)[0])
                        temp_tokens.clear()
                
                else:
                    temp_tokens.append("COMMA")

                current_pos += 1
            
            else:
                temp_tokens.append(get(current_pos))
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

            elif get(current_pos) == "NAME":
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
                    temp_tokens.append(get(current_pos))
                    break

                else:
                    temp_tokens.append(get(current_pos))
                    current_pos += 1

        else:
            while True:
                if get(current_pos) == "LCURLYBRACKET":
                    if ignore != 0:
                        temp_tokens.append(get(current_pos))

                    ignore += 1
                    current_pos += 1

                elif get(current_pos) == "RCURLYBRACKET":
                    ignore -= 1

                    if ignore == 0:
                        break

                    temp_tokens.append(get(current_pos))
                    current_pos += 1

                else:
                    temp_tokens.append(get(current_pos))
                    current_pos += 1

        return parser(temp_tokens, file, create_json), current_pos + 1

    while len(tokens) > pos:
        if last_token["token"] == None or get(pos) != last_token["token"]:
            last_token = {"token": get(pos), "value": 0}

        elif get(pos) == last_token["token"]: last_token["value"] += 1
        if last_token["value"] >= 1000: error()

        if get(pos) == "NAMESPACE":
            if get(pos + 1) == "NAME":
                if get(pos + 3) == "LCURLYBRACKET":
                    name = get(pos + 2)
                    temp_ast, pos = get_func_ast(pos + 3)

                    if "." in name:
                        error("invalid character", suggest = False)

                    ast.append({"type": "namespace", "name": name, "ast": temp_ast})
                    pos += 1

        elif get(pos) == "NOT":
            temp_tokens = []
            pos += 1

            while True:
                if get(pos) == "SEMICOLON":
                    temp_tokens.append(get(pos))
                    break

                else:
                    temp_tokens.append(get(pos))
                    pos += 1

            if get(pos) == "SEMICOLON":
                ast.append({"type": "not", "value": parser(temp_tokens, file, create_json)[0]})
                pos += 1

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
                ast.append({"type": "for", "ast": temp_ast, "init": parser(temp_tokens[0], file, False), "condition": temp_tokens[1], "update": parser(temp_tokens[2], file, False)})

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
                ast.append({"type": name, "ast": temp_ast, "condition": condition_tokens})

            else:
                ast.append({"type": name, "ast": temp_ast})

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

                pos = condition_pos + 1
                ast.append({"type": "do while", "ast": temp_ast, "condition": condition_tokens})

                if get(pos) == "SEMICOLON":
                    pos += 1

            else:
                ast.append({"type": "do", "ast": temp_ast})

        elif get(pos) == "RETURN":
            temp_tokens = []
            type = get(pos + 1)
            pos += 1

            while True:
                if get(pos) == "SEMICOLON":
                    temp_tokens.append(get(pos))
                    break

                else:
                    temp_tokens.append(get(pos))
                    pos += 1

            if get(pos) == "SEMICOLON":
                ast.append({"type": "return", "value": parser(temp_tokens, file, create_json)[0]})
                pos += 1

        elif get(pos) == "DELETE":
            if get(pos + 3) == "SEMICOLON":
                if get(pos + 1) == "NAME":
                    ast.append({"type": get(pos).lower(), "value": get(pos + 2)})
                    pos += 4

        elif get(pos) == "INCLUDE":
            if get(pos + 3) == "SEMICOLON":
                if get(pos + 1) == "STRING":
                    ast.append({"type": get(pos).lower(), "all": False, "value": get(pos + 2)})
                    pos += 4

            elif get(pos + 3) == "COLON":
                if get(pos + 5) == "SEMICOLON":
                    if get(pos + 4) == "MULTIPLY":
                        if get(pos + 1) == "STRING":
                            ast.append({"type": "include", "all": True, "value": get(pos + 2)})
                            pos += 6

        elif get(pos) in ["BREAK", "CONTINUE"]:
            if get(pos + 1) == "SEMICOLON":
                ast.append({"type": get(pos).lower()})
                pos += 2

        elif get(pos) in ["INCREMENT", "DECREMENT"]:
            ast.append({"type": get(pos).lower(), "value": get(pos + 1)})
            pos += 3

        elif get(pos) == "LPAREN":
            if get(pos + 2) == "RPAREN":
                temp_tokens = []
                type = get(pos + 1)
                pos += 3

                while True:
                    if get(pos) == "SEMICOLON":
                        temp_tokens.append(get(pos))
                        break

                    else:
                        temp_tokens.append(get(pos))
                        pos += 1

                if get(pos) == "SEMICOLON":
                    ast.append({"type": "cast", "cast_type": type, "value": parser(temp_tokens, file, create_json)[0]})
                    pos += 1

        elif get(pos) == "NAME":
            if get(pos + 2) == "EQUALS":
                temp_tokens = []
                name = get(pos + 1)
                pos += 3

                while True:
                    if get(pos) == "SEMICOLON":
                        temp_tokens.append(get(pos))
                        break

                    else:
                        temp_tokens.append(get(pos))
                        pos += 1

                if get(pos) == "SEMICOLON":
                    ast.append({"type": "var", "value_type": None, "name": name, "value": parser(temp_tokens, file, create_json)[0]})
                    pos += 1

            else:
                if get(pos + 2) == "SEMICOLON":
                    ast.append({"type": "NAME", "value": get(pos + 1)})
                    pos += 3

        elif get(pos) == "CALL":
            if get(pos + 2) == "LPAREN":
                name = get(pos + 1)
                args, pos = get_call_args(pos + 2)

                if get(pos) == "SEMICOLON":
                    ast.append({"type": "call", "name": name, "args": args})
                    pos += 1

                else:
                    error("expected ';'")

        elif get(pos) in ["VOID", "BOOL", "INT", "FLOAT", "STRING", "AUTO"]:
            if get(pos + 2) == "SEMICOLON":
                ast.append({"type": get(pos), "value": get(pos + 1)})
                pos += 3

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
                        ast.append({"type": "var", "value_type": type, "name": name, "value": parser(temp_tokens, file, create_json)[0]})
                        pos += 1

                elif get(pos + 3) == "SEMICOLON":
                    if get(pos + 1) == "NAME":
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

    if create_json:
        name = os.path.splitext(os.path.split(file)[1])[0]

        if name == "init":
            dirs = os.path.split(file)[0].split("/")
            name = dirs[len(dirs) - 1]

        with open(f"{name}_ast.json", "w") as file:
            file.write(json.dumps(ast, indent = 4))

    return ast

def interpreter(ast, file, isbase, islib, functions, variables, return_type, library_functions, include_folders, create_json, already_included = [], pre_included = []):
    def set_text_attr(color):
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32. SetConsoleTextAttribute(console_handle, color)

    def error(msg, file = file, type = "error", terminated = False):
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(12)
        print(f"{type}: ", end = "", flush = True)
        set_text_attr(7)
        print(msg, end = "\n", flush = True)
        if terminated: print("program terminated.")
        sys.exit(-1)

    def warning(message, file = file, type = "warning"):
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(13)
        print(f"{type}: ", end = "", flush = True)
        set_text_attr(7)
        print(message, end = "\n", flush = True)

    def define_standards(file, functions, variables, library_functions, include_folders):
        library_functions.update(std.std["functions"])
        variables["__file__"] = {"type": "STRING", "value": {file: "STRING"}}

    def proccess_string(string):
        return string.replace("\\n", "\n").replace("\\\\", "\\").replace("\\t", "\t").replace("\\\"", "\"")

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
                    error_code = interpreter(functions[i["name"]]["ast"], file, False, False, functions, variables, i["return_type"], library_functions, include_folders, create_json)
                    
                    if error_code in ["BREAK", "CONTINUE"]:
                        error("cant use '" + error_code.lower() + "' here")

                    elif error_code["type"] == "NULL":
                        error("non-void functions should return a value")

                    else:
                        if error_code["type"] == "INT":
                            error_code = error_code["value"]

        elif i["type"] == "namespace":
            temp_variables, temp_functions, temp_library_functions = interpreter(i["ast"], file, False, False, functions.copy(), variables.copy(), None, library_functions.copy(), include_folders, create_json)
            
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
                        variables[i["value"]]["value"] = str(float(variables[i["value"]]["value"]).lower().replace("f", "")) + (1 if i["type"] == "increment" else -1) + "f"

                    else:
                        error("unknown error")

                else:
                    error("'" + i["value"] + "' should be an integer or float value")

        elif i["type"] in ["break", "continue"]:
            if isbase: error("cant use '" + i["type"] + "' here")
            return i["type"].upper()
                
        elif i["type"] == "var":
            value = interpreter([i["value"]], file, False, False, functions, variables, "VOID", library_functions, include_folders, create_json)

            if i["value_type"] == None:
                if i["name"] in variables:
                    if value["type"] != variables[i["name"]]["type"]:
                        value = interpreter([{"type": "cast", "cast_type": variables[i["name"]]["type"], "value": value}], file, False, False, functions, variables, "VOID", library_functions, include_folders, create_json)
                        
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
                        value = interpreter([{"type": "cast", "cast_type": i["value_type"], "value": value}], file, False, False, functions, variables, "VOID", library_functions, include_folders, create_json)
                        
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

                temp = interpreter(parser(lexer(tools.read_file(file_path), file_path, create_json), file_path, create_json), file_path, False, True, {}, {}, None, {}, include_folders, create_json)

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

        elif i["type"] in ["NAME", "AUTO", "BOOL", "STRING", "INT", "FLOAT", "VOID", "NULL"]:
            if i["type"] == "NAME":
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
            value = interpreter([i["value"]], file, False, False, functions, variables, "VOID", library_functions, include_folders, create_json)

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
            value = interpreter([i["value"]], file, False, False, functions, variables, "VOID", library_functions, include_folders, create_json)
            
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
                    return {"type": "INT", "value": str(int(str(value["value"]).lower().replace("f", "")))}

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

        elif i["type"] == "for":
            sec_temp_variables, sec_temp_functions, sec_temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            interpreter(i["init"].copy(), file, False, False, functions, variables, None, library_functions, include_folders, create_json)
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            condition = parse_condition(i["condition"].copy(), file, variables, functions) if len(i["condition"]) != 0 else True

            while condition:
                response = interpreter(i["ast"].copy(), file, False, False, functions, variables, None, library_functions, include_folders, create_json)
                interpreter(i["update"].copy(), file, False, False, functions, variables, None, library_functions, include_folders, create_json)
                condition = parse_condition(i["condition"].copy(), file, variables, functions) if len(i["condition"]) != 0 else True

                for j in list(set(variables) - set(temp_variables)): del variables[j]
                for j in list(set(functions) - set(temp_functions)): del functions[j]
                for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]
                if response == "BREAK": break

            for j in list(set(variables) - set(sec_temp_variables)): del variables[j]
            for j in list(set(functions) - set(sec_temp_functions)): del functions[j]
            for j in list(set(library_functions) - set(sec_temp_library_functions)): del library_functions[j]

        elif i["type"] == "do":
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            response = interpreter(i["ast"].copy(), file, False, False, functions, variables, None, library_functions, include_folders, create_json)

            for j in list(set(variables) - set(temp_variables)): del variables[j]
            for j in list(set(functions) - set(temp_functions)): del functions[j]
            for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]

            if response == "BREAK": break

        elif i["type"] == "do while":
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            interpreter(i["ast"].copy(), file, False, False, functions, variables, None, library_functions, include_folders, create_json)
            result_report[index] = parse_condition(i["condition"].copy(), file, variables, functions)

            while result_report[index]:
                response = interpreter(i["ast"].copy(), file, False, False, functions, variables, None, library_functions, include_folders, create_json)
                result_report[index] = parse_condition(i["condition"].copy(), file, variables, functions)

                for j in list(set(variables) - set(temp_variables)): del variables[j]
                for j in list(set(functions) - set(temp_functions)): del functions[j]
                for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]
                if response == "BREAK": break

            for j in list(set(variables) - set(temp_variables)): del variables[j]
            for j in list(set(functions) - set(temp_functions)): del functions[j]
            for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]

        elif i["type"] == "while":
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            result_report[index] = parse_condition(i["condition"].copy(), file, variables, functions)

            while result_report[index]:
                response = interpreter(i["ast"].copy(), file, False, False, functions, variables, None, library_functions, include_folders, create_json)
                result_report[index] = parse_condition(i["condition"].copy(), file, variables, functions)

                for j in list(set(variables) - set(temp_variables)): del variables[j]
                for j in list(set(functions) - set(temp_functions)): del functions[j]
                for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]
                if response == "BREAK": break

        elif i["type"] == "if":
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()
            result_report[index] = parse_condition(i["condition"].copy(), file, variables, functions)

            if result_report[index]:
                response = interpreter(i["ast"].copy(), file, False, False, functions, variables, None, library_functions, include_folders, create_json)
                if response in ["BREAK", "CONTINUE"]: return response

                for j in list(set(variables) - set(temp_variables)): del variables[j]
                for j in list(set(functions) - set(temp_functions)): del functions[j]
                for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]

        elif i["type"] == "else if":
            temp_variables, temp_functions, temp_library_functions = variables.copy(), functions.copy(), library_functions.copy()

            if ast[index]["type"] in ["if", "else if"] and (index - 1 in result_report):
                if not result_report[index - 1]:
                    result_report[index] = parse_condition(i["condition"], file, variables, functions)

                    if result_report[index]:
                        response = interpreter(i["ast"].copy(), file, False, False, functions, variables, None, library_functions, include_folders, create_json)
                        if response in ["BREAK", "CONTINUE"]: return response

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

                if not result_report[index - 1]:
                    response = interpreter(i["ast"].copy(), file, False, False, functions, variables, None, library_functions, include_folders, create_json)
                    if response in ["BREAK", "CONTINUE"]: return response

                    for j in list(set(variables) - set(temp_variables)): del variables[j]
                    for j in list(set(functions) - set(temp_functions)): del functions[j]
                    for j in list(set(library_functions) - set(temp_library_functions)): del library_functions[j]

            else:
                error("couldn't find any statements")

        elif i["type"] == "return":
            if isbase or islib:
                error("return can only be used in functions")

            if return_type == None:
                error("return can only be used in functions")

            if return_type == "VOID":
                if i["value"]["type"] != None:
                    error("can't return any value in non-void functions")

            returned = interpreter([i["value"]], file, False, False, functions, variables, "VOID", library_functions, include_folders, create_json)

            if returned["type"] != return_type:
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
                        temp.append(interpreter([j], file, False, False, functions, variables, None, library_functions, include_folders, create_json))

                    for index, j in enumerate(library_functions[i["name"]]["args"].values()):
                        if temp[index]["type"] != j and temp[index]["type"] not in ["NULL"]:
                            temp[index] = interpreter([{"type": "cast", "cast_type": j, "value": temp[index]}], file, False, False, functions, variables, "INT", library_functions, include_folders, create_json)
                        
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
                            new_temp[name] = proccess_string(j["value"])

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
                        "include_folders": include_folders,
                        "create_json": create_json
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
                        temp.append(interpreter([j], file, False, False, functions, variables, None, library_functions, include_folders, create_json))

                    for index, j in enumerate(functions[i["name"]]["args"].values()):
                        if temp[index]["type"] != j and temp[index]["type"] not in ["NULL"]:
                            temp[index] = interpreter([{"type": "cast", "cast_type": j, "value": temp[index]}], file, False, False, functions, variables, None, library_functions, include_folders, create_json)

                    temp_vars = variables.copy()

                    for index, j in enumerate(functions[i["name"]]["args"].keys()):
                        if functions[i["name"]]["args"][j] == temp[index]["type"]:
                            temp_vars[j] = temp[index]

                    returned = interpreter(functions[i["name"]]["ast"], file, False, False, functions.copy(), temp_vars, functions[i["name"]]["type"], library_functions, include_folders, create_json)

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
        if return_type != None and return_type != "VOID":
            error("non-void functions should return a value")

        elif return_type == None:
            return variables, functions, library_functions

def main(argv):
    def get(index, message, file, type = "error", terminated = False):
        try: return argv[index + 1]
        except IndexError: tools.error(message, file, type, terminated)

    version = "0.0.8"

    file = get(0, "no input files", "rsharp", "fatal error", True)

    include_folders = [f"{tools.get_dir()}\\include\\", "C:\\RSharp\\include\\", ".\\include\\", ".\\"]
    create_json = False
    console = True

    for i in argv:
        if i.startswith("-I"):
            include_folders.append(i[2:])

        elif i.startswith("-l"):
            command = i[2:]

            if command == "json":
                create_json = True

            elif command == "noconsole":
                console = False

    if "--interprete" in argv:
        interpreter(parser(lexer(tools.read_file(file), file, create_json), file, create_json), file, True, False, {}, {}, None, {}, include_folders, create_json)

    elif "--transpile-python" in argv:
        transpiler.python(parser(lexer(tools.read_file(file), file, create_json), file, create_json), file)

    elif "--compile" in argv:
        variables, functions, library_functions, files = tools.auto_include(
            file = file,
            include_folders = include_folders
        )

        builder.build_program(
            path = file,
            include_folders = include_folders,
            console = console,
            variables = variables,
            functions = functions,
            library_functions = library_functions,
            pre_included = files,
        )

    elif "--version" in argv:
        print(f"R# {version}")

    else:
        interpreter(parser(lexer(tools.read_file(file), file, create_json), file, create_json), file, True, False, {}, {}, None, {}, include_folders, create_json)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))