from rsharp.tools import *

import raylib

from colors import *
from globals import *

create_library("core")

@create_function("VOID", {"width": "INT", "height": "INT", "title": "STRING"})
def InitWindow(environment):
    raylib.InitWindow(environment["args"]["width"], environment["args"]["height"], environment["args"]["title"].encode())

@create_function("BOOL", {})
def WindowShouldClose(environment):
    return bool(raylib.WindowShouldClose())

@create_function("VOID", {})
def CloseWindow(environment):
    raylib.CloseWindow()

@create_function("BOOL", {})
def IsWindowReady(environment):
    return bool(raylib.IsWindowReady())

@create_function("BOOL", {})
def IsWindowFullscreen(environment):
    return bool(raylib.IsWindowFullscreen())

@create_function("BOOL", {})
def IsWindowHidden(environment):
    return bool(raylib.IsWindowHidden())

@create_function("BOOL", {})
def IsWindowMinimized(environment):
    return bool(raylib.IsWindowMinimized())

@create_function("BOOL", {})
def IsWindowMaximized(environment):
    return bool(raylib.IsWindowMaximized())

@create_function("BOOL", {})
def IsWindowFocused(environment):
    return bool(raylib.IsWindowFocused())

@create_function("BOOL", {})
def IsWindowResized(environment):
    return bool(raylib.IsWindowResized())

@create_function("BOOL", {"flag": "INT"})
def IsWindowState(environment):
    return bool(raylib.IsWindowState(environment["args"]["flag"]))

@create_function("VOID", {"flags": "INT"})
def SetWindowState(environment):
    raylib.SetWindowState(environment["args"]["flags"])

@create_function("VOID", {"flags": "INT"})
def ClearWindowState(environment):
    raylib.ClearWindowState(environment["args"]["flags"])

@create_function("VOID", {})
def ToggleFullscreen(environment):
    raylib.ToggleFullscreen()

@create_function("VOID", {})
def MaximizeWindow(environment):
    raylib.MaximizeWindow()

@create_function("VOID", {})
def MinimizeWindow(environment):
    raylib.MinimizeWindow()

@create_function("VOID", {})
def RestoreWindow(environment):
    raylib.RestoreWindow()

@create_function("VOID", {"image": "INT"})
def SetWindowIcon(environment):
    raylib.SetWindowIcon(get_var(environment["args"]["image"]))

@create_function("VOID", {"title": "STRING"})
def SetWindowTitle(environment):
    raylib.SetWindowTitle(environment["args"]["title"].encode())

@create_function("VOID", {"x": "INT", "y": "INT"})
def SetWindowPosition(environment):
    raylib.SetWindowPosition(environment["args"]["x"], environment["args"]["y"])

@create_function("VOID", {"monitor": "INT"})
def SetWindowMonitor(environment):
    raylib.SetWindowMonitor(environment["args"]["monitor"])

@create_function("VOID", {"width": "INT", "height": "INT"})
def SetWindowMinSize(environment):
    raylib.SetWindowMinSize(environment["args"]["width"], environment["args"]["height"])

@create_function("VOID", {"width": "INT", "height": "INT"})
def SetWindowSize(environment):
    raylib.SetWindowSize(environment["args"]["width"], environment["args"]["height"])

# @create_function(..., {})
# def GetWindowHandle(environment):
#     return raylib.GetWindowHandle()

@create_function("INT", {})
def GetScreenWidth(environment):
    return raylib.GetScreenWidth()

@create_function("INT", {})
def GetScreenHeight(environment):
    return raylib.GetScreenHeight()

@create_function("INT", {})
def GetMonitorCount(environment):
    return raylib.GetMonitorCount()

@create_function("INT", {})
def GetCurrentMonitor(environment):
    return raylib.GetCurrentMonitor()

# @create_function(..., {"monitor": "INT"})
# def GetMonitorPosition(environment):
#     return raylib.GetMonitorPosition(environment["args"]["monitor"])

