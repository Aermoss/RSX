import socket as sock

from sockets import sockets

from rsxpy.tools import *

create_library("rsxsocket")

@create_function("INT", {"family": "STRING", "type": "STRING"})
def socket(environ):
    family, type = environ["args"].values()
    sockets[len(sockets)] = sock.socket(getattr(sock, family), getattr(sock, type))
    return len(sockets) - 1

@create_function("VOID", {"socket": "INT", "ip": "STRING", "port": "INT"})
def bind(environ):
    socket, ip, port = environ["args"].values()
    sockets[socket].bind((ip, port))

@create_function("VOID", {"socket": "INT", "ip": "STRING", "port": "INT"})
def connect(environ):
    socket, ip, port = environ["args"].values()
    sockets[socket].connect((ip, port))

@create_function("VOID", {"socket": "INT"})
def listen(environ):
    sockets[environ["args"]["socket"]].listen()

@create_function("VOID", {"socket": "INT", "data": "STRING"})
def send(environ):
    socket, data = environ["args"].values()
    sockets[socket].send(data.encode())

@create_function("STRING", {"socket": "INT", "bytes": "INT"})
def recv(environ):
    socket, bytes = environ["args"].values()
    return sockets[socket].recv(bytes).decode()

@create_function("INT", {"socket": "INT"})
def accept(environ):
    sockets[len(sockets)] = sockets[environ["args"]["socket"]].accept()[0]
    return len(sockets) - 1

@create_function("VOID", {"socket": "INT", "type": "STRING"})
def shutdown(environ):
    socket, type = environ["args"].values()
    sockets[socket].shutdown(getattr(sock, type))

@create_function("VOID", {"socket": "INT"})
def close(environ):
    sockets[environ["args"]["socket"]].close()

@create_function("STRING", {"hostname": "STRING"})
def gethostbyname(environ):
    return sock.gethostbyname(environ["args"]["hostname"])

@create_function("STRING", {})
def gethostname(environ):
    return sock.gethostname()

rsxsocket = pack_library()