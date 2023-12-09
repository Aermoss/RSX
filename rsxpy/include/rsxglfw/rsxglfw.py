import rsxpy.rsxlib as rsxlib
import rsxpy.tools as tools

import glfw

import rsxglfw_globals
tools.environ["RSXGLFW_GLOBALS"] = rsxglfw_globals

from rsxglfw_globals import *

rsxlib.begin()

def glfwInit() -> bool:
    return True if glfw.init() else False

def glfwTerminate() -> None:
    glfw.terminate()

def glfwSwapBuffers(window: int) -> None:
    glfw.swap_buffers(get_var(window))

def glfwPollEvents() -> None:
    glfw.poll_events()

def glfwWindowHint(hint: int, value: int) -> None:
    glfw.window_hint(hint, value)

def glfwSetInputMode(window: int, mode: int, value: int) -> None:
    glfw.set_input_mode(get_var(window), mode, value)

def glfwCreateWindow(width: int, height: int, title: str) -> int:
    return add_var(glfw.create_window(width, height, title, None, None), True)

def glfwDestroyWindow(window: int) -> None:
    glfw.destroy_window(get_var(window))

def glfwWindowShouldClose(window: int) -> bool:
    return True if glfw.window_should_close(get_var(window)) == 1 else False

def glfwMakeContextCurrent(window: int) -> None:
    glfw.make_context_current(get_var(window))

def glfwSwapInterval(interval: int) -> None:
    glfw.swap_interval(interval)

def glfwGetTime() -> float:
    return glfw.get_time()

def glfwGetKey(window: int, key: int) -> bool:
    return True if glfw.get_key(get_var(window), key) else False

def glfwSetCursorPos(window: int, x: float, y: float) -> None:
    glfw.set_cursor_pos(get_var(window), x, y)

def _glfwGetWindowWidth(window: int) -> int:
    return glfw.get_window_size(get_var(window))[0]

def _glfwGetWindowHeight(window: int) -> int:
    return glfw.get_window_size(get_var(window))[1]

def _glfwGetCursorX(window: int) -> float:
    return glfw.get_cursor_pos(get_var(window))[0]

def _glfwGetCursorY(window: int) -> float:
    return glfw.get_cursor_pos(get_var(window))[1]

rsxlib.end()