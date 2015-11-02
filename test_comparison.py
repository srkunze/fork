import time
from fork import *


@cpu_bound
def fib(n):
    return 1 if n <= 1 else fib(n-1) + fib(n-2)

@io_bound
def webservice():
    time.sleep(0.001)
    return 'result'


def test_cpu_bound_fork(n):
    print('##### test_cpu_bound_fork #####')
    start = time.time()
    seq_results = []
    for i in range(n):
        seq_results += [fib(i)]
    str(seq_results)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_results = []
    for i in range(n):
        par_results += [fork(fib, i)]
    str(par_results)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_results == par_results:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_results)
        print('parallel:  ', par_results)


def test_cpu_bound_process(n):
    print('##### test_cpu_bound_process #####')
    start = time.time()
    seq_results = []
    for i in range(n):
        seq_results += [fib(i)]
    str(seq_results)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_results = []
    for i in range(n):
        par_results += [process(fib, i)]
    str(par_results)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_results == par_results:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_results)
        print('parallel:  ', par_results)


def test_cpu_bound_fork_contagious(n):
    print('##### test_cpu_bound_fork_contagious #####')
    start = time.time()
    seq_results = 0
    for i in [20]*n:
        seq_results += fib(i)
    str(seq_results)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_results = 0
    for i in [20]*n:
        par_results += fork(fib, i)
    str(par_results)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_results == par_results:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_results)
        print('parallel:  ', par_results)


def test_cpu_bound_process_contagious(n):
    print('##### test_cpu_bound_process_contagious #####')
    start = time.time()
    seq_results = 0
    for i in [20]*n:
        seq_results += fib(i)
    str(seq_results)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_results = 0
    for i in [20]*n:
        par_results += process(fib, i)
    str(par_results)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_results == par_results:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_results)
        print('parallel:  ', par_results)


def test_io_bound_fork(n):
    print('##### test_io_bound_fork #####')
    start = time.time()
    seq_results = []
    for i in range(n):
        seq_results += [webservice()]
    str(seq_results)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_results = []
    for i in range(n):
        par_results += [fork(webservice)]
    str(par_results)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_results == par_results:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_results)
        print('parallel:  ', par_results)


def test_io_bound_thread(n):
    print('##### test_io_bound_thread #####')
    start = time.time()
    seq_results = []
    for i in range(n):
        seq_results += [webservice()]
    str(seq_results)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_results = []
    for i in range(n):
        par_results += [thread(webservice)]
    str(par_results)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_results == par_results:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_results)
        print('parallel:  ', par_results)


def test_io_bound_fork_contagious(n):
    print('##### test_io_bound_fork_contagious #####')
    start = time.time()
    seq_results = ''
    for i in range(n):
        seq_results += webservice()
    str(seq_results)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_results = ''
    for i in range(n):
        par_results += fork(webservice)
    str(par_results)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_results == par_results:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_results)
        print('parallel:  ', par_results)


def test_io_bound_thread_contagious(n):
    print('##### test_io_bound_thread_contagious #####')
    start = time.time()
    seq_results = ''
    for i in range(n):
        seq_results += webservice()
    str(seq_results)
    end = time.time()
    print('sequential:', end-start)

    start = time.time()
    par_results = ''
    for i in range(n):
        par_results += thread(webservice)
    str(par_results)
    end = time.time()
    print('parallel:  ', end-start)

    if seq_results == par_results:
        print('results are equal')
    else:
        print('results are unequal')
        print('sequential:', seq_results)
        print('parallel:  ', par_results)


test_cpu_bound_fork(n=30)
test_cpu_bound_process(n=30)
test_cpu_bound_fork_contagious(n=1000)
test_cpu_bound_process_contagious(n=1000)
test_io_bound_fork(n=30)
test_io_bound_thread(n=30)
test_io_bound_fork_contagious(n=1000)
test_io_bound_thread_contagious(n=1000)
