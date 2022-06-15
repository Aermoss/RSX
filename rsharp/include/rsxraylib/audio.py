from rsharp.tools import *

import raylib

from globals import *

create_library("audio")

@create_function("VOID", {})
def InitAudioDevice(environment):
    raylib.InitAudioDevice()

@create_function("VOID", {})
def CloseAudioDevice(environment):
    raylib.CloseAudioDevice()

@create_function("BOOL", {})
def IsAudioDeviceReady(environment):
    return bool(raylib.IsAudioDeviceReady())

@create_function("VOID", {"volume": "FLOAT"})
def SetMasterVolume(environment):
    raylib.SetMasterVolume(environment["args"]["volume"])

@create_function("INT", {"fileName": "STRING"})
def LoadWave(environment):
    return add_var(raylib.LoadWave(environment["args"]["fileName"].encode()))

# @create_function("INT", {"fileType": "STRING", ..., "dataSize": "INT"})
# def LoadWaveFromMemory(environment):
#     return add_wave(raylib.LoadWaveFromMemory(environment["args"]["fileType"].encode(), ..., environment["args"]["dataSize"]))

@create_function("INT", {"fileName": "STRING"})
def LoadSound(environment):
    return add_var(raylib.LoadSound(environment["args"]["fileName"].encode()))

@create_function("INT", {"wave": "INT"})
def LoadSoundFromWave(environment):
    return add_var(raylib.LoadSoundFromWave(get_var(environment["args"]["wave"])))

# @create_function("VOID", {"sound": "INT", ..., "samplesCount": "INT"})
# def UpdateSound(environment):
#     raylib.UpdateSound(environment["args"]["pitch"], ..., environment["args"]["samplesCount"])

@create_function("VOID", {"wave": "INT"})
def UnloadWave(environment):
    raylib.UnloadWave(get_var(environment["args"]["wave"]))
    del_var(environment["args"]["wave"])

@create_function("VOID", {"sound": "INT"})
def UnloadSound(environment):
    raylib.UnloadSound(get_var(environment["args"]["sound"]))
    del_var(environment["args"]["sound"])

@create_function("BOOL", {"wave": "INT", "fileName": "STRING"})
def ExportWave(environment):
    return bool(raylib.ExportWave(get_var(environment["args"]["wave"]), environment["args"]["fileName"].encode()))

@create_function("BOOL", {"wave": "INT", "fileName": "STRING"})
def ExportWaveAsCode(environment):
    return bool(raylib.ExportWaveAsCode(get_var(environment["args"]["wave"]), environment["args"]["fileName"].encode()))

@create_function("VOID", {"sound": "INT"})
def PlaySound(environment):
    raylib.PlaySound(get_var(environment["args"]["sound"]))

@create_function("VOID", {"sound": "INT"})
def StopSound(environment):
    raylib.StopSound(get_var(environment["args"]["sound"]))

@create_function("VOID", {"sound": "INT"})
def PauseSound(environment):
    raylib.PauseSound(get_var(environment["args"]["sound"]))

@create_function("VOID", {"sound": "INT"})
def ResumeSound(environment):
    raylib.ResumeSound(get_var(environment["args"]["sound"]))

@create_function("VOID", {"sound": "INT"})
def PlaySoundMulti(environment):
    raylib.PlaySoundMulti(get_var(environment["args"]["sound"]))

@create_function("VOID", {})
def StopSoundMulti(environment):
    raylib.StopSoundMulti()

@create_function("INT", {})
def GetSoundsPlaying(environment):
    return raylib.GetSoundsPlaying()

@create_function("BOOL", {"sound": "INT"})
def IsSoundPlaying(environment):
    return bool(raylib.IsSoundPlaying(get_var(environment["args"]["sound"])))

@create_function("VOID", {"sound": "INT", "volume": "FLOAT"})
def SetSoundVolume(environment):
    raylib.SetSoundVolume(get_var(environment["args"]["sound"]), environment["args"]["volume"])

@create_function("VOID", {"sound": "INT", "pitch": "FLOAT"})
def SetSoundPitch(environment):
    raylib.SetSoundPitch(get_var(environment["args"]["sound"]), environment["args"]["pitch"])

@create_function("VOID", {"wave": "INT", "sampleRate": "INT", "sampleSize": "INT", "channels": "INT"})
def WaveFormat(environment):
    raylib.WaveFormat(get_var(environment["args"]["wave"]), environment["args"]["sampleRate"], environment["args"]["sampleSize"], environment["args"]["channels"])

@create_function("INT", {"wave": "INT"})
def WaveCopy(environment):
    return add_var(raylib.WaveCopy(get_var(environment["args"]["wave"])))

@create_function("VOID", {"wave": "INT", "initSample": "INT", "finalSample": "INT"})
def WaveCrop(environment):
    raylib.WaveCrop(get_var(environment["args"]["wave"]), environment["args"]["initSample"], environment["args"]["finalSample"])

# @create_function(..., {"wave": "INT"})
# def LoadWaveSamples(environment):
#     return raylib.LoadWaveSamples(get_var(environment["args"]["wave"]))

# @create_function("VOID", {...})
# def UnloadWaveSamples(environment):
#     raylib.UnloadWaveSamples(...)

