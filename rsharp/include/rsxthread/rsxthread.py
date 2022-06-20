from rsharp.tools import *

import threading

create_library("rsxthread")

threads = {}

@create_function("INT", {"func": "STRING", "daemon": "BOOL"})
def create_thread(environment):
    threads[len(threads)] = threading.Thread(target = run_function(environment["args"]["func"], environment), args = [], daemon = environment["args"]["daemon"])
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