@create_function("INT", {"monitor": "INT"})
def GetMonitorWidth(environment):
    return raylib.GetMonitorWidth(environment["args"]["monitor"])

@create_function("INT", {"monitor": "INT"})
def GetMonitorHeight(environment):
    return raylib.GetMonitorHeight(environment["args"]["monitor"])

@create_function("INT", {"monitor": "INT"})
def GetMonitorPhysicalWidth(environment):
    return raylib.GetMonitorPhysicalWidth(environment["args"]["monitor"])

@create_function("INT", {"monitor": "INT"})
def GetMonitorPhysicalHeight(environment):
    return raylib.GetMonitorPhysicalHeight(environment["args"]["monitor"])

@create_function("INT", {"monitor": "INT"})
def GetMonitorRefreshRate(environment):
    return raylib.GetMonitorRefreshRate(environment["args"]["monitor"])

# @create_function(..., {})
# def GetWindowPosition(environment):
#     return raylib.GetWindowPosition()

# @create_function(..., {})
# def GetWindowScaleDPI(environment):
#     return raylib.GetWindowScaleDPI()

@create_function("STRING", {"monitor": "INT"})
def GetMonitorName(environment):
    return raylib.GetMonitorName(environment["args"]["monitor"])

@create_function("VOID", {"text": "STRING"})
def SetClipboardText(environment):
    raylib.SetClipboardText(environment["args"]["text"].encode())

@create_function("STRING", {})
def GetClipboardText(environment):
    return raylib.GetClipboardText()

@create_function("VOID", {})
def ShowCursor(environment):
    raylib.ShowCursor()

@create_function("VOID", {})
def HideCursor(environment):
    raylib.HideCursor()

@create_function("BOOL", {})
def IsCursorHidden(environment):
    return bool(raylib.IsCursorHidden())

@create_function("VOID", {})
def EnableCursor(environment):
    raylib.EnableCursor()

@create_function("VOID", {})
def DisableCursor(environment):
    raylib.DisableCursor()

@create_function("BOOL", {})
def IsCursorOnScreen(environment):
    return bool(raylib.IsCursorOnScreen())

@create_function("VOID", {"color": "INT"})
def ClearBackground(environment):
    raylib.ClearBackground(get_var(environment["args"]["color"]))

@create_function("VOID", {})
def BeginDrawing(environment):
    raylib.BeginDrawing()

@create_function("VOID", {})
def EndDrawing(environment):
    raylib.EndDrawing()

@create_function("VOID", {"camera": "INT"})
def BeginMode2D(environment):
    raylib.BeginMode2D(get_var(environment["args"]["camera"]))

@create_function("VOID", {})
def EndMode2D(environment):
    raylib.EndMode2D()

@create_function("VOID", {"camera": "INT"})
def BeginMode3D(environment):
    raylib.BeginMode3D(get_var(environment["args"]["camera"]))

@create_function("VOID", {})
def EndMode3D(environment):
    raylib.EndMode3D()

@create_function("VOID", {"target": "INT"})
def BeginTextureMode(environment):
    raylib.BeginTextureMode(get_var(environment["args"]["target"]))

@create_function("VOID", {})
def EndTextureMode(environment):
    raylib.EndTextureMode()

@create_function("VOID", {"shader": "INT"})
def BeginShaderMode(environment):
    raylib.BeginShaderMode(get_var(environment["args"]["shader"]))

@create_function("VOID", {})
def EndShaderMode(environment):
    raylib.EndShaderMode()

@create_function("VOID", {"mode": "INT"})
def BeginBlendMode(environment):
    raylib.BeginBlendMode(environment["args"]["mode"])

@create_function("VOID", {})
def EndBlendMode(environment):
    raylib.EndBlendMode()

