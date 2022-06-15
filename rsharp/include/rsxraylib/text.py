from rsharp.tools import *

import raylib

from globals import *

create_library("text")

# @create_function(..., {})
# def GetFontDefault(environment):
#     return raylib.GetFontDefault()

# @create_function(..., {"fileName": "STRING"})
# def LoadFont(environment):
#     return raylib.LoadFont(environment["args"]["fileName"].encode())

# @create_function(..., {"fileName": "STRING", "fontSize": "INT", ..., "glyphCount": "INT"})
# def LoadFontEx(environment):
#     return raylib.LoadFontEx(environment["args"]["fileName"].encode(), environment["args"]["fontSize"], ..., environment["args"]["glyphCount"])

# @create_function(..., {"image": "INT", "key": "INT", "firstChar": "INT"})
# def LoadFontFromImage(environment):
#     return raylib.LoadFontFromImage(get_image(environment["args"]["image"]), get_color(environment["args"]["key"]), environment["args"]["firstChar"])

# @create_function(..., {"fileType": "STRING", ..., "dataSize": "INT", "fontSize": "INT", ..., "glyphCount": "INT"})
# def LoadFontFromMemory(environment):
#     return raylib.LoadFontFromMemory(environment["args"]["fileType"].encode(), ..., environment["args"]["dataSize"], environment["args"]["fontSize"], ..., environment["args"]["glyphCount"])

# @create_function(..., {..., "dataSize": "INT", "fontSize": "INT", ..., "glyphCount": "INT", "type": "INT"})
# def LoadFontData(environment):
#     return raylib.LoadFontData(..., environment["args"]["dataSize"], environment["args"]["fontSize"], ..., environment["args"]["glyphCount"], environment["args"]["type"])

# @create_function("INT", {..., ..., "glyphCount": "INT", "fontSize": "INT", "padding": "INT", "packMethod": "INT"})
# def GenImageFontAtlas(environment):
#     return raylib.GenImageFontAtlas(..., ..., environment["args"]["glyphCount"], environment["args"]["fontSize"], environment["args"]["padding"], environment["args"]["packMethod"])

# @create_function("VOID", {..., "glyphCount": "INT"})
# def UnloadFontData(environment):
#     raylib.UnloadFontData(..., environment["args"]["glyphCount"])

# @create_function("VOID", {...})
# def UnloadFont(environment):
#     raylib.UnloadFont(...)

@create_function("VOID", {"posX": "INT", "posY": "INT"})
def DrawFPS(environment):
    raylib.DrawFPS(environment["args"]["posX"], environment["args"]["posY"])

@create_function("VOID", {"text": "STRING", "posX": "INT", "posY": "INT", "fontSize": "INT", "tint": "INT"})
def DrawText(environment):
    raylib.DrawText(environment["args"]["text"].encode(), environment["args"]["posX"], environment["args"]["posY"], environment["args"]["fontSize"], get_var(environment["args"]["tint"]))

# @create_function("VOID", {..., "text": "STRING", ..., "fontSize": "FLOAT", "spacing": "FLOAT", "tint": "INT"})
# def DrawTextEx(environment):
#     raylib.DrawTextEx(..., environment["args"]["text"].encode(), ..., environment["args"]["fontSize"], environment["args"]["spacing"], get_var(environment["args"]["tint"]))

# @create_function("VOID", {..., "text": "STRING", ..., ..., "rotation": "FLOAT", "fontSize": "FLOAT", "spacing": "FLOAT", "tint": "INT"})
# def DrawTextPro(environment):
#     raylib.DrawTextPro(..., environment["args"]["text"].encode(), ..., ..., environment["args"]["rotation"], environment["args"]["fontSize"], environment["args"]["spacing"], get_var(environment["args"]["tint"]))

# @create_function("VOID", {..., "codepoint": "INT", ..., "fontSize": "FLOAT", "tint": "INT"})
# def DrawTextCodepoint(environment):
#     raylib.DrawTextCodepoint(..., environment["args"]["codepoint"], ..., environment["args"]["fontSize"], get_var(environment["args"]["tint"]))

@create_function("INT", {"text": "STRING", "fontSize": "INT"})
def MeasureText(environment):
    return raylib.MeasureText(environment["args"]["text"].encode(), environment["args"]["fontSize"])

