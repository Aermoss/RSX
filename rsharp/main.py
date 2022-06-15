import sys, os

sys.dont_write_bytecode = True

import importlib
import ctypes, ctypes.util
import difflib, json
import string as strlib

import rsharp.transpiler as transpiler
import rsharp.tools as tools
import rsharp.std as std

def lexer(data, file, create_json):
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
        "class": "CLASS",
        "return": "RETURN",
        "not": "NOT",
        "and": "AND",
        "or": "OR",
        "false": "FALSE",
        "true": "TRUE",
        "null": "NULL",
        "if": "IF",
        "else": "ELSE",
        "while": "WHILE",
        "for": "FOR",
        "switch": "SWITCH",
        "case": "CASE",
        "public": "PUBLIC",
        "private": "PRIVATE",
        "protected": "PROTECTED",
        "try": "TRY",
        "throw": "THROW",
        "catch": "CATCH",
        "const": "CONST",
        "using": "USING",
        "namespace": "NAMESPACE",
        "struct": "STRUCT",
        "break": "BREAK",
        "continue": "CONTINUE",
        "new": "NEW",
        "delete": "DELETE",
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

                if string == "VERTICALBARVERTICALBAR":
                    temp.append("OR")
                    string = ""

                if string == "AMPERSANDAMPERSAND":
                    temp.append("AND")
                    string = ""

        elif char in tokens:
            if char in ["\"", "(", ")", ";", ":", "=", "{"]:
                if (token != "" or string != "") and char in ["(", ")", ";", ":", "=", "{", "}"]:
                    if state == "string":
                        if token != "":
                            string += token
                            token = ""

                        string += char

                    if state == "name" and char == ":":
                        string += char

                    elif token != "" and char == ":":
                        token += char

                    if char == ";":
                        if state == "token":
                            if string == "PLUSPLUS":
                                temp.append("INCREMENT")
                                temp.append(token)

                            elif string == "--":
                                temp.append("DECREMENT")
                                temp.append(token)

                            else:
                                temp.append(string)

                            string = ""
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
                                if string == "--":
                                    temp.append("DECREMENT")
                                    temp.append(token)
                                    token = ""

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

                while len(lines[row - 1]) >= current and lines[row - 1][current] in ["=", "<", ">", "|", "&", ")", "}", "]", ",", " "]:
                    if lines[row - 1][current] in ["=", "<", ">", "|", "&", ")", "}", "]", ","]:
                        found = True

                    current += 1

                if token != "" and not found:
                    if state == None:
                        print(f"{file}:{row}:{col}: ", end = "", flush = True)
                        set_text_attr(12)
                        print("error: ", end = "", flush = True)
                        set_text_attr(7)
                        print(f"'{token[:-1]}' was not declared in this scope", end = "\n", flush = True)

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

