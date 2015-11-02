import time
from fork import *


@cpu_bound
def fib(n):
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


@io_bound
def webservice():
    time.sleep(0.001)
    return 'result'


def test_cpu_bound_await(n):
    print('##### test_cpu_bound_await #####')
    print(await(process(fib, n)))


def test_cpu_bound_await_all(n):
    print('##### test_cpu_bound_await_all #####')
    print(await_all(map_process(fib, range(n))))


def test_cpu_bound_await_any(n):
    print('##### test_cpu_bound_await_any #####')
    print(await_any(map_process(fib, range(n))))


def test_io_bound_await(n):
    print('##### test_io_bound_await #####')
    print(await(thread(webservice)))


def test_io_bound_await_all(n):
    print('##### test_io_bound_await_all #####')
    print(await_all([thread(webservice) for i in range(n)]))


def test_io_bound_await_any(n):
    print('##### test_io_bound_await_any #####')
    print(await_any([thread(webservice) for i in range(n)]))


test_cpu_bound_await(10)
test_cpu_bound_await_all(10)
test_cpu_bound_await_any(10)
test_io_bound_await(10)
test_io_bound_await_all(10)
test_io_bound_await_any(10)
