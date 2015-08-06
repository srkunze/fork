from fork import *


@cpu_bound
def cpu_a():
    print('cpu_a')
    for _ in range(30):
        fork(cpu_b)
    print('cpu_a end')

@cpu_bound
def cpu_b():
    print('cpu_b')
    for _ in range(30):
        fork(cpu_c)
    print('cpu_b end')

@cpu_bound
def cpu_c():
    print('cpu_c')
    pass


@cpu_bound_fork
def cpu_a_fork():
    print('cpu_a_fork')
    for _ in range(30):
        cpu_b_fork()
    print('cpu_a_fork end')

@cpu_bound_fork
def cpu_b_fork():
    print('cpu_b_fork')
    for _ in range(30):
        cpu_c_fork()
    print('cpu_b_fork end')

@cpu_bound_fork
def cpu_c_fork():
    print('cpu_c_fork')
    pass


@io_bound
def io_a():
    print('io_a')
    for _ in range(30):
        fork(io_b)
    print('io_a end')

@io_bound
def io_b():
    print('io_b')
    for _ in range(30):
        fork(io_c)
    print('io_b end')

@io_bound
def io_c():
    print('io_c')
    pass


@io_bound_fork
def io_a_fork():
    print('io_a_fork')
    for _ in range(30):
        io_b_fork()
    print('io_a_fork end')

@io_bound_fork
def io_b_fork():
    print('io_b_fork')
    for _ in range(30):
        io_c_fork()
    print('io_b_fork end')

@io_bound_fork
def io_c_fork():
    print('io_c_fork')
    pass


fork(cpu_a)
cpu_a_fork()
fork(io_a)
io_a_fork()

fork(fork, fork, fork, fork, fork, cpu_a)
fork(fork, fork, fork, fork, fork, io_a)
