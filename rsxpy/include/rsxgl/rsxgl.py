import rsxpy.rsxlib as rsxlib
import rsxpy.tools as tools

import pyglet.gl as gl
from ctypes import *

from rsxgl_globals import *

gl.glGetString.restype = c_char_p

rsxlib.begin()

def glGetString(name: int) -> str:
    return gl.glGetString(name).decode()

def glCreateShader(type: int) -> int:
    return gl.glCreateShader(type)

def glCreateProgram() -> int:
    return gl.glCreateProgram()

def glDeleteProgram(program: int) -> None:
    gl.glDeleteProgram(program)

def glShaderSource(shader: int, count: int, string: str) -> None:
    src_buffer = create_string_buffer(string.encode())
    buf_pointer = cast(pointer(pointer(src_buffer)), POINTER(POINTER(c_char)))
    length = c_int(len(string) + 1)
    gl.glShaderSource(shader, count, buf_pointer, byref(length))

def glCompileShader(shader: int) -> None:
    gl.glCompileShader(shader)

def glDeleteShader(shader: int) -> None:
    gl.glDeleteShader(shader)

def glAttachShader(program: int, shader: int) -> None:
    gl.glAttachShader(program, shader)

def glLinkProgram(program: int) -> None:
    gl.glLinkProgram(program)

def glDetachShader(program: int, shader: int) -> None:
    gl.glDetachShader(program, shader)

def glGenTextures(n: int) -> int:
    textures = c_uint32()
    gl.glGenTextures(n, pointer(textures))
    return add_var(textures)

def glBindTexture(target: int, texture: int) -> None:
    gl.glBindTexture(target, get_var(texture))

def glTexParameterf(target: int, key: int, value: float) -> None:
    gl.glTexParameterf(target, key, value)

def glTexParameteri(target: int, key: int, value: int) -> None:
    gl.glTexParameteri(target, key, value)

def glGenerateMipmap(target: int) -> None:
    gl.glGenerateMipmap(target)

def glTexImage2D(target: int, level: int, internalformat: int, width: int, height: int, border: int, format: int, type: int, pixels: int) -> None:
    gl.glTexImage2D(target, level, internalformat, width, height, border, format, type, tools.environ["RSXIMG_GLOBALS"].get_var(pixels))

def glGenBuffers(n: int) -> int:
    buffers = c_uint32()
    gl.glGenBuffers(n, byref(buffers))
    return add_var(buffers)

def glBindBuffer(target: int, buffer: int) -> None:
    gl.glBindBuffer(target, get_var(buffer))

def glBufferData(target: int, size: int, data: int, usage: int) -> None:
    gl.glBufferData(target, size, get_var(data), usage)

def glGetAttribLocation(program: int, name: str) -> int:
    return gl.glGetAttribLocation(program, name)

def glGenVertexArrays(n: int) -> int:
    arrays = c_uint32()
    gl.glGenVertexArrays(n, byref(arrays))
    return add_var(arrays)

def glBindVertexArray(array: int) -> None:
    gl.glBindVertexArray(get_var(array))

def glVertexAttribPointer(index: int, size: int, type: int, normalized: bool, stride: int, pointer: int) -> None:
    gl.glVertexAttribPointer(index, size, type, normalized, stride, pointer)

def glEnableVertexAttribArray(index: int) -> None:
    gl.glEnableVertexAttribArray(index)

def glUseProgram(program: int) -> None:
    gl.glUseProgram(program)

def glDrawArrays(mode: int, first: int, count: int) -> None:
    gl.glDrawArrays(mode, first, count)

def glDeleteBuffers(n: int, buffers: int) -> None:
    gl.glDeleteBuffers(n, byref(get_var(buffers)))

def glDeleteVertexArrays(n: int, arrays: int) -> None:
    gl.glDeleteVertexArrays(n, byref(get_var(arrays)))

def glGetError() -> int:
    return gl.glGetError()

def glDrawElements(mode: int, count: int, type: int, indices: int) -> None:
    gl.glDrawElements(mode, count, type, indices)

def glClear(mask: int) -> None:
    return gl.glClear(mask)

def glClearColor(red: float, green: float, blue: float, alpha: float) -> None:
    return gl.glClearColor(red, green, blue, alpha)

def glDepthFunc(cap: int) -> None:
    gl.glDepthFunc(cap)

def glDisable(cap: int) -> None:
    gl.glDisable(cap)

def glEnable(cap: int) -> None:
    gl.glEnable(cap)

def glGetShaderiv(shader: int, enum: int) -> int:
    status = c_int32()
    gl.glGetShaderiv(shader, enum, byref(status))
    return status.value

def glGetProgramiv(program: int, enum: int) -> int:
    status = c_int32()
    gl.glGetProgramiv(program, enum, byref(status))
    return status.value

