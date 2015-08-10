# -*- coding: utf-8 -*-
import sys
import traceback
from fork import *


@cpu_bound
def runtime_error_cpu():
    raise RuntimeError('runtime error')

@cpu_bound
def operator_error_cpu():
    return ''

@cpu_bound_fork
def runtime_error_cpu_fork():
    raise RuntimeError('runtime error')

@cpu_bound_fork
def operator_error_cpu_fork():
    return ''


@io_bound
def runtime_error_io():
    raise RuntimeError('runtime error')

@io_bound
def operator_error_io():
    return ''

@io_bound_fork
def runtime_error_io_fork():
    raise RuntimeError('runtime error')

@io_bound_fork
def operator_error_io_fork():
    return ''


def test_cpu_bound_runtime_error():
    print('##### test_cpu_bound_runtime_error #####', file=sys.stderr)
    try:
        x = fork(runtime_error_cpu)
        print(x)
    except:
        traceback.print_exc()


def test_cpu_bound_operator_error():
    print('##### test_cpu_bound_operator_error #####', file=sys.stderr)
    try:
        x = 1 + fork(operator_error_cpu)
        print(x)
    except:
        traceback.print_exc()


def test_cpu_bound_fork_runtime_error():
    print('##### test_cpu_bound_fork_runtime_error #####', file=sys.stderr)
    try:
        x = runtime_error_cpu_fork()
        print(x)
    except:
        traceback.print_exc()


def test_cpu_bound_fork_operator_error():
    print('##### test_cpu_bound_fork_operator_error #####', file=sys.stderr)
    try:
        x = 1 + operator_error_cpu_fork()
        print(x)
    except:
        traceback.print_exc()


def test_io_bound_runtime_error():
    print('##### test_cpu_bound_runtime_error #####', file=sys.stderr)
    try:
        x = fork(runtime_error_io)
        print(x)
    except:
        traceback.print_exc()


def test_io_bound_operator_error():
    print('##### test_io_bound_operator_error #####', file=sys.stderr)
    try:
        x = 1 + fork(operator_error_io)
        print(x)
    except:
        traceback.print_exc()


def test_io_bound_fork_runtime_error():
    print('##### test_io_bound_fork_runtime_error #####', file=sys.stderr)
    try:
        x = runtime_error_io_fork()
        print(x)
    except:
        traceback.print_exc()


def test_io_bound_fork_operator_error():
    print('##### test_io_bound_fork_operator_error #####', file=sys.stderr)
    try:
        x = 1 + operator_error_io_fork()
        print(x)
    except:
        traceback.print_exc()


test_cpu_bound_runtime_error()
test_cpu_bound_fork_runtime_error()
test_io_bound_runtime_error()
test_io_bound_fork_runtime_error()

test_cpu_bound_operator_error()
test_cpu_bound_fork_operator_error()
test_io_bound_operator_error()
test_io_bound_fork_operator_error()
