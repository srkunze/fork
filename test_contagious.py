import time
from fork import *


@cpu_bound
def fib(n):
    return 1 if n <= 1 else fib(n-1) + fib(n-2)

@cpu_bound_fork
def fib_fork(n):
    return 1 if n <= 1 else fib(n-1) + fib(n-2)

@contagious_result
@cpu_bound_fork
def contagious_fib_fork(n):
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


@io_bound
def webservice():
    time.sleep(0.02)
    return 'result'

@io_bound_fork
def webservice_fork():
    time.sleep(0.02)
    return 'result'

@contagious_result
@io_bound_fork
def contagious_webservice_fork():
    time.sleep(0.02)
    return 'result'


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
        par_result += fib_fork(i)
    str(par_result)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_result == seq_result:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_result)
        print('parallel:  ', seq_result)


def test_cpu_bound_contagious_decorator(n):
    print('##### test_cpu_bound_contagious_decorator #####')
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
        par_result += contagious_fib_fork(i)
    str(par_result)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_result == seq_result:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_result)
        print('parallel:  ', seq_result)


def test_cpu_bound_contagious_directly(n):
    print('##### test_cpu_bound_contagious_directly #####')
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
        par_result += fork_contagious(fib, i)
    str(par_result)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_result == seq_result:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_result)
        print('parallel:  ', seq_result)


def test_cpu_bound_noncontagious(n):
    print('##### test_cpu_bound_noncontagious #####')
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
        par_result += fork_noncontagious(contagious_fib_fork, i)
    str(par_result)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_result == seq_result:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_result)
        print('parallel:  ', seq_result)


def test_io_bound(n):
    print('##### test_io_bound #####')
    start = time.time()
    seq_result = ''
    for i in range(n):
        seq_result += webservice()
    str(seq_result)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_result = ''
    for i in range(n):
        par_result += webservice_fork()
    str(par_result)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_result == seq_result:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_result)
        print('parallel:  ', seq_result)


def test_io_bound_contagious_decorator(n):
    print('##### test_io_bound_contagious_decorator #####')
    start = time.time()
    seq_result = ''
    for i in range(n):
        seq_result += webservice()
    str(seq_result)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_result = ''
    for i in range(n):
        par_result += contagious_webservice_fork()
    str(par_result)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_result == seq_result:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_result)
        print('parallel:  ', seq_result)


def test_io_bound_contagious_directly(n):
    print('##### test_io_bound_contagious_directly #####')
    start = time.time()
    seq_result = ''
    for i in range(n):
        seq_result += webservice()
    str(seq_result)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_result = ''
    for i in range(n):
        par_result += fork_contagious(webservice)
    str(par_result)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_result == seq_result:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_result)
        print('parallel:  ', seq_result)


def test_io_bound_noncontagious(n):
    print('##### test_io_bound_noncontagious #####')
    start = time.time()
    seq_result = ''
    for i in range(n):
        seq_result += webservice()
    str(seq_result)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_result = ''
    for i in range(n):
        par_result += fork_noncontagious(contagious_webservice_fork)
    str(par_result)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_result == seq_result:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_result)
        print('parallel:  ', seq_result)


test_cpu_bound(n=30)
test_cpu_bound_contagious_decorator(n=10)
test_cpu_bound_contagious_directly(n=30)
test_cpu_bound_noncontagious(n=30)
test_io_bound(n=30)
test_io_bound_contagious_decorator(n=30)
test_io_bound_contagious_directly(n=30)
test_io_bound_noncontagious(n=30)
