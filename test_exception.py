# -*- coding: utf-8 -*-
import time
from fork import *

@cpu_bound_fork
def fib_fork(n):
    raise RuntimeError('error')


@io_bound_fork
def webservice_fork():
    time.sleep(0.02)
    raise RuntimeError('error')


def test_cpu_bound_exception():
    print('##### test_cpu_bound_exception #####')
    try:
        x = fib_fork(8)
        print(x)
    except Exception as exc:
        import traceback
        traceback.print_exc(exc)


def test_io_bound_exception():
    print('##### test_io_bound_exception #####')
    try:
        print(webservice_fork())
    except Exception as exc:
        import traceback
        traceback.print_exc(exc)


test_cpu_bound_exception()
test_io_bound_exception()