# @create_function(..., {..., "text": "STRING", "fontSize": "FLOAT", "spacing": "FLOAT"})
# def MeasureTextEx(environment):
#     return raylib.MeasureTextEx(..., environment["args"]["text"].encode(), environment["args"]["fontSize"], environment["args"]["spacing"])

# @create_function("INT", {..., "codepoint": "INT"})
# def GetGlyphIndex(environment):
#     return raylib.GetGlyphIndex(..., environment["args"]["codepoint"])

# @create_function(..., {..., "codepoint": "INT"})
# def GetGlyphInfo(environment):
#     return raylib.GetGlyphInfo(..., environment["args"]["codepoint"])

# @create_function(..., {..., "codepoint": "INT"})
# def GetGlyphAtlasRec(environment):
#     return raylib.GetGlyphAtlasRec(..., environment["args"]["codepoint"])

# @create_function("INT", {"text": "STRING", ...})
# def LoadCodepoints(environment):
#     return raylib.LoadCodepoints(environment["args"]["text"], ...)

# @create_function("VOID", {...})
# def UnloadCodepoints(environment):
#     return raylib.UnloadCodepoints(...)

@create_function("INT", {"text": "STRING"})
def GetCodepointCount(environment):
    return raylib.GetCodepointCount(environment["args"]["text"].encode())

# @create_function("INT", {"text": "STRING", ...})
# def GetCodepoint(environment):
#     return raylib.GetCodepoint(environment["args"]["text"].encode(), ...)

# @create_function("STRING", {"codepoint": "INT", ...})
# def CodepointToUTF8(environment):
#     return raylib.CodepointToUTF8(environment["args"]["codepoint"], ...)

# @create_function("STRING", {..., "length": "INT"})
# def TextCodepointsToUTF8(environment):
#     return raylib.TextCodepointsToUTF8(..., environment["args"]["length"])

# @create_function("INT", {..., "src": "STRING"})
# def TextCopy(environment):
#     return raylib.TextCopy(..., environment["args"]["src"])

@create_function("BOOL", {"text1": "STRING", "text2": "STRING"})
def TextIsEqual(environment):
    return bool(raylib.TextIsEqual(environment["args"]["text1"].encode(), environment["args"]["text2"].encode()))

@create_function("INT", {"text": "STRING"})
def TextLength(environment):
    return raylib.TextLength(environment["args"]["text"].encode())

# @create_function("STRING", {"text": "STRING", ...})
# def TextFormat(environment):
#     return raylib.TextFormat(environment["args"]["text"], ...)

@create_function("STRING", {"text": "STRING", "position": "INT", "length": "INT"})
def TextSubtext(environment):
    return raylib.TextSubtext(environment["args"]["text"].encode(), environment["args"]["position"], environment["args"]["length"])

@create_function("STRING", {"text": "STRING", "replace": "STRING", "by": "STRING"})
def TextReplace(environment):
    return raylib.TextReplace(environment["args"]["text"].encode(), environment["args"]["replace"].encode(), environment["args"]["by"].encode())

@create_function("STRING", {"text": "STRING", "insert": "STRING", "position": "INT"})
def TextInsert(environment):
    return raylib.TextInsert(environment["args"]["text"].encode(), environment["args"]["insert"].encode(), environment["args"]["position"])

# @create_function("STRING", {..., "count": "INT", "delimiter": "STRING"})
# def TextJoin(environment):
#     return raylib.TextJoin(..., environment["args"]["count"], environment["args"]["delimiter"].encode())

# @create_function(..., {"text": "STRING", ..., ...})
# def TextSplit(environment):
#     return raylib.TextSplit(environment["args"]["text"].encode(), ..., ...)

# @create_function("VOID", {..., "append": "STRING", "position": "INT"})
# def TextAppend(environment):
#     raylib.TextAppend(..., environment["args"]["append"].encode(), environment["args"]["position"])

@create_function("VOID", {"text": "STRING", "find": "STRING"})
def TextFindIndex(environment):
    raylib.TextFindIndex(environment["args"]["text"].encode(), environment["args"]["find"].encode())

@create_function("STRING", {"text": "STRING"})
def TextToUpper(environment):
    return raylib.TextToUpper(environment["args"]["text"].encode())

@create_function("STRING", {"text": "STRING"})
def TextToLower(environment):
    return raylib.TextToLower(environment["args"]["text"].encode())

text = pack_library()