def parser(tokens, file, create_json):
    ast = []
    pos = 0

    last_token = {"token": None, "value": None}

    def set_text_attr(color):
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32. SetConsoleTextAttribute(console_handle, color)

    def error(msg = "failed to generate the ast", file = file, type = "error", terminated = False, suggest = False):
        print(f"{file}:", end = " ", flush = True)
        set_text_attr(12)
        print(f"{type}: ", end = "", flush = True)
        set_text_attr(7)
        print(msg, end = "\n", flush = True)
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

    while len(tokens) > pos:
        if last_token["token"] == None or get(pos) != last_token["token"]:
            last_token = {"token": get(pos), "value": 0}

        elif get(pos) == last_token["token"]: last_token["value"] += 1
        if last_token["value"] >= 1000: error()

        if get(pos) == "NAMESPACE":
            if get(pos + 1) == "NAME":
                if get(pos + 3) == "LCURLYBRACKET":
                    new_tokens = []
                    new_pos = pos + 4
                    ignore = 0

                    while True:
                        if get(new_pos) == "LCURLYBRACKET":
                            new_tokens.append(get(new_pos))
                            new_pos += 1
                            ignore += 1

                        elif get(new_pos) == "RCURLYBRACKET":
                            if ignore == 0:
                                break

                            else:
                                new_tokens.append(get(new_pos))
                                new_pos += 1
                                ignore -= 1

                        else:
                            new_tokens.append(get(new_pos))
                            new_pos += 1

                    if "." in get(pos + 2): error("invalid character", suggest = False)
                    ast.append({"type": "namespace", "name": get(pos + 2), "ast": parser(new_tokens, file, create_json)})
                    pos = new_pos + 1

        elif get(pos) == "RETURN":
            if get(pos + 1) == "SEMICOLON":
                ast.append({"type": get(pos).lower(), "value": {None: None}})
                pos += 2

            elif get(pos + 3) == "SEMICOLON":
                ast.append({"type": get(pos).lower(), "value": {get(pos + 1): get(pos + 2)}})
                pos += 4

            elif get(pos + 1) == "CALL":
                if get(pos + 3) == "LPAREN":
                    args, arg_value = [], None
                    arg_pos = pos + 4
                    arg_ignore = 0

                    while True:
                        if get(arg_pos) == "LPAREN":
                            arg_ignore += 1
                            arg_pos += 1

                        elif get(arg_pos) == "RPAREN":
                            if arg_ignore == 0:
                                if arg_value != None:
                                    args.append(arg_value)
                                    arg_value = None

                                break

                            else:
                                arg_ignore -= 1
                                arg_pos += 1

                        elif get(arg_pos) in ["VOID", "BOOL", "INT", "FLOAT", "STRING", "NAME", "NULL"]:
                            arg_value = {"type": get(arg_pos), "value": get(arg_pos + 1)}
                            arg_pos += 2

                        elif get(arg_pos) == "CALL":
                            name = get(arg_pos + 1)
                            new_arg_pos = arg_pos + 2
                            new_arg_ignore = 0
                            new_tokens = []

                            new_tokens.append("CALL")
                            new_tokens.append(name)

                            while True:
                                if get(new_arg_pos) == "LPAREN":
                                    new_tokens.append("LPAREN")
                                    new_arg_ignore += 1
                                    new_arg_pos += 1

                                elif get(new_arg_pos) == "RPAREN":
                                    new_tokens.append("RPAREN")
                                    new_arg_ignore -= 1
                                    new_arg_pos += 1

                                    if new_arg_ignore == 0:
                                        break
                            
                                else:
                                    new_tokens.append(get(new_arg_pos))
                                    new_arg_pos += 1

                            new_tokens.append("SEMICOLON")

                            arg_value = parser(new_tokens, file, create_json)[0]
                            arg_pos = new_arg_pos

                        elif get(arg_pos) == "COMMA":
                            if arg_value != None:
                                args.append(arg_value)
                                arg_value = None

                            arg_pos += 1

                    if get(arg_pos + 1) == "SEMICOLON":
                        ast.append({"type": get(pos).lower(), "value": {"type": "call", "name": get(pos + 2), "args": args}})
                        pos = arg_pos + 2

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

        elif get(pos) == "NAME":
            if get(pos + 2) == "EQUALS":
                if get(pos + 3) == "CALL":
                    if get(pos + 5) == "LPAREN":
                        args, arg_value = [], None
                        arg_pos = pos + 6
                        arg_ignore = 0

                        while True:
                            if get(arg_pos) == "LPAREN":
                                arg_ignore += 1
                                arg_pos += 1

                            elif get(arg_pos) == "RPAREN":
                                if arg_ignore == 0:
                                    if arg_value != None:
                                        args.append(arg_value)
                                        arg_value = None

                                    break

                                else:
                                    arg_ignore -= 1
                                    arg_pos += 1

                            elif get(arg_pos) in ["VOID", "BOOL", "INT", "FLOAT", "STRING", "NAME", "NULL"]:
                                arg_value = {"type": get(arg_pos), "value": get(arg_pos + 1)}
                                arg_pos += 2

                            elif get(arg_pos) == "CALL":
                                name = get(arg_pos + 1)
                                new_arg_pos = arg_pos + 2
                                new_arg_ignore = 0
                                new_tokens = []

                                new_tokens.append("CALL")
                                new_tokens.append(name)

                                while True:
                                    if get(new_arg_pos) == "LPAREN":
                                        new_tokens.append("LPAREN")
                                        new_arg_ignore += 1
                                        new_arg_pos += 1

                                    elif get(new_arg_pos) == "RPAREN":
                                        new_tokens.append("RPAREN")
                                        new_arg_ignore -= 1
                                        new_arg_pos += 1

                                        if new_arg_ignore == 0:
                                            break
                                
                                    else:
                                        new_tokens.append(get(new_arg_pos))
                                        new_arg_pos += 1

                                new_tokens.append("SEMICOLON")

                                arg_value = parser(new_tokens, file, create_json)[0]
                                arg_pos = new_arg_pos

                            elif get(arg_pos) == "COMMA":
                                if arg_value != None:
                                    args.append(arg_value)
                                    arg_value = None

                                arg_pos += 1

                        if get(arg_pos + 1) == "SEMICOLON":
                            ast.append({"type": "var", "value_type": None, "name": get(pos + 1), "value": {"type": "call", "name": get(pos + 4), "args": args}})
                            pos = arg_pos + 2

                elif get(pos + 5) == "SEMICOLON":
                    ast.append({"type": "var", "value_type": None, "name": get(pos + 1), "value": {get(pos + 4): get(pos + 3)}})
                    pos += 6

        elif get(pos) == "CALL":
            if get(pos + 2) == "LPAREN":
                args, arg_value = [], None
                arg_pos = pos + 3
                arg_ignore = 0

                while True:
                    if get(arg_pos) == "LPAREN":
                        arg_ignore += 1
                        arg_pos += 1

                    elif get(arg_pos) == "RPAREN":
                        if arg_ignore == 0:
                            if arg_value != None:
                                args.append(arg_value)
                                arg_value = None

                            break

                        else:
                            arg_ignore -= 1
                            arg_pos += 1

                    elif get(arg_pos) in ["VOID", "BOOL", "INT", "FLOAT", "STRING", "NAME", "NULL"]:
                        arg_value = {"type": get(arg_pos), "value": get(arg_pos + 1)}
                        arg_pos += 2

                    elif get(arg_pos) == "CALL":
                        name = get(arg_pos + 1)
                        new_arg_pos = arg_pos + 2
                        new_arg_ignore = 0
                        new_tokens = []

                        new_tokens.append("CALL")
                        new_tokens.append(name)

                        while True:
                            if get(new_arg_pos) == "LPAREN":
                                new_tokens.append("LPAREN")
                                new_arg_ignore += 1
                                new_arg_pos += 1

                            elif get(new_arg_pos) == "RPAREN":
                                new_tokens.append("RPAREN")
                                new_arg_ignore -= 1
                                new_arg_pos += 1

                                if new_arg_ignore == 0:
                                    break
                        
                            else:
                                new_tokens.append(get(new_arg_pos))
                                new_arg_pos += 1

                        new_tokens.append("SEMICOLON")

                        arg_value = parser(new_tokens, file, create_json)[0]
                        arg_pos = new_arg_pos

                    elif get(arg_pos) == "COMMA":
                        if arg_value != None:
                            args.append(arg_value)
                            arg_value = None

                        arg_pos += 1

                if get(arg_pos + 1) == "SEMICOLON":
                    ast.append({"type": "call", "name": get(pos + 1), "args": args})
                    pos = arg_pos + 2

        elif get(pos) in ["VOID", "BOOL", "INT", "FLOAT", "STRING", "AUTO"]:
            if get(pos + 3) == "EQUALS" or get(pos + 3) == "SEMICOLON":
                if get(pos + 3) == "EQUALS":
                    if get(pos + 4) == "CALL":
                        if get(pos + 6) == "LPAREN":
                            args, arg_value = [], None
                            arg_pos = pos + 7
                            arg_ignore = 0

                            while True:
                                if get(arg_pos) == "LPAREN":
                                    arg_ignore += 1
                                    arg_pos += 1

                                elif get(arg_pos) == "RPAREN":
                                    if arg_ignore == 0:
                                        if arg_value != None:
                                            args.append(arg_value)
                                            arg_value = None

                                        break

                                    else:
                                        arg_ignore -= 1
                                        arg_pos += 1

                                elif get(arg_pos) in ["VOID", "BOOL", "INT", "FLOAT", "STRING", "NAME", "NULL"]:
                                    arg_value = {"type": get(arg_pos), "value": get(arg_pos + 1)}
                                    arg_pos += 2

                                elif get(arg_pos) == "CALL":
                                    name = get(arg_pos + 1)
                                    new_arg_pos = arg_pos + 2
                                    new_arg_ignore = 0
                                    new_tokens = []

                                    new_tokens.append("CALL")
                                    new_tokens.append(name)

                                    while True:
                                        if get(new_arg_pos) == "LPAREN":
                                            new_tokens.append("LPAREN")
                                            new_arg_ignore += 1
                                            new_arg_pos += 1

                                        elif get(new_arg_pos) == "RPAREN":
                                            new_tokens.append("RPAREN")
                                            new_arg_ignore -= 1
                                            new_arg_pos += 1

                                            if new_arg_ignore == 0:
                                                break
                                    
                                        else:
                                            new_tokens.append(get(new_arg_pos))
                                            new_arg_pos += 1

                                    new_tokens.append("SEMICOLON")

                                    arg_value = parser(new_tokens, file, create_json)[0]
                                    arg_pos = new_arg_pos

                                elif get(arg_pos) == "COMMA":
                                    if arg_value != None:
                                        args.append(arg_value)
                                        arg_value = None

                                    arg_pos += 1

                            if get(arg_pos + 1) == "SEMICOLON":
                                if "." in get(pos + 2): error("invalid character", suggest = False)
                                if ":" in get(pos + 2): error("invalid character", suggest = False)
                                ast.append({"type": "var", "value_type": get(pos), "name": get(pos + 2), "value": {"type": "call", "name": get(pos + 5), "args": args}})
                                pos = arg_pos + 2

                    else:
                        if "." in get(pos + 2): error("invalid character", suggest = False)
                        if ":" in get(pos + 2): error("invalid character", suggest = False)
                        ast.append({"type": "var", "value_type": get(pos + 4) if get(pos) == "AUTO" else get(pos), "name": get(pos + 2), "value": {get(pos + 5): get(pos + 4)}})

                        if get(pos + 6) == "SEMICOLON" and get(pos + 1) == "NAME" and (get(pos + 4) in (get(pos), "NULL", "NAME") or get(pos) == "AUTO"):
                            pos += 7

                        else:
                            if not (get(pos + 4) in (get(pos), "NULL", "NAME") or get(pos) == "AUTO"):
                                error("invalid conversion from" + " " + "'" + get(pos + 4).lower() + "'" + " " + "to" + " " + "'" + get(pos).lower() + "'")

                            else:
                                error()

                elif get(pos + 3) == "SEMICOLON":
                    if "." in get(pos + 2): error("invalid character", suggest = False)
                    if ":" in get(pos + 2): error("invalid character", suggest = False)
                    ast.append({"type": "var", "value_type": get(pos), "name": get(pos + 2), "value": None})

                    if get(pos + 1) == "NAME":
                        pos += 4

                    else:
                        error()

            elif get(pos + 3) == "LPAREN":
                args, arg_type, arg_name = {}, None, None
                arg_pos = pos + 4
                arg_ignore = 0

                while True:
                    if get(arg_pos) == "LPAREN":
                        arg_ignore += 1
                        arg_pos += 1

                    elif get(arg_pos) == "RPAREN":
                        if arg_ignore == 0:
                            if arg_name != None and arg_type != None:
                                args[arg_name] = arg_type
                                arg_type, arg_name = None, None

                            break

                        else:
                            arg_ignore -= 1
                            arg_pos += 1

                    elif get(arg_pos) in ["VOID", "BOOL", "INT", "FLOAT", "STRING"]:
                        arg_type = get(arg_pos)
                        arg_pos += 1

                    elif get(arg_pos) == "NAME":
                        arg_name = get(arg_pos + 1)
                        arg_pos += 2

                    elif get(arg_pos) == "COMMA":
                        if arg_name != None and arg_type != None:
                            args[arg_name] = arg_type
                            arg_type, arg_name = None, None

                        arg_pos += 1

                if get(arg_pos + 1) == "SEMICOLON":
                    if "." in get(pos + 2): error("invalid character", suggest = False)
                    if ":" in get(pos + 2): error("invalid character", suggest = False)
                    ast.append({"type": "func", "return_type": get(pos), "name": get(pos + 2), "args": args, "ast": []})
                    pos = arg_pos + 2

                elif get(arg_pos + 1) == "LCURLYBRACKET":
                    func_pos, func_tokens = arg_pos + 2, []
                    func_pass = 0

                    while True:
                        if get(func_pos) == "LCURLYBRACKET":
                            func_tokens.append(get(func_pos))
                            func_pass += 1
                            func_pos += 1

                        elif get(func_pos) == "RCURLYBRACKET":
                            if func_pass == 0:
                                break

                            else:
                                func_tokens.append(get(func_pos))
                                func_pass -= 1
                                func_pos += 1

                        else:
                            func_tokens.append(get(func_pos))
                            func_pos += 1

                    if "." in get(pos + 2): error("invalid character", suggest = False)
                    ast.append({"type": "func", "return_type": get(pos), "name": get(pos + 2), "args": args, "ast": parser(func_tokens, file, False)})
                    pos = func_pos + 1

    if create_json:
        name = os.path.splitext(os.path.split(file)[1])[0]

        if name == "init":
            dirs = os.path.split(file)[0].split("/")
            name = dirs[len(dirs) - 1]

        with open(f"{name}_ast.json", "w") as file:
            file.write(json.dumps(ast, indent = 4))

    return ast

