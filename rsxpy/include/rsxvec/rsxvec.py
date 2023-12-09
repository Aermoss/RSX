from rsxpy import *
from rsxvec_globals import *

import typing

rsxlib.begin()

def new() -> int:
    return add_var([], True)

def delete(vec: int) -> None:
    del_var(vec)

def pop(vec: int, index: int) -> None:
    get_var(vec).pop(index)

def length(vec: int) -> int:
    return len(get_var(vec))

def getStruct(vec: int, index: int) -> rsxlib.RawStruct():
    return get_var(vec)[index]

def getInt(vec: int, index: int) -> int:
    return get_var(vec)[index]

def getFloat(vec: int, index: int) -> float:
    return get_var(vec)[index]

def getString(vec: int, index: int) -> str:
    return get_var(vec)[index]

def getBool(vec: int, index: int) -> bool:
    return get_var(vec)[index]

def getIntArray(vec: int, index: int) -> typing.List[int]:
    return get_var(vec)[index]

def getFloatArray(vec: int, index: int) -> rsxlib.RawArray(tools.FloatType()):
    return get_var(vec)[index]

def getStringArray(vec: int, index: int) -> typing.List[str]:
    return get_var(vec)[index]

def getBoolArray(vec: int, index: int) -> typing.List[bool]:
    return get_var(vec)[index]

def addStruct(vec: int, value: rsxlib.RawStruct()) -> None:
    get_var(vec).append(value)

def addInt(vec: int, value: int) -> None:
    get_var(vec).append(value)

def addFloat(vec: int, value: float) -> None:
    get_var(vec).append(value)

def addString(vec: int, value: str) -> None:
    get_var(vec).append(value)

def addBool(vec: int, value: bool) -> None:
    get_var(vec).append(value)

def addIntArray(vec: int, value: typing.List[int]) -> None:
    get_var(vec).append(value)

def addFloatArray(vec: int, value: rsxlib.RawArray(tools.FloatType())) -> None:
    get_var(vec).append(value)

def addStringArray(vec: int, value: typing.List[str]) -> None:
    get_var(vec).append(value)

def addBoolArray(vec: int, value: typing.List[bool]) -> None:
    get_var(vec).append(value)

def setStruct(vec: int, index: int, value: rsxlib.RawStruct()) -> None:
    get_var(vec)[index] = value

def setInt(vec: int, index: int, value: int) -> None:
    get_var(vec)[index] = value

def setFloat(vec: int, index: int, value: float) -> None:
    get_var(vec)[index] = value

def setString(vec: int, index: int, value: str) -> None:
    get_var(vec)[index] = value

def setBool(vec: int, index: int, value: bool) -> None:
    get_var(vec)[index] = value

def setIntArray(vec: int, index: int, value: typing.List[int]) -> None:
    get_var(vec)[index] = value

def setFloatArray(vec: int, index: int, value: typing.List[float]) -> None:
    get_var(vec)[index] = value

def setStringArray(vec: int, index: int, value: typing.List[str]) -> None:
    get_var(vec)[index] = value

def setBoolArray(vec: int, index: int, value: typing.List[bool]) -> None:
    get_var(vec)[index] = value

rsxlib.end()