def glGetShaderInfoLog(shader: int, length: int) -> str:
    buffer = create_string_buffer(length)
    gl.glGetShaderInfoLog(shader, length, None, buffer)
    return buffer.value.decode()

def glGetProgramInfoLog(program: int, length: int) -> str:
    buffer = create_string_buffer(length)
    gl.glGetProgramInfoLog(program, length, None, buffer)
    return buffer.value.decode()

def glViewport(x: int, y: int, width: int, height: int) -> None:
    gl.glViewport(x, y, width, height)

def glGetUniformLocation(program: int, name: str) -> int:
    return gl.glGetUniformLocation(program, name.encode())

def _glUniform1i(location: int, i0: int) -> None:
    gl.glUniform1i(location, i0)

def _glUniform2i(location: int, i0: int, i1: int) -> None:
    gl.glUniform2i(location, i0, i1)

def _glUniform3i(location: int, i0: int, i1: int, i2: int) -> None:
    gl.glUniform3i(location, i0, i1, i2)

def _glUniform4i(location: int, i0: int, i1: int, i2: int, i3: int) -> None:
    gl.glUniform4i(location, i0, i1, i2, i3)

def _glUniform1f(location: int, f0: int) -> None:
    gl.glUniform1f(location, f0)

def _glUniform2f(location: int, f0: int, f1: int) -> None:
    gl.glUniform2f(location, f0, f1)

def _glUniform3f(location: int, f0: int, f1: int, f2: int) -> None:
    gl.glUniform3f(location, f0, f1, f2)

def _glUniform4f(location: int, f0: int, f1: int, f2: int, f3: int) -> None:
    gl.glUniform4f(location, f0, f1, f2, f3)

def _glUniform1iv(location: int, count: int, value: int) -> None:
    gl.glUniform1iv(location, count, get_var(value))

def _glUniform2iv(location: int, count: int, value: int) -> None:
    gl.glUniform2iv(location, count, get_var(value))

def _glUniform3iv(location: int, count: int, value: int) -> None:
    gl.glUniform3iv(location, count, get_var(value))

def _glUniform4iv(location: int, count: int, value: int) -> None:
    gl.glUniform4iv(location, count, get_var(value))

def _glUniform1fv(location: int, count: int, value: int) -> None:
    gl.glUniform1fv(location, count, get_var(value))

def _glUniform2fv(location: int, count: int, value: int) -> None:
    gl.glUniform2fv(location, count, get_var(value))

def _glUniform3fv(location: int, count: int, value: int) -> None:
    gl.glUniform3fv(location, count, get_var(value))

def _glUniform4fv(location: int, count: int, value: int) -> None:
    gl.glUniform4fv(location, count, get_var(value))

def glUniformMatrix2fv(location: int, count: int, transpose: bool, value: int) -> None:
    gl.glUniformMatrix2fv(location, count, transpose, tools.environ["RSXGLM_GLOBALS"].get_var(value))

def glUniformMatrix3fv(location: int, count: int, transpose: bool, value: int) -> None:
    gl.glUniformMatrix3fv(location, count, transpose, tools.environ["RSXGLM_GLOBALS"].get_var(value))

def glUniformMatrix4fv(location: int, count: int, transpose: bool, value: int) -> None:
    gl.glUniformMatrix4fv(location, count, transpose, tools.environ["RSXGLM_GLOBALS"].get_var(value))

def glUniformMatrix2x3fv(location: int, count: int, transpose: bool, value: int) -> None:
    gl.glUniformMatrix2x3fv(location, count, transpose, tools.environ["RSXGLM_GLOBALS"].get_var(value))

def glUniformMatrix3x2fv(location: int, count: int, transpose: bool, value: int) -> None:
    gl.glUniformMatrix3x2fv(location, count, transpose, tools.environ["RSXGLM_GLOBALS"].get_var(value))

def glUniformMatrix2x4fv(location: int, count: int, transpose: bool, value: int) -> None:
    gl.glUniformMatrix2x4fv(location, count, transpose, tools.environ["RSXGLM_GLOBALS"].get_var(value))

def glUniformMatrix4x2fv(location: int, count: int, transpose: bool, value: int) -> None:
    gl.glUniformMatrix4x2fv(location, count, transpose, tools.environ["RSXGLM_GLOBALS"].get_var(value))

def glUniformMatrix3x4fv(location: int, count: int, transpose: bool, value: int) -> None:
    gl.glUniformMatrix3x4fv(location, count, transpose, tools.environ["RSXGLM_GLOBALS"].get_var(value))

def glUniformMatrix4x3fv(location: int, count: int, transpose: bool, value: int) -> None:
    gl.glUniformMatrix4x3fv(location, count, transpose, tools.environ["RSXGLM_GLOBALS"].get_var(value))

rsxlib.end()