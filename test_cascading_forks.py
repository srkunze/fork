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



fork(cpu_a)
fork(io_a)

fork(fork, fork, fork, fork, fork, cpu_a)
fork(fork, fork, fork, fork, fork, io_a)
