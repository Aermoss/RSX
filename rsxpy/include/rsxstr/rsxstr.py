from rsxpy.tools import *

create_library("rsxstr")

@create_function("BOOL", {"a": "STRING"})
def isspace(environment):
    return environment["args"]["a"].isspace()

@create_function("BOOL", {"a": "STRING"})
def isalpha(environment):
    return environment["args"]["a"].isalpha()

@create_function("BOOL", {"a": "STRING"})
def isalnum(environment):
    return environment["args"]["a"].isalnum()

@create_function("BOOL", {"a": "STRING"})
def isascii(environment):
    return environment["args"]["a"].isascii()

@create_function("BOOL", {"a": "STRING"})
def isdecimal(environment):
    return environment["args"]["a"].isdecimal()

@create_function("BOOL", {"a": "STRING"})
def isdigit(environment):
    return environment["args"]["a"].isdigit()

@create_function("BOOL", {"a": "STRING"})
def isnumeric(environment):
    return environment["args"]["a"].isnumeric()

@create_function("BOOL", {"a": "STRING"})
def isupper(environment):
    return environment["args"]["a"].isupper()

@create_function("BOOL", {"a": "STRING"})
def islower(environment):
    return environment["args"]["a"].islower()

@create_function("INT", {"a": "STRING", "b": "STRING"})
def find(environment):
    return environment["args"]["a"].find(environment["args"]["b"])

@create_function("STRING", {"a": "STRING"})
def upper(environment):
    return environment["args"]["a"].upper()

@create_function("STRING", {"a": "STRING"})
def lower(environment):
    return environment["args"]["a"].lower()

@create_function("STRING", {"a": "STRING"})
def casefold(environment):
    return environment["args"]["a"].casefold()

@create_function("STRING", {"a": "STRING"})
def capitalize(environment):
    return environment["args"]["a"].capitalize()

@create_function("STRING", {"a": "STRING", "b": "STRING", "c": "STRING"})
def replace(environment):
    return environment["args"]["a"].replace(environment["args"]["b"], environment["args"]["c"])

@create_function("INT", {"a": "STRING"})
def strlen(environment):
    return len(environment["args"]["a"])

@create_function("STRING", {"a": "STRING", "b": "INT"})
def getchar(environment):
    return environment["args"]["a"][environment["args"]["b"]]

@create_function("STRING", {"a": "STRING", "b": "STRING"})
def addstr(environment):
    return environment["args"]["a"] + environment["args"]["b"]

@create_function("STRING", {"a": "STRING", "b": "INT"})
def mulstr(environment):
    return environment["args"]["a"] * environment["args"]["b"]

@create_function("STRING", {"a": "BOOL"})
def btos(environment):
    return str(environment["args"]["a"]).lower()

@create_function("STRING", {"a": "FLOAT"})
def ftos(environment):
    return str(environment["args"]["a"])

@create_function("STRING", {"a": "INT"})
def itos(environment):
    return str(environment["args"]["a"])

@create_function("BOOL", {"a": "STRING"})
def stob(environment):
    if environment["args"]["a"] == "true": return True
    else: return False

@create_function("FLOAT", {"a": "STRING"})
def stof(environment):
    return float(environment["args"]["a"].lower().replace("f", ""))

@create_function("INT", {"a": "STRING"})
def stoi(environment):
    return int(environment["args"]["a"])

rsxstr = pack_library()