@create_function("VOID", {"x": "INT", "y": "INT", "width": "INT", "height": "INT"})
def BeginScissorMode(environment):
    raylib.BeginScissorMode(environment["args"]["x"], environment["args"]["y"], environment["args"]["width"], environment["args"]["height"])

@create_function("VOID", {})
def EndScissorMode(environment):
    raylib.EndScissorMode()

# @create_function("VOID", {...})
# def BeginVrStereoMode(environment):
#     raylib.BeginVrStereoMode(...)

@create_function("VOID", {})
def EndVrStereoMode(environment):
    raylib.EndVrStereoMode()

# @create_function(..., {...})
# def LoadVrStereoConfig(environment):
#     return raylib.LoadVrStereoConfig(...)

# @create_function("VOID", {...})
# def UnloadVrStereoConfig(environment):
#     raylib.UnloadVrStereoConfig(...)

@create_function("INT", {"vsFileName": "STRING", "fsFileName": "STRING"})
def LoadShader(environment):
    return add_var(raylib.LoadShader(environment["args"]["vsFileName"].encode(), environment["args"]["fsFileName"].encode()))

@create_function("INT", {"vsCode": "STRING", "fsCode": "STRING"})
def LoadShaderFromMemory(environment):
    return add_var(raylib.LoadShaderFromMemory(environment["args"]["vsCode"].encode(), environment["args"]["fsCode"].encode()))

@create_function("INT", {"shader": "INT", "uniformName": "STRING"})
def GetShaderLocation(environment):
    return raylib.GetShaderLocation(get_var(environment["args"]["shader"]), environment["args"]["uniformName"].encode())

@create_function("INT", {"shader": "INT", "attribName": "STRING"})
def GetShaderLocationAttrib(environment):
    return raylib.GetShaderLocationAttrib(get_var(environment["args"]["shader"]), environment["args"]["attribName"].encode())

# @create_function("VOID", {"shader": "INT", "locIndex": "INT", ..., "uniformType": "INT"})
# def SetShaderValue(environment):
#     raylib.SetShaderValue(get_var(environment["args"]["shader"]), environment["args"]["locIndex"], ..., environment["args"]["uniformType"])

# @create_function("VOID", {"shader": "INT", "locIndex": "INT", ..., "uniformType": "INT", "count": "INT"})
# def SetShaderValueV(environment):
#     raylib.SetShaderValueV(get_var(environment["args"]["shader"]), environment["args"]["locIndex"], ..., environment["args"]["uniformType"], environment["args"]["count"])

# @create_function("VOID", {"shader": "INT", "locIndex": "INT", ...})
# def SetShaderValueMatrix(environment):
#     raylib.SetShaderValueMatrix(get_var(environment["args"]["shader"]), environment["args"]["locIndex"], ...)

# @create_function("VOID", {"shader": "INT", "locIndex": "INT", ...})
# def SetShaderValueTexture(environment):
#     raylib.SetShaderValueTexture(get_var(environment["args"]["shader"]), environment["args"]["locIndex"], ...)

@create_function("VOID", {"shader": "INT"})
def UnloadShader(environment):
    raylib.UnloadShader(get_var(environment["args"]["shader"]))

# @create_function(..., {..., ...})
# def GetMouseRay(environment):
#     return raylib.GetMouseRay(..., ...)

# @create_function(..., {...})
# def GetCameraMatrix(environment):
#     return raylib.GetCameraMatrix(...)

# @create_function(..., {...})
# def GetCameraMatrix2D(environment):
#     return raylib.GetCameraMatrix2D(...)

# @create_function(..., {..., ...})
# def GetWorldToScreen(environment):
#     return raylib.GetWorldToScreen(..., ...)

# @create_function(..., {..., ..., "width": "INT", "height": "INT"})
# def GetWorldToScreenEx(environment):
#     return raylib.GetWorldToScreenEx(..., ..., environment["args"]["width"], environment["args"]["height"])

# @create_function(..., {..., ...})
# def GetWorldToScreen2D(environment):
#     return raylib.GetWorldToScreen2D(..., ...)

