import time
from fork import *


@cpu_bound
def fib(n):
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


@io_bound
def webservice():
    time.sleep(0.1)
    return 'res'


@cpu_bound
def raise_an_error():
    print('called raise_an_error')
    raise Exception()


def test_cpu_bound(n):
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


def test_io_bound(n):
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

print('##### start #######')
test_cpu_bound(n=35)
print('##### next #######')
test_io_bound(n=30)
print('##### end #######')