@create_function("INT", {"fileName": "STRING"})
def LoadMusicStream(environment):
    return add_var(raylib.LoadMusicStream(environment["args"]["fileName"].encode()))

# @create_function("INT", {"fileType": "STRING", ..., "dataSize": "INT"})
# def LoadMusicStreamFromMemory(environment):
#     return add_var(raylib.LoadMusicStreamFromMemory(environment["args"]["fileType"].encode(), ..., environment["args"]["dataSize"]))

@create_function("VOID", {"music": "INT"})
def UnloadMusicStream(environment):
    raylib.UnloadMusicStream(get_var(environment["args"]["music"]))
    del_var(environment["args"]["music"])

@create_function("VOID", {"music": "INT"})
def PlayMusicStream(environment):
    raylib.PlayMusicStream(get_var(environment["args"]["music"]))

@create_function("BOOL", {"music": "INT"})
def IsMusicStreamPlaying(environment):
    return bool(raylib.IsMusicStreamPlaying(get_var(environment["args"]["music"])))

@create_function("VOID", {"music": "INT"})
def UpdateMusicStream(environment):
    raylib.UpdateMusicStream(get_var(environment["args"]["music"]))

@create_function("VOID", {"music": "INT"})
def StopMusicStream(environment):
    raylib.StopMusicStream(get_var(environment["args"]["music"]))

@create_function("VOID", {"music": "INT"})
def PauseMusicStream(environment):
    raylib.PauseMusicStream(get_var(environment["args"]["music"]))

@create_function("VOID", {"music": "INT"})
def ResumeMusicStream(environment):
    raylib.ResumeMusicStream(get_var(environment["args"]["music"]))

@create_function("VOID", {"music": "INT", "position": "FLOAT"})
def SeekMusicStream(environment):
    raylib.SeekMusicStream(get_var(environment["args"]["music"]), environment["args"]["position"])

@create_function("VOID", {"music": "INT", "volume": "FLOAT"})
def SetMusicVolume(environment):
    raylib.SetMusicVolume(get_var(environment["args"]["music"]), environment["args"]["volume"])

@create_function("VOID", {"music": "INT", "pitch": "FLOAT"})
def SetMusicPitch(environment):
    raylib.SetMusicPitch(get_var(environment["args"]["music"]), environment["args"]["pitch"])

@create_function("FLOAT", {"music": "INT"})
def GetMusicTimeLength(environment):
    return raylib.GetMusicTimeLength(get_var(environment["args"]["music"]))

@create_function("FLOAT", {"music": "INT"})
def GetMusicTimePlayed(environment):
    return raylib.GetMusicTimePlayed(get_var(environment["args"]["music"]))

@create_function("INT", {"sampleRate": "INT", "sampleSize": "INT", "channels": "INT"})
def InitAudioStream(environment):
    return add_var(raylib.InitAudioStream(environment["args"]["sampleRate"], environment["args"]["sampleSize"], environment["args"]["channels"]))

# @create_function("VOID", {"stream": "INT", ..., "samplesCount": "INT"})
# def UpdateAudioStream(environment):
#     raylib.UpdateAudioStream(get_var(environment["args"]["stream"]), ..., environment["args"]["samplesCount"])

@create_function("VOID", {"stream": "INT"})
def CloseAudioStream(environment):
    raylib.CloseAudioStream(get_var(environment["args"]["stream"]))
    del_var(environment["args"]["stream"])

@create_function("BOOL", {"stream": "INT"})
def IsAudioStreamProcessed(environment):
    return bool(raylib.IsAudioStreamProcessed(get_var(environment["args"]["stream"])))

@create_function("VOID", {"stream": "INT"})
def PlayAudioStream(environment):
    raylib.PlayAudioStream(get_var(environment["args"]["stream"]))

@create_function("VOID", {"stream": "INT"})
def PauseAudioStream(environment):
    raylib.PauseAudioStream(get_var(environment["args"]["stream"]))

@create_function("VOID", {"stream": "INT"})
def ResumeAudioStream(environment):
    raylib.ResumeAudioStream(get_var(environment["args"]["stream"]))

@create_function("BOOL", {"stream": "INT"})
def IsAudioStreamPlaying(environment):
    return bool(raylib.IsAudioStreamPlaying(get_var(environment["args"]["stream"])))

@create_function("VOID", {"stream": "INT"})
def StopAudioStream(environment):
    raylib.StopAudioStream(get_var(environment["args"]["stream"]))

@create_function("VOID", {"stream": "INT", "volume": "FLOAT"})
def SetAudioStreamVolume(environment):
    raylib.SetAudioStreamVolume(get_var(environment["args"]["stream"]), environment["args"]["volume"])

@create_function("VOID", {"stream": "INT", "pitch": "FLOAT"})
def SetAudioStreamPitch(environment):
    raylib.SetAudioStreamPitch(get_var(environment["args"]["stream"]), environment["args"]["pitch"])

@create_function("VOID", {"size": "INT"})
def SetAudioStreamBufferSizeDefault(environment):
    raylib.SetAudioStreamBufferSizeDefault(environment["args"]["size"])

audio = pack_library()