# @create_function(..., {..., ...})
# def GetScreenToWorld2D(environment):
#     return raylib.GetScreenToWorld2D(..., ...)

@create_function("VOID", {"fps": "INT"})
def SetTargetFPS(environment):
    raylib.SetTargetFPS(environment["args"]["fps"])

@create_function("INT", {})
def GetFPS(environment):
    return raylib.GetFPS()

@create_function("FLOAT", {})
def GetFrameTime(environment):
    return raylib.GetFrameTime()

@create_function("FLOAT", {})
def GetTime(environment):
    return raylib.GetTime()

@create_function("INT", {"min": "INT", "max": "INT"})
def GetRandomValue(environment):
    return raylib.GetRandomValue(environment["args"]["min"], environment["args"]["max"])

@create_function("VOID", {"seed": "INT"})
def SetRandomSeed(environment):
    raylib.SetRandomSeed(environment["args"]["seed"])

@create_function("VOID", {"fileName": "STRING"})
def TakeScreenshot(environment):
    raylib.TakeScreenshot(environment["args"]["fileName"].encode())

@create_function("INT", {"flags": "INT"})
def SetConfigFlags(environment):
    return raylib.SetConfigFlags(environment["args"]["flags"])

@create_function("INT", {"logLevel": "INT"})
def SetTraceLogLevel(environment):
    return raylib.SetTraceLogLevel(environment["args"]["logLevel"])

@create_function("INT", {"logLevel": "INT", "text": "STRING"})
def TraceLog(environment):
    return raylib.TraceLog(environment["args"]["logLevel"], environment["args"]["text"].encode())

# @create_function(..., {"size": "INT"})
# def MemAlloc(environment):
#     return raylib.MemAlloc(environment["args"]["size"])

# @create_function(..., {..., "size": "INT"})
# def MemRealloc(environment):
#     return raylib.MemRealloc(..., environment["args"]["size"])

# @create_function("VOID", {...})
# def MemFree(environment):
#     raylib.MemFree(...)

# @create_function("VOID", {...})
# def TraceLogCallback(environment):
#     raylib.TraceLogCallback(...)

# @create_function("VOID", {...})
# def LoadFileDataCallback(environment):
#     raylib.LoadFileDataCallback(...)

# @create_function("VOID", {...})
# def SaveFileDataCallback(environment):
#     raylib.SaveFileDataCallback(...)

# @create_function("VOID", {...})
# def LoadFileTextCallback(environment):
#     raylib.LoadFileTextCallback(...)

# @create_function("VOID", {...})
# def SaveFileTextCallback(environment):
#     raylib.SaveFileTextCallback(...)

# @create_function(..., {"fileName": "STRING", ...})
# def LoadFileData(environment):
#     return raylib.LoadFileData(environment["args"]["fileName"].encode(), ...)

# @create_function("VOID", {...})
# def UnloadFileData(environment):
#     raylib.UnloadFileData(...)

# @create_function("BOOL", {"fileName": "STRING", ..., "bytesToWrite": "INT"})
# def SaveFileData(environment):
#     return bool(raylib.SaveFileData(environment["args"]["fileName"].encode(), ..., environment["args"]["bytesToWrite"]))

@create_function("STRING", {"fileName": "STRING"})
def LoadFileText(environment):
    return raylib.LoadFileText(environment["args"]["fileName"].encode())

# @create_function("VOID", {...})
# def UnloadFileText(environment):
#     raylib.UnloadFileText(...)

# @create_function("BOOL", {"fileName": "STRING", ...})
# def SaveFileText(environment):
#     return bool(raylib.SaveFileText(environment["args"]["fileName"].encode(), ...))

@create_function("BOOL", {"fileName": "STRING"})
def FileExists(environment):
    return bool(raylib.FileExists(environment["args"]["fileName"].encode()))