def interpreter(ast, file, isbase = False, islib = False, functions = {}, variables = {}, return_type = None, library_functions = {}, include_folders = [], create_json = False):
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
        return string.replace("\\n", "\n")

    if isbase:
        found_main = False
        define_standards(file, functions, variables, library_functions, include_folders)

    for i in ast:
        if i["type"] == "func":
            if i["name"] in functions or i["name"] in library_functions:
                error("can't overload a function")

            if i["name"] in variables:
                error("can't overload a function with a variable")

            functions[i["name"]] = {"type": i["return_type"], "args": i["args"], "ast": i["ast"]}

            if i["name"] == "main" and i["return_type"] == "INT" and i["args"] == {} and not found_main:
                if isbase:
                    found_main = True
                    error_code = interpreter(functions[i["name"]]["ast"], file, False, False, functions, variables, i["return_type"], library_functions, include_folders, create_json)
                    if error_code == {"NULL": "NULL"}: error("non-void functions should return a value")
                    else: error_code = error_code["INT"]

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
                error("'" + i["value"] + "'" + " " + "was not declared in this scope")

            else:
                if list(variables[i["value"]]["value"].values())[0] in ["FLOAT", "INT"]:
                    value = None

                    if list(variables[i["value"]]["value"].values())[0] == "INT":
                        value = int(list(variables[i["value"]]["value"].keys())[0]) + 1 if i["type"] == "increment" else -1

                    elif list(variables[i["value"]]["value"].values())[0] == "FLOAT":
                        value = str(float(list(variables[i["value"]]["value"].keys())[0].lower().replace("f", "")) + (1 if i["type"] == "increment" else -1)) + "f"

                    else:
                        error("unknown error")

                    variables[i["value"]]["value"] = {value: list(variables[i["value"]]["value"].values())[0]}

                else:
                    error("'" + i["value"] + "'" + " " + "should be an integer or float value")
                
        elif i["type"] == "var":
            if i["name"] in functions or i["name"] in library_functions:
                error("can't define a variable with an existing functions name")

            if i["value"] == None:
                if i["name"] in variables:
                    if variables[i["name"]]["type"] != i["value_type"]:
                        error("variable already exists")

                if i["value_type"] == "AUTO":
                    error("can't define auto type variables with no value")

                value = None
            
                match i["value_type"]:
                    case "INT": value = "0"
                    case "FLOAT": value = "0.0f"
                    case "BOOL": value = "FALSE"
                    case "STRING": value = ""

                if value == None:
                    error("unknown type")


                variables[i["name"]] = {"type": i["value_type"], "value": {value: i["value_type"]}}

            elif "type" in i["value"]:
                if isbase or islib:
                    error("functions only can be called in functions")

                if i["value"]["type"] == "call":
                    if i["name"] not in variables:
                        if i["value_type"] == None:
                            error("'" + i["name"] + "'" + " " + "was not declared in this scope")

                    if i["value"]["name"] in functions:
                        returned = interpreter([i["value"]], file, False, False, functions, variables, functions[i["value"]["name"]]["type"], library_functions, include_folders, create_json)

                    elif i["value"]["name"] in library_functions:
                        returned = interpreter([i["value"]], file, False, False, functions, variables, library_functions[i["value"]["name"]]["type"], library_functions, include_folders, create_json)

                    else:
                        error("'" + i["value"]["name"] + "'" + " " + "was not declared in this scope")

                    if list(returned.keys())[0] == i["value_type"] or i["value_type"] == "AUTO" or i["value_type"] == None:
                        if i["name"] in variables:
                            if variables[i["name"]]["type"] != list(returned.keys())[0]:
                                error("variable already exists")

                        variables[i["name"]] = {"type": list(returned.keys())[0], "value": {returned[list(returned.keys())[0]]: list(returned.keys())[0]}}

                    else:
                        error("invalid conversion from" + " " + "'" + list(returned.keys())[0].lower() + "'" + " " + "to" + " " + "'" + i["value_type"].lower() + "'")

            else:
                if i["value_type"] == None and i["name"] in variables:
                    if variables[i["name"]]["type"] == i["value"][list(i["value"].keys())[0]]:
                        variables[i["name"]]["value"] = i["value"]

                    elif variables[i["name"]]["type"] == list(variables[list(i["value"].keys())[0]]["value"].values())[0]:
                        variables[i["name"]]["value"] = variables[list(i["value"].keys())[0]]["value"]

                    elif "NULL" == i["value"][list(i["value"].keys())[0]]:
                        variables[i["name"]]["value"] = {"null": "STRING"}

                    else:
                        error("invalid conversion from" + " " + "'" + i["value"][list(i["value"].keys())[0]].lower() + "'" + " " + "to" + " " + "'" + variables[i["name"]]["type"].lower() + "'")

                elif i["value_type"] in ["STRING", "INT", "FLOAT", "BOOL"]:
                    if list(i["value"].values())[0] == "NAME":
                        if list(i["value"].keys())[0] in variables:
                            value_type = variables[list(i["value"].keys())[0]]["value"][list(variables[list(i["value"].keys())[0]]["value"].keys())[0]]

                        else:
                            error("'" + list(i["value"].keys())[0] + "'" + " " + "was not declared in this scope")

                    else:
                        value_type = i["value_type"]

                    if i["name"] in variables:
                        if list(i["value"].values())[0] != variables[i["name"]]["type"]:
                            error("can't change type of a variable")

                    if list(i["value"].keys())[0] in variables:
                        variables[i["name"]] = {"type": value_type, "value": {list(variables[list(i["value"].keys())[0]]["value"].keys())[0]: value_type}}

                    else:
                        if list(i["value"].values())[0] == "NULL" and value_type == "STRING":
                            variables[i["name"]] = {"type": value_type, "value": {"null": value_type}}
                            
                        else:
                            variables[i["name"]] = {"type": value_type, "value": {list(i["value"].keys())[0]: value_type}}

                else:
                    error("'" + i["name"] + "'" + " " + "was not declared in this scope")

        elif i["type"] == "include":
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

        elif i["type"] == "return":
            if isbase or islib:
                error("return keyword only can be use in functions")

            if return_type == None:
                error("return keyword only can be use in functions")

            elif return_type == "VOID":
                if list(i["value"].keys())[0] != None:
                    error("return can't return any value in non-void functions")

            elif list(i["value"].keys())[0] == "NAME":
                temp = variables[i["value"][list(i["value"].keys())[0]]]["value"]
                temp = {temp[list(temp.keys())[0]]: list(temp.keys())[0]}
                return temp

            elif list(i["value"].keys())[0] == return_type:
                return i["value"]

            elif list(i["value"].keys())[0] == "NULL":
                if return_type == "NULL": return {"null": return_type}
                else: return {"NULL": return_type}

            elif "type" in i["value"]:
                if i["value"]["type"] == "call":
                    if i["value"]["name"] in functions:
                        returned = interpreter([i["value"]], file, False, False, functions, variables, functions[i["value"]["name"]]["type"], library_functions, include_folders, create_json)

                    elif i["value"]["name"] in library_functions:
                        returned = interpreter([i["value"]], file, False, False, functions, variables, library_functions[i["value"]["name"]]["type"], library_functions, include_folders, create_json)

                    else:
                        error("'" + i["value"]["name"] + "'" + " " + "was not declared in this scope")

                    if list(returned.keys())[0] == return_type:
                        return {list(returned.keys())[0]: returned[list(returned.keys())[0]]}

                    else:
                        error("invalid conversion from" + " " + "'" + list(returned.keys())[0].lower() + "'" + " " + "to" + " " + "'" + i["value_type"].lower() + "'")

            else:
                error("unknown error")

        elif i["type"] == "delete":
            if i["value"] in variables:
                del variables[i["value"]]

            elif i["value"] in functions:
                del functions[i["value"]]

        elif i["type"] == "call":
            if isbase or islib:
                error("functions only can be called in functions")

            elif i["name"] in library_functions:
                if len(i["args"]) == len(library_functions[i["name"]]["args"]):  
                    temp = []

                    for j in i["args"]:
                        if j["type"] == "NAME":
                            if j["value"] not in variables:
                                error("'" + j["value"] + "'" + " " + "was not declared in this scope")

                            temp.append({"type": variables[j["value"]]["type"], "value": list(variables[j["value"]]["value"].keys())[0]})

                        elif j["type"] == "call":
                            temp_return_type = None

                            if i["name"] in library_functions: temp_return_type = library_functions[i["name"]]["type"]
                            elif i["name"] in functions: temp_return_type = functions[i["name"]]["type"]
                            else: error("'" + i["name"] + "'" + " " + "was not declared in this scope")

                            temp_value = interpreter([j], file, False, False, functions, variables, temp_return_type, library_functions, include_folders, create_json)
                            temp.append({"type": list(temp_value.keys())[0], "value": list(temp_value.values())[0]})

                        else:
                            temp.append(j)

                    for index, j in enumerate(library_functions[i["name"]]["args"].values()):
                        if temp[index]["type"] != j and temp[index]["type"] not in ["NULL"]:
                            error("argument types didn't match for" + " " + "'" + i["name"] + "'")

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

                    if returned == None: returned = {"NULL": "NULL"}
                    elif type(returned) == int: returned = {"INT": str(returned)}
                    elif type(returned) == float: returned = {"FLOAT": str(returned)}
                    elif type(returned) == bool: returned = {"BOOL": str(returned).upper()}
                    elif type(returned) == str: returned = {"STRING": str(returned)}
                    else: error("unknown type")

                    if len(ast) == 1:
                        return returned

                else:
                    error("argument count didn't match for" + " " + "'" + i["name"] + "'")

            elif i["name"] in functions:
                if len(i["args"]) == len(functions[i["name"]]["args"]):
                    temp = []

                    for j in i["args"]:
                        if j["type"] == "NAME":
                            temp.append({"type": variables[j["value"]]["type"], "value": list(variables[j["value"]]["value"].keys())[0]})

                        elif j["type"] == "call":
                            temp_return_type = None

                            if i["name"] in library_functions: temp_return_type = library_functions[i["name"]]["type"]
                            elif i["name"] in functions: temp_return_type = functions[i["name"]]["type"]
                            else: error("'" + i["name"] + "'" + " " + "was not declared in this scope")

                            temp_value = interpreter([j], file, False, False, functions, variables, temp_return_type, library_functions, include_folders, create_json)
                            temp.append({"type": list(temp_value.keys())[0], "value": list(temp_value.values())[0]})

                        else:
                            temp.append(j)

                    for index, j in enumerate(functions[i["name"]]["args"].values()):
                        if temp[index]["type"] != j:
                            error("argument types didn't match for" + " " + "'" + i["name"] + "'")

                    temp_vars = variables.copy()

                    for index, j in enumerate(functions[i["name"]]["args"].keys()):
                        if functions[i["name"]]["args"][j] == temp[index]["type"]:
                            temp_vars[j] = {"type": temp[index]["type"], "value": {temp[index]["value"]: temp[index]["type"]}}

                    returned = interpreter(functions[i["name"]]["ast"], file, False, False, functions.copy(), temp_vars, functions[i["name"]]["type"], library_functions, include_folders, create_json)

                    if len(ast) == 1:
                        return returned

                else:
                    error("argument count didn't match for" + " " + "'" + i["name"] + "'")

            else:
                error("'" + i["name"] + "'" + " " + "was not declared in this scope")

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

    file = get(0, "no input files", "rsharp", "fatal error", True)

    include_folders = [f"{os.path.split(__file__)[0]}\include", "."]
    create_json = False

    for i in argv[3:]:
        if i.startswith("-I"):
            include_folders.append(i[2:])

        elif i.startswith("-l"):
            command = i[2:]

            if command == "json":
                create_json = True

    if get(1, "no operation", "rsharp", "fatal error", True) == "--interprete":
        interpreter(parser(lexer(tools.read_file(file), file, create_json), file, create_json), file, True, False, include_folders = include_folders, create_json = create_json)

    elif get(1, "no operation", "rsharp", "fatal error", True) == "--transpile-python":
        transpiler.python(parser(lexer(tools.read_file(file), file, create_json), file, create_json), file)

    else:
        tools.error("operation not found", "fatal error")

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))