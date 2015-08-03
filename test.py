from fork import *


@io_bound
def func():
    print('called func')
    import time
    time.sleep(2)
    print('waited 2 seconds in func')
    return 'result'


@cpu_bound
def fib(n):
    print('called fib')
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


@cpu_bound
def raise_an_error():
    print('called raise_an_error')
    raise Exception()


def test():
    a = fork(func)
    b = fork(fib, 4)
    c = fork(raise_an_error())
    print(a)
    print(b)
    print(c)


test()