@create_function("BOOL", {"dirPath": "STRING"})
def DirectoryExists(environment):
    return bool(raylib.DirectoryExists(environment["args"]["dirPath"].encode()))

@create_function("BOOL", {"fileName": "STRING", "ext": "STRING"})
def IsFileExtension(environment):
    return bool(raylib.IsFileExtension(environment["args"]["fileName"].encode(), environment["args"]["ext"].encode()))

@create_function("STRING", {"fileName": "STRING"})
def GetFileExtension(environment):
    return raylib.GetFileExtension(environment["args"]["fileName"].encode())

@create_function("STRING", {"filePath": "STRING"})
def GetFileName(environment):
    return raylib.GetFileName(environment["args"]["filePath"].encode())

@create_function("STRING", {"filePath": "STRING"})
def GetFileNameWithoutExt(environment):
    return raylib.GetFileNameWithoutExt(environment["args"]["filePath"].encode())

@create_function("STRING", {"filePath": "STRING"})
def GetDirectoryPath(environment):
    return raylib.GetDirectoryPath(environment["args"]["filePath"].encode())

@create_function("STRING", {"dirPath": "STRING"})
def GetPrevDirectoryPath(environment):
    return raylib.GetPrevDirectoryPath(environment["args"]["dirPath"].encode())

@create_function("STRING", {})
def GetWorkingDirectory(environment):
    return raylib.GetWorkingDirectory()

# @create_function("STRING", {"dirPath": "STRING", ...})
# def GetDirectoryFiles(environment):
#     return raylib.GetDirectoryFiles(environment["args"]["dirPath"].encode(), ...)

@create_function("VOID", {})
def ClearDirectoryFiles(environment):
    raylib.ClearDirectoryFiles()

@create_function("BOOL", {"dir": "STRING"})
def ChangeDirectory(environment):
    return bool(raylib.ChangeDirectory(environment["args"]["dir"].encode()))

@create_function("BOOL", {})
def IsFileDropped(environment):
    return bool(raylib.IsFileDropped())

# @create_function("STRING", {...})
# def GetDroppedFiles(environment):
#     return raylib.GetDroppedFiles()

@create_function("VOID", {})
def ClearDroppedFiles(environment):
    raylib.ClearDroppedFiles()

@create_function("INT", {"fileName": "STRING"})
def GetFileModTime(environment):
    return raylib.GetFileModTime(environment["args"]["fileName".encode()])

# @create_function("STRING", {"data": "STRING", "dataLength": "INT", ...})
# def CompressData(environment):
#     return raylib.CompressData(environment["args"]["data"].encode(), environment["args"]["dataLength"], ...)

# @create_function("STRING", {"compData": "STRING", "compDataLength": "INT", ...})
# def DecompressData(environment):
#     return raylib.DecompressData(environment["args"]["compData"].encode(), environment["args"]["compDataLength"], ...)

# @create_function("STRING", {"data": "STRING", "dataLength": "INT", ...})
# def EncodeDataBase64(environment):
#     return raylib.EncodeDataBase64(environment["args"]["data"].encode(), environment["args"]["dataLength"], ...)

# @create_function("STRING", {"data": "STRING", ...})
# def DecodeDataBase64(environment):
#     return raylib.DecodeDataBase64(environment["args"]["data"].encode(), ...)

@create_function("BOOL", {"position": "INT", "value": "INT"})
def SaveStorageValue(environment):
    return bool(raylib.SaveStorageValue(environment["args"]["position"], environment["args"]["value"]))

@create_function("INT", {"position": "INT"})
def LoadStorageValue(environment):
    return raylib.LoadStorageValue(environment["args"]["position"])

@create_function("VOID", {"url": "STRING"})
def OpenURL(environment):
    raylib.OpenURL(environment["args"]["url"].encode())

@create_function("BOOL", {"key": "INT"})
def IsKeyPressed(environment):
    return bool(raylib.IsKeyPressed(environment["args"]["key"]))

