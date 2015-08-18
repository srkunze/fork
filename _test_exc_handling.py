# -*- coding: utf-8 -*-

from fork import *


class ArbitraryException(Exception):
    pass

class ExitTestException(Exception):
    pass

def func00():
    return func01()

def func01():
    return fork(func02)

def func02():
    raise ArbitraryException('runtime error')

def func10(x):
    return func11(x)

def func11(x):
    try:
        return func12(x)
    except ArbitraryException:
        print('test failed: catched ArbitraryException in wrong try-block A')
        raise ExitTestException

def func12(x):
    return evaluate(x)

def func20():
    try:
        return func21()
    except ArbitraryException:
        print('test passed: catched ArbitraryException in correct try-block')
        raise ExitTestException

def func21():
    return fork(func22)

def func22():
    raise ArbitraryException('runtime error')


def test_result_proxy_evaluation_when_entering_a_try_statement():
    print('##### test_result_proxy_evaluation_when_entering_a_try_statement #####')
    try:
        x = func00()
        func10(x)
    except ArbitraryException:
        print('test passed: catched ArbitraryException in correct try-block')
        raise ExitTestException
    else:
        print('test failed: no ArbitraryException catched in correct try-block')
        raise ExitTestException


def test_result_proxy_evaluation_when_exiting_a_try_statement():
    print('##### test_result_proxy_evaluation_when_exiting_a_try_statement #####')
    try:
        x = func20()
        func10(x)
    except ArbitraryException:
        print('test failed: catched ArbitraryException in wrong try-block B')
        raise ExitTestException
    else:
        print('test failed: no ArbitraryException catched in correct try-block')
        raise ExitTestException
