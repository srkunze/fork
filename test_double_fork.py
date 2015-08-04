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


@cpu_bound_fork
def cpu_a_fork():
    for _ in range(30):
        cpu_b_fork()

@cpu_bound_fork
def cpu_b_fork():
    for _ in range(30):
        cpu_c_fork()

@cpu_bound_fork
def cpu_c_fork():
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


@io_bound_fork
def io_a_fork():
    for _ in range(30):
        io_b_fork()

@io_bound_fork
def io_b_fork():
    for _ in range(30):
        io_c_fork()

@io_bound_fork
def io_c_fork():
    pass


fork(cpu_a)
cpu_a_fork()
fork(io_a)
io_a_fork()