@create_function("BOOL", {"key": "INT"})
def IsKeyReleased(environment):
    return bool(raylib.IsKeyReleased(environment["args"]["key"]))

@create_function("BOOL", {"key": "INT"})
def IsKeyDown(environment):
    return bool(raylib.IsKeyDown(environment["args"]["key"]))

@create_function("BOOL", {"key": "INT"})
def IsKeyUp(environment):
    return bool(raylib.IsKeyUp(environment["args"]["key"]))

@create_function("VOID", {"key": "INT"})
def SetExitKey(environment):
    raylib.SetExitKey(environment["args"]["key"])

@create_function("INT", {})
def GetKeyPressed(environment):
    return raylib.GetKeyPressed()

@create_function("INT", {})
def GetCharPressed(environment):
    return raylib.GetCharPressed()

@create_function("BOOL", {"gamepad": "INT"})
def IsGamepadAvailable(environment):
    return bool(raylib.IsGamepadAvailable(environment["args"]["gamepad"]))

@create_function("STRING", {"gamepad": "INT"})
def GetGamepadName(environment):
    return raylib.GetGamepadName(environment["args"]["gamepad"])

@create_function("BOOL", {"gamepad": "INT", "button": "INT"})
def IsGamepadButtonPressed(environment):
    return bool(raylib.IsGamepadButtonPressed(environment["args"]["gamepad"], environment["args"]["button"]))

@create_function("BOOL", {"gamepad": "INT", "button": "INT"})
def IsGamepadButtonDown(environment):
    return bool(raylib.IsGamepadButtonDown(environment["args"]["gamepad"], environment["args"]["button"]))

@create_function("BOOL", {"gamepad": "INT", "button": "INT"})
def IsGamepadButtonReleased(environment):
    return bool(raylib.IsGamepadButtonReleased(environment["args"]["gamepad"], environment["args"]["button"]))

@create_function("BOOL", {"gamepad": "INT", "button": "INT"})
def IsGamepadButtonUp(environment):
    return bool(raylib.IsGamepadButtonUp(environment["args"]["gamepad"], environment["args"]["button"]))

@create_function("INT", {})
def GetGamepadButtonPressed(environment):
    return raylib.GetGamepadButtonPressed()

@create_function("INT", {"gamepad": "INT"})
def GetGamepadAxisCount(environment):
    return raylib.GetGamepadAxisCount(environment["args"]["gamepad"])

@create_function("FLOAT", {"gamepad": "INT", "axis": "INT"})
def GetGamepadAxisMovement(environment):
    return raylib.GetGamepadAxisMovement(environment["args"]["gamepad"], environment["args"]["axis"])

@create_function("INT", {"mappings": "STRING"})
def SetGamepadMappings(environment):
    return raylib.SetGamepadMappings(environment["args"]["mappings"].encode())

@create_function("BOOL", {"button": "INT"})
def IsMouseButtonPressed(environment):
    return bool(raylib.IsMouseButtonPressed(environment["args"]["button"]))

@create_function("BOOL", {"button": "INT"})
def IsMouseButtonReleased(environment):
    return bool(raylib.IsMouseButtonReleased(environment["args"]["button"]))

@create_function("BOOL", {"button": "INT"})
def IsMouseButtonDown(environment):
    return bool(raylib.IsMouseButtonDown(environment["args"]["button"]))

@create_function("BOOL", {"button": "INT"})
def IsMouseButtonUp(environment):
    return bool(raylib.IsMouseButtonUp(environment["args"]["button"]))

@create_function("INT", {})
def GetMouseX(environment):
    return raylib.GetMouseX()

@create_function("INT", {})
def GetMouseY(environment):
    return raylib.GetMouseY()

# @create_function(..., {})
# def GetMousePosition(environment):
#     return raylib.GetMousePosition()

# @create_function(..., {})
# def GetMouseDelta(environment):
#     return raylib.GetMouseDelta()

