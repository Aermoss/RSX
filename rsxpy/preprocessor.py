import sys, os

import rsxpy.tools as tools
import rsxpy.core as core

import __main__

def preprocessor(content, include_folders):
    def lexer():
        result = []
        pos, ignore = 0, 0
        string = ""

        keywords = [
            "define"
        ]

        while len(content) > pos:
            if content[pos] == "[":
                result.append({"type": "STRING", "value": string})
                string, code = "", ""
                pos += 1

                while content[pos] != "]":
                    code += content[pos]
                    if content[pos] == "[": ignore += 1
                    pos += 1
                    if content[pos] == "]":
                        if ignore != 0:
                            ignore -= 1
                            pos += 1

                if len(code) == 0:
                    result.append({"type": "STRING", "value": "[]"})

                elif code[0].isdigit() or (code.split(" ")[0] not in keywords):
                    result.append({"type": "STRING", "value": "[" + code + "]"})

                else:
                    result.append({"type": "PREPROCESS", "value": code})

                pos += 1

            else:
                string += content[pos]
                pos += 1

        result.append({"type": "STRING", "value": string})
        return result

    def parser(tokens = lexer()):
        code, pos = "", 0

        if not hasattr(__main__, "replace_name"):
            __main__.replace_name = {}

        while len(tokens) > pos:
            if tokens[pos]["type"] == "STRING":
                res = tokens[pos]["value"]

                for i in __main__.replace_name:
                    for j in " ([{)]};,":
                        for k in " ([{)]};,":
                            res = res.replace(j + i + k, j + __main__.replace_name[i] + k)

                code += res

            elif tokens[pos]["type"] == "PREPROCESS":
                value = tokens[pos]["value"]

                if value.split(" ")[0] == "define":
                    __main__.replace_name[value.split(" ")[1]] =  " ".join(value.split(" ")[2:])

            pos += 1

        return code

    return parser()