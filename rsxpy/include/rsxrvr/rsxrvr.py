import rsxpy.rsxlib as rsxlib
import rsxpy.tools as tools

import rvr, glm, os, ctypes

rsxlib.begin()

def RVRGetRecommendedRenderTargetSizeX() -> int:
    x = ctypes.c_uint32()
    y = ctypes.c_uint32()
    rvr.RVRGetRecommendedRenderTargetSize(ctypes.byref(x), ctypes.byref(y))
    return x.value

def RVRGetRecommendedRenderTargetSizeY() -> int:
    x = ctypes.c_uint32()
    y = ctypes.c_uint32()
    rvr.RVRGetRecommendedRenderTargetSize(ctypes.byref(x), ctypes.byref(y))
    return y.value

def RVRIsReady() -> bool:
    return rvr.RVRIsReady()

def RVRSetupStereoRenderTargets() -> bool:
    return rvr.RVRSetupStereoRenderTargets()

def RVRBeginRendering(eye: int) -> bool:
    return rvr.RVRBeginRendering(eye)

def RVREndRendering() -> bool:
    return rvr.RVREndRendering()

def RVRSubmitFramebufferDescriptorsToCompositor() -> bool:
    return rvr.RVRSubmitFramebufferDescriptorsToCompositor()

def RVRDeleteFramebufferDescriptors() -> bool:
    return rvr.RVRDeleteFramebufferDescriptors()

def RVRCreateShaderProgram(vertexShaderSource: str, fragmentShaderSource: str) -> int:
    return rvr.RVRCreateShaderProgram(vertexShaderSource, fragmentShaderSource)

def RVRInitControllers() -> bool:
    return rvr.RVRInitControllers()

def RVRSetControllerShowState(controller: int, state: bool) -> None:
    return rvr.RVRSetControllerShowState(controller, state)

def RVRGetControllerShowState(controller: int) -> bool:
    return rvr.RVRGetControllerShowState(controller)

def RVRGetCurrentViewProjectionMatrix(eye: int) -> int:
    data = rvr.RVRGetCurrentViewProjectionMatrix(eye)
    return tools.environ["RSXGLM_GLOBALS"].add_var(
        glm.mat4(*[data.value[i] for i in range(16)])
    )

def RVRRenderControllers() -> bool:
    return rvr.RVRRenderControllers()

def RVRInit() -> bool:
    rvr.RVRSetActionManifestPath((os.path.split(__file__)[0] + "\\" + "rvr_actions.json").replace("//", "\\").replace("/", "\\").encode())
    return rvr.RVRInit()

def RVRGetControllerTriggerClickState(controller: int) -> bool:
    return rvr.RVRGetControllerTriggerClickState(controller)

def RVRGetControllerTriggerClickRisingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerTriggerClickRisingEdge(controller)

def RVRGetControllerTriggerClickFallingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerTriggerClickFallingEdge(controller)

def RVRGetControllerGripClickState(controller: int) -> bool:
    return rvr.RVRGetControllerGripClickState(controller)

def RVRGetControllerGripClickRisingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerGripClickRisingEdge(controller)

def RVRGetControllerGripClickFallingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerGripClickFallingEdge(controller)

def RVRGetControllerJoystickClickState(controller: int) -> bool:
    return rvr.RVRGetControllerJoystickClickState(controller)

def RVRGetControllerJoystickClickRisingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerJoystickClickRisingEdge(controller)

def RVRGetControllerJoystickClickFallingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerJoystickClickFallingEdge(controller)

def RVRGetControllerTriggerTouchState(controller: int) -> bool:
    return rvr.RVRGetControllerTriggerTouchState(controller)

def RVRGetControllerTriggerTouchRisingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerTriggerTouchRisingEdge(controller)

def RVRGetControllerTriggerTouchFallingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerTriggerTouchFallingEdge(controller)

def RVRGetControllerGripTouchState(controller: int) -> bool:
    return rvr.RVRGetControllerGripTouchState(controller)

def RVRGetControllerGripTouchRisingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerGripTouchRisingEdge(controller)

def RVRGetControllerGripTouchFallingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerGripTouchFallingEdge(controller)

def RVRGetControllerJoystickTouchState(controller: int) -> bool:
    return rvr.RVRGetControllerJoystickTouchState(controller)

def RVRGetControllerJoystickTouchRisingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerJoystickTouchRisingEdge(controller)

def RVRGetControllerJoystickTouchFallingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerJoystickTouchFallingEdge(controller)

def RVRGetControllerButtonOneClickState(controller: int) -> bool:
    return rvr.RVRGetControllerButtonOneClickState(controller)

def RVRGetControllerButtonOneClickRisingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerButtonOneClickRisingEdge(controller)

def RVRGetControllerButtonOneClickFallingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerButtonOneClickFallingEdge(controller)

def RVRGetControllerButtonOneTouchState(controller: int) -> bool:
    return rvr.RVRGetControllerButtonOneTouchState(controller)

def RVRGetControllerButtonOneTouchRisingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerButtonOneTouchRisingEdge(controller)

def RVRGetControllerButtonOneTouchFallingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerButtonOneTouchFallingEdge(controller)

def RVRGetControllerButtonTwoClickState(controller: int) -> bool:
    return rvr.RVRGetControllerButtonTwoClickState(controller)

def RVRGetControllerButtonTwoClickRisingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerButtonTwoClickRisingEdge(controller)

def RVRGetControllerButtonTwoClickFallingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerButtonTwoClickFallingEdge(controller)

def RVRGetControllerButtonTwoTouchState(controller: int) -> bool:
    return rvr.RVRGetControllerButtonTwoTouchState(controller)

def RVRGetControllerButtonTwoTouchRisingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerButtonTwoTouchRisingEdge(controller)

def RVRGetControllerButtonTwoTouchFallingEdge(controller: int) -> bool:
    return rvr.RVRGetControllerButtonTwoTouchFallingEdge(controller)

def RVRGetControllerTriggerPull(controller: int) -> float:
    return rvr.RVRGetControllerTriggerPull(controller)

def RVRGetControllerGripPull(controller: int) -> float:
    return rvr.RVRGetControllerGripPull(controller)

def RVRGetControllerJoystickPosition(controller: int) -> int:
    data = rvr.RVRGetControllerJoystickPosition(controller)
    return tools.environ["RSXGLM_GLOBALS"].add_var(glm.vec2(data.x, data.y))

def RVRTriggerHapticVibration(controller: int, duration: float, frequency: float, amplitude: float) -> None:
    return rvr.RVRTriggerHapticVibration(controller, duration, frequency, amplitude)

def RVRShutdown() -> bool:
    return rvr.RVRShutdown()

def RVRIsInputAvailable() -> bool:
    return rvr.RVRIsInputAvailable()

def RVRGetProjectionMatrix(eye: int, nearClip: float, farClip: float) -> int:
    data = rvr.RVRGetProjectionMatrix(eye, nearClip, farClip)
    return tools.environ["RSXGLM_GLOBALS"].add_var(
        glm.mat4(*[data.value[i] for i in range(16)])
    )

def RVRGetEyePoseMatrix(eye: int) -> int:
    data = rvr.RVRGetEyePoseMatrix(eye)
    return tools.environ["RSXGLM_GLOBALS"].add_var(
        glm.mat4(*[data.value[i] for i in range(16)])
    )

def RVRCheckControllers() -> None:
    return rvr.RVRCheckControllers()

def RVRPollEvents() -> None:
    return rvr.RVRPollEvents()

def RVRInitEyes(nearClip: float, farClip: float) -> bool:
    return rvr.RVRInitEyes(nearClip, farClip)

def RVRInitCompositor() -> bool:
    return rvr.RVRInitCompositor()

def RVRUpdateHMDPoseMatrix() -> None:
    return rvr.RVRUpdateHMDPoseMatrix()

rsxlib.end()