@create_function("VOID", {"x": "INT", "y": "INT"})
def SetMousePosition(environment):
     raylib.SetMousePosition(environment["args"]["x"], environment["args"]["y"])

@create_function("VOID", {"offset_x": "INT", "offset_y": "INT"})
def SetMouseOffset(environment):
    raylib.SetMouseOffset(environment["args"]["offset_x"], environment["args"]["offset_y"])

@create_function("VOID", {"scale_x": "FLOAT", "scale_y": "FLOAT"})
def SetMouseScale(environment):
    raylib.SetMouseScale(environment["args"]["scale_x"], environment["args"]["scale_y"])

@create_function("FLOAT", {})
def GetMouseWheelMove(environment):
    return raylib.GetMouseWheelMove()

@create_function("VOID", {"cursor": "INT"})
def SetMouseCursor(environment):
    raylib.SetMouseCursor(environment["args"]["cursor"])

@create_function("INT", {})
def GetTouchX(environment):
    return raylib.GetTouchX()

@create_function("INT", {})
def GetTouchY(environment):
    return raylib.GetTouchY()

# @create_function(..., {"index": "INT"})
# def GetTouchPosition(environment):
#     return raylib.GetTouchPosition(environment["args"]["index"])

@create_function("INT", {"index": "INT"})
def GetTouchPointId(environment):
    return raylib.GetTouchPointId(environment["args"]["index"])

@create_function("INT", {})
def GetTouchPointCount(environment):
    return raylib.GetTouchPointCount()

@create_function("VOID", {"flags": "INT"})
def SetGesturesEnabled(environment):
    return raylib.SetGesturesEnabled(environment["args"]["flags"])

@create_function("BOOL", {"gesture": "INT"})
def IsGestureDetected(environment):
    return bool(raylib.IsGestureDetected(environment["args"]["gesture"]))

@create_function("INT", {})
def GetGestureDetected(environment):
    return raylib.GetGestureDetected()

@create_function("FLOAT", {})
def GetGestureHoldDuration(environment):
    return raylib.GetGestureHoldDuration()

# @create_function(..., {})
# def GetGestureDragVector(environment):
#     return raylib.GetGestureDragVector()

@create_function("FLOAT", {})
def GetGestureDragAngle(environment):
    return raylib.GetGestureDragAngle()

# @create_function(..., {})
# def GetGesturePinchVector(environment):
#     return raylib.GetGesturePinchVector()

@create_function("FLOAT", {})
def GetGesturePinchAngle(environment):
    return raylib.GetGesturePinchAngle()

# @create_function("VOID", {..., "mode": "INT"})
# def SetCameraMode(environment):
#     return raylib.SetCameraMode(..., environment["args"]["mode"])

# @create_function("VOID", {...})
# def UpdateCamera(environment):
#     return raylib.UpdateCamera(...)

@create_function("VOID", {"keyPan": "INT"})
def SetCameraPanControl(environment):
    raylib.SetCameraPanControl(environment["args"]["keyPan"])

@create_function("VOID", {"keyAlt": "INT"})
def SetCameraAltControl(environment):
    raylib.SetCameraAltControl(environment["args"]["keyAlt"])

@create_function("VOID", {"keySmoothZoom": "INT"})
def SetCameraSmoothZoomControl(environment):
    raylib.SetCameraSmoothZoomControl(environment["args"]["keySmoothZoom"])

@create_function("VOID", {"keyFront": "INT", "keyBack": "INT", "keyRight": "INT", "keyLeft": "INT", "keyUp": "INT", "keyDown": "INT"})
def SetCameraMoveControls(environment):
    raylib.SetCameraMoveControls(environment["args"]["keyFront"], environment["args"]["keyBack"], environment["args"]["keyRight"], environment["args"]["keyLeft"], environment["args"]["keyUp"], environment["args"]["keyDown"])

core = pack_library()