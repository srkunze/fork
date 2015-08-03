from fork import *


@cpu_bound
def cpu_a():
    for _ in range(30):
        fork(cpu_b)

@cpu_bound
def cpu_b():
    for _ in range(30):
        fork(cpu_c)

@cpu_bound
def cpu_c():
    pass


@io_bound
def io_a():
    for _ in range(30):
        fork(io_b)

@io_bound
def io_b():
    for _ in range(30):
        fork(io_c)

@io_bound
def io_c():
    pass


fork(cpu_a)
fork(io_a)

