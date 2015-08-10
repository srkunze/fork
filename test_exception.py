# -*- coding: utf-8 -*-
import time
import traceback
from fork import *


@cpu_bound_fork
def runtime_error_cpu_fork():
    raise RuntimeError('error')

@cpu_bound_fork
def wrong_result_cpu_fork():
    return ''


@io_bound_fork
def runtime_error_fork():
    time.sleep(0.02)
    raise RuntimeError('error')

@io_bound_fork
def wrong_result_io_fork():
    return ''


def test_cpu_bound_fork_exception():
    print('##### test_cpu_bound_exception #####')
    try:
        x = runtime_error_cpu_fork()
        print(x)
    except:
        traceback.print_exc()


def test_cpu_bound_operator_exception():
    print('##### test_cpu_bound_operator_exception #####')
    try:
        x = 1 + wrong_result_cpu_fork()
        print(x)
    except:
        traceback.print_exc()


def test_io_bound_fork_exception():
    print('##### test_io_bound_fork_exception #####')
    try:
        x = runtime_error_fork()
        print(x)
    except:
        traceback.print_exc()


def test_io_bound_operator_exception():
    print('##### test_io_bound_operator_exception #####')
    try:
        x = 1 + wrong_result_io_fork()
        print(x)
    except:
        traceback.print_exc()


test_cpu_bound_fork_exception()
test_cpu_bound_operator_exception()
test_io_bound_fork_exception()
test_io_bound_operator_exception()
