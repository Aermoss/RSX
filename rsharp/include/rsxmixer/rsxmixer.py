from rsharp.tools import *

import sdl2, sdl2.sdlmixer

create_library("rsxmixer")

chunk = None
channel = None
volume = None
filepath = None
initialized = False

@create_function("VOID", {"file": "STRING", "volume": "INT"})
def init(environment):
    global chunk, volume, filepath, initialized
    initialized = True
    volume = environment["args"]["volume"]
    filepath = environment["args"]["file"]
    sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)
    sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)
    chunk = sdl2.sdlmixer.Mix_LoadWAV(filepath.encode())

@create_function("VOID", {"loop": "INT"})
def play(environment):
    if not initialized: error("aermixer was not initialized", environment["file"])
    global channel
    channel = sdl2.sdlmixer.Mix_PlayChannel(-1, chunk, environment["args"]["loop"])
    sdl2.sdlmixer.Mix_Volume(channel, int(volume / 2))

@create_function("VOID", {})
def stop(environment):
    sdl2.sdlmixer.Mix_HaltChannel(channel)

@create_function("VOID", {})
def pause(environment):
    sdl2.sdlmixer.Mix_Pause(channel)

@create_function("VOID", {})
def resume(environment):
    sdl2.sdlmixer.Mix_Resume(channel)

@create_function("VOID", {"volum": "INT"})
def set_volume(environment):
    global volume
    volume = environment["args"]["volume"]
    sdl2.sdlmixer.Mix_Volume(channel, int(volume / 2))

@create_function("INT", {})
def get_volume(environment):
    return volume

@create_function("VOID", {"duration": "INT", "loop": "INT"})
def fade_in(environment):
    global channel
    channel = sdl2.sdlmixer.Mix_FadeInChannel(-1, chunk, environment["args"]["loop"], environment["args"]["duration"])
    sdl2.sdlmixer.Mix_Volume(channel, int(volume / 2))

@create_function("VOID", {"duration": "INT"})
def fade_out(environment):
    sdl2.sdlmixer.Mix_FadeOutChannel(channel, environment["args"]["duration"])

@create_function("VOID", {"file": "STRING"})
def set_file(environment):
    global music
    filepath = environment["args"]["file"]
    music = sdl2.sdlmixer.Mix_LoadMUS(filepath.encode())

@create_function("STRING", {})
def get_file(environment):
    return filepath

rsxmixer = pack_library()