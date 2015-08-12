# -*- coding: utf-8 -*-
import re
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
    print('##### test_cpu_bound_runtime_error #####')
    try:
        x = fork(runtime_error_cpu)
        print(x)
    except:
        given_traceback = traceback.format_exc()
        if re.match(wanted_runtime_traceback.strip(), given_traceback.strip()):
            print('Traceback looks as desired.')
        else:
            print('Traceback do not look as desired:')
            print(given_traceback.strip())


def test_cpu_bound_fork_runtime_error():
    print('##### test_cpu_bound_fork_runtime_error #####')
    try:
        x = runtime_error_cpu_fork()
        print(x)
    except:
        given_traceback = traceback.format_exc()
        if re.match(wanted_runtime_traceback.strip(), given_traceback.strip()):
            print('Traceback looks as desired.')
        else:
            print('Traceback do not look as desired:')
            print(given_traceback.strip())


def test_io_bound_runtime_error():
    print('##### test_cpu_bound_runtime_error #####')
    try:
        x = fork(runtime_error_io)
        print(x)
    except:
        given_traceback = traceback.format_exc()
        if re.match(wanted_runtime_traceback.strip(), given_traceback.strip()):
            print('Traceback looks as desired.')
        else:
            print('Traceback do not look as desired:')
            print(given_traceback.strip())


def test_io_bound_fork_runtime_error():
    print('##### test_io_bound_fork_runtime_error #####')
    try:
        x = runtime_error_io_fork()
        print(x)
    except:
        given_traceback = traceback.format_exc()
        if re.match(wanted_runtime_traceback.strip(), given_traceback.strip()):
            print('Traceback looks as desired.')
        else:
            print('Traceback do not look as desired:')
            print(given_traceback.strip())


def test_cpu_bound_operator_error():
    print('##### test_cpu_bound_operator_error #####')
    try:
        x = 1 + fork(operator_error_cpu)
        print(x)
    except:
        given_traceback = traceback.format_exc()
        if re.match(wanted_operator_traceback.strip(), given_traceback.strip()):
            print('Traceback looks as desired.')
        else:
            print('Traceback do not look as desired:')
            print(given_traceback.strip())


def test_cpu_bound_fork_operator_error():
    print('##### test_cpu_bound_fork_operator_error #####')
    try:
        x = 1 + operator_error_cpu_fork()
        print(x)
    except:
        given_traceback = traceback.format_exc()
        if re.match(wanted_operator_traceback.strip(), given_traceback.strip()):
            print('Traceback looks as desired.')
        else:
            print('Traceback do not look as desired:')
            print(given_traceback.strip())


def test_io_bound_operator_error():
    print('##### test_io_bound_operator_error #####')
    try:
        x = 1 + fork(operator_error_io)
        print(x)
    except:
        given_traceback = traceback.format_exc()
        if re.match(wanted_operator_traceback.strip(), given_traceback.strip()):
            print('Traceback looks as desired.')
        else:
            print('Traceback do not look as desired:')
            print(given_traceback.strip())


def test_io_bound_fork_operator_error():
    print('##### test_io_bound_fork_operator_error #####')
    try:
        x = 1 + operator_error_io_fork()
        print(x)
    except:
        given_traceback = traceback.format_exc()
        if re.match(wanted_operator_traceback.strip(), given_traceback.strip()):
            print('Traceback looks as desired.')
        else:
            print('Traceback do not look as desired:')
            print(given_traceback.strip())


wanted_runtime_traceback = \
r'''
Traceback \(most recent call last\):
  File ".*/test_exception\.py", line \d+, in test_.*_runtime_error
    print\(x\)
  File ".*/fork\.py", line \d+, in __str__
    return str\(self\.__future__\.result\(\)\)
  File ".*/fork\.py", line \d+, in result_with_proper_traceback
    raise ResultEvaluationError\(original_traceback\)
fork\.ResultEvaluationError:\s*
\s*
    Original Traceback \(most recent call last\):
      File ".*/test_exception\.py", line \d+, in <module>
        test_.*_runtime_error\(\)
      File ".*/test_exception\.py", line \d+, in test_.*_runtime_error
        x = .*fork.*
      File ".*/test_exception\.py", line \d+, in runtime_error_.*
        raise RuntimeError\('runtime error'\)
    RuntimeError: runtime error
'''


wanted_operator_traceback = \
r'''
Traceback \(most recent call last\):
  File ".*/test_exception\.py", line \d+, in test_.*_operator_error
    print\(x\)
  File ".*/fork\.py", line \d+, in __str__
    return str\(self.__future__.result\(\)\)
  File ".*/fork\.py", line \d+, in result_with_proper_traceback
    raise ResultEvaluationError\(original_traceback\)
fork.ResultEvaluationError:\s*
\s*
    Original Traceback \(most recent call last\):
      File ".*/test_exception\.py", line \d+, in <module>
        test_.*_operator_error\(\)
      File ".*/test_exception\.py", line \d+, in .*_operator_error
        x = \d+ \+ .*fork.*
    TypeError: unsupported operand type\(s\) for \+: 'int' and 'str'
'''

test_cpu_bound_runtime_error()
test_cpu_bound_fork_runtime_error()
test_io_bound_runtime_error()
test_io_bound_fork_runtime_error()

test_cpu_bound_operator_error()
test_cpu_bound_fork_operator_error()
test_io_bound_operator_error()
test_io_bound_fork_operator_error()
