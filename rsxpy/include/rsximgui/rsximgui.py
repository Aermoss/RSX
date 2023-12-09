import rsxpy.rsxlib as rsxlib
import rsxpy.tools as tools
from rsximgui_globals import *

import imgui.integrations.glfw as glfw_impl
import imgui

rsxlib.begin()

def GlfwRenderer(window: int) -> int:
    return add_var(glfw_impl.GlfwRenderer(tools.environ["RSXGLFW_GLOBALS"].get_var(window)))

def CreateContext() -> None:
    imgui.create_context()

def Begin(name: str, closable: bool, flags: int) -> bool:
    return imgui.begin(name, closable, flags)[1]

def End() -> None:
    imgui.end()

def Text(text: str) -> None:
    imgui.text(text)

def Render() -> None:
    imgui.render()

def NewFrame() -> None:
    imgui.new_frame()

def EndFrame() -> None:
    imgui.end_frame()

def ImVec2(x: int, y: int) -> int:
    return add_var(imgui.Vec2(x, y))

def ImVec4(x: int, y: int, z: int, w: int) -> int:
    return add_var(imgui.Vec4(x, y, z, w))

def TextColored(var: int, text: str) -> None:
    color = get_var(var)
    imgui.text_colored(text, color.x, color.y, color.z, color.w)

def Button(text: str) -> bool:
    return imgui.button(text)

def BeginChild(name: str) -> None:
    imgui.begin_child(name)

def EndChild() -> None:
    imgui.end_child()

def GetTime() -> float:
    return imgui.get_time()

def BeginMenuBar() -> bool:
    return imgui.begin_menu_bar()

def EndMenuBar() -> None:
    imgui.end_menu_bar()

def BeginMenu(name: str) -> bool:
    return imgui.begin_menu(name)

def EndMenu() -> None:
    imgui.end_menu()

def MenuItem(name: str, keybinding: str) -> bool:
    return imgui.menu_item(name, keybinding)[0]

def ColorEdit4(name: str, var: int) -> bool:
    color = get_var(var)
    res = imgui.color_edit4(name, color.x, color.y, color.z, color.w)
    set_var(var, imgui.Vec4(*(res[1])))
    return res[0]

def _PlotLines(name: str, data: int, count: int):
    imgui.plot_lines(name, get_var(data), count)

def GetDrawData() -> int:
    return add_var(imgui.get_draw_data())

def ImplRender(impl: int, data: int) -> None:
    get_var(impl).render(get_var(data))
    del_var(data)

def ImplProcessInputs(impl: int) -> None:
    get_var(impl).process_inputs()

def ImplShutdown(impl: int) -> None:
    get_var(impl).shutdown()

def Delete(var: int) -> None:
    del_var(var)

rsxlib.end()