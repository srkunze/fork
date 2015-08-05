import time
from fork import *

def fib(n):
    return 1 if n <= 1 else fib(n-1) + fib(n-2)

@cpu_bound_fork
def fib_fork(n):
    return 1 if n <= 1 else fib(n-1) + fib(n-2)

@contagious
@cpu_bound_fork
def fib_contagious_fork(n):
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def test_cpu_bound(n):
    print('##### test_cpu_bound #####')
    start = time.time()
    seq_result = 0
    for i in range(n):
        seq_result += fib(i)
    str(seq_result)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_result = 0
    for i in range(n):
        par_result += fib(i)
    str(par_result)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_result == seq_result:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_result)
        print('parallel:  ', seq_result)


def test_cpu_bound_contagious(n):
    print('##### test_cpu_bound_contagious #####')
    start = time.time()
    seq_result = 0
    for i in range(n):
        seq_result += fib(i)
    str(seq_result)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_result = 0
    for i in range(n):
        par_result += fib_contagious_fork(i)
    str(par_result)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_result == seq_result:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_result)
        print('parallel:  ', seq_result)


test_cpu_bound(n=35)
test_cpu_bound_contagious(n=35)
