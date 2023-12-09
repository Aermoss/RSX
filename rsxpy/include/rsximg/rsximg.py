import rsxpy.rsxlib as rsxlib
import rsxpy.tools as tools

from rsximg_globals import *

import rsximg_globals
tools.environ["RSXIMG_GLOBALS"] = rsximg_globals

import PIL.Image

rsxlib.begin()

def loadImage(file: str) -> int:
    try: return add_var(PIL.Image.open(file))
    except FileNotFoundError: tools.error("file not found: " + file, "<rsximg>/rsximg.py")

def getTextureData(addr: int, mode: str) -> int:
    data = get_var(addr).tobytes("raw", mode, 0, -1)
    return add_var((ctypes.c_uint8 * len(data))(*data))

def _getTextureWidth(addr: int) -> int:
    return get_var(addr).width

def _getTextureHeight(addr: int) -> int:
    return get_var(addr).height

rsxlib.end()