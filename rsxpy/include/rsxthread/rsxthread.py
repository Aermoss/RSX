from rsxpy.tools import *
from rsxpy.core import *

import threading

create_library("rsxthread")

threads = {}

@create_function("INT", {"func": "STRING", "daemon": "BOOL"})
def create_thread(environment):
    context = Context(environment["context"].scope["global"][environment["args"]["func"]]["ast"], environment["file"])
    context.return_type = environment["context"].scope["global"][environment["args"]["func"]]["return_type"]
    context.scope = environment["context"].scope.copy()
    context.is_thread = True
    context.actual_context = environment["context"]
    threads[len(threads)] = threading.Thread(target = run_function, args = [environment["args"]["func"], context], daemon = environment["args"]["daemon"])
    return len(threads) - 1

@create_function("VOID", {"thread": "INT"})
def start_thread(environment):
    threads[environment["args"]["thread"]].start()

@create_function("VOID", {"thread": "INT"})
def join_thread(environment):
    threads[environment["args"]["thread"]].join()

@create_function("INT", {})
def active_count(environment):
    return threading.active_count()

rsxthread = pack_library()