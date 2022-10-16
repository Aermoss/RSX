import sdl2, sdl2.ext, sdl2.sdlttf, sdl2.sdlgfx, sdl2.sdlmixer

from globals import *

import rsxpy.rsxlib as rsxlib

rsxlib.begin()

def RSX_SDL_GetEventType(event: int) -> int:
    return get_var(event).type

def SDL_Init(flags: int) -> int:
    return sdl2.SDL_Init(flags)

def SDL_CreateWindow(title: str, x: int, y: int, width: int, height: int, flags: int) -> int:
    return add_var(sdl2.SDL_CreateWindow(title.encode(), x, y, width, height, flags))

def SDL_DestroyWindow(window: int) -> None:
    sdl2.SDL_DestroyWindow(get_var(window))

def SDL_PollEvent(event: int) -> int:
    return sdl2.SDL_PollEvent(get_var(event))

def SDL_GetWindowSurface(window: int) -> int:
    return add_var(sdl2.SDL_GetWindowSurface(get_var(window)))

def SDL_UpdateWindowSurface(window: int) -> int:
    return sdl2.SDL_UpdateWindowSurface(get_var(window))

def SDL_Delay(time: int) -> None:
    sdl2.SDL_Delay(time)

def SDL_Event() -> int:
    return add_var(sdl2.SDL_Event())

rsxlib.end()