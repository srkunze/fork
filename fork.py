# -*- coding: utf-8 -*-
import os
import sys
import types
import traceback
from functools import wraps
import threading
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor

_debug = False

__version__ = '0.30'
__version_info__ = (0, 30)
__all__ = [
    'cpu_bound', 'io_bound', 'cpu_bound_fork', 'io_bound_fork', 'unsafe',
    'fork', 'evaluate',
    'UnknownWaitingForError', 'ResultEvaluationError',
]


def cpu_bound(callable_):
    """
    Marks callable as mainly cpu-bound and safe for running off the MainThread.
    """
    callable_.__has_side_effects__ = False
    callable_.__waiting_for__ = 'cpu'
    return callable_


def io_bound(callable_):
    """
    Marks callable as mainly io-bound and safe for running off the MainThread.
    """
    callable_.__has_side_effects__ = False
    callable_.__waiting_for__ = 'io'
    return callable_


def cpu_bound_fork(callable_):
    """
    Converts callable into a fork marked as mainly
    cpu-bound and safe for running off the MainThread.
    """
    callable_ = cpu_bound(callable_)
    callable_.__stack_frames_to_pop_off__ = 3

    @wraps(callable_)
    def fork_wrapper(*args, **kwargs):
        return fork(callable_, *args, **kwargs)

    import sys
    new_name = '__decorated_cpu_bound_function_{name}__'.format(name=callable_.__name__)
    callable_.__name__ = new_name
    setattr(sys.modules[callable_.__module__], new_name, callable_)

    return fork_wrapper


def io_bound_fork(callable_):
    """
    Converts callable into a fork marked as mainly
    io-bound and safe for running off the MainThread.
    """
    callable_ = io_bound(callable_)
    callable_.__stack_frames_to_pop_off__ = 3

    @wraps(callable_)
    def fork_wrapper(*args, **kwargs):
        return fork(callable_, *args, **kwargs)
    return fork_wrapper


def unsafe(callable_):
    """
    Marks callable as not safe for running off the MainThread.
    """
    callable_.__has_side_effects__ = True
    return callable_


_pools_of = threading.local()
_pools_of.processes = None
_pools_of.threads = None


def fork(callable_, *args, **kwargs):
    """
    Submit a callable to another process or thread
    depending on its io- or cpu-boundness.
    Returns an proxy object for the return value.
    """
    has_side_effects = getattr(callable_, '__has_side_effects__', False)
    if has_side_effects:
        return callable_(*args, **kwargs)
    waiting_for = getattr(callable_, '__waiting_for__', 'cpu')
    stack_frames_to_pop_off = getattr(callable_, '__stack_frames_to_pop_off__', 2)
    if waiting_for == 'cpu':
        if not _pools_of.processes:
            _pools_of.processes = ProcessPoolExecutor()
        return ResultProxy(_pools_of.processes.submit(_safety_wrapper, callable_, *args, **kwargs), stack_frames_to_pop_off)
    elif waiting_for == 'io':
        if not _pools_of.threads:
            _pools_of.threads = ThreadPoolExecutor(2 * (os.cpu_count() or 1))
        return ResultProxy(_pools_of.threads.submit(_safety_wrapper, callable_, *args, **kwargs), stack_frames_to_pop_off)
    raise UnknownWaitingForError(waiting_for)


def evaluate(result_proxy):
    """
    Unwraps the result from the proxy.
    """
    return result_proxy.__future__.result()


def _safety_wrapper(callable_, *args, **kwargs):
    _pools_of.processes = None
    _pools_of.threads = None
    try:
        return callable_(*args, **kwargs)
    except BaseException as exc:
        if _debug:
            raise TransportException(exc, traceback.format_tb(sys.exc_info()[2]) + traceback.format_exception_only(type(exc), exc))
        else:
            raise TransportException(exc, traceback.format_tb(sys.exc_info()[2])[1:] + traceback.format_exception_only(type(exc), exc))
    finally:
        if _pools_of.processes:
            _pools_of.processes.shutdown()
        if _pools_of.threads:
            _pools_of.threads.shutdown()


class UnknownWaitingForError(Exception):

    pass


class TransportException(Exception):

    #FIXME: remove default parameters when https://github.com/agronholm/pythonfutures/issues/30 is fixed
    def __init__(self, exc=None, traceback_info=None):
        self.exc = exc
        self.traceback_info = traceback_info


class ResultEvaluationError(Exception):

    pass


class ResultProxy(object):

    def __init__(self, future, stack_frames_to_pop_off=2):
        if _debug:
            future.__current_stack__ = traceback.format_stack()
        else:
            future.__current_stack__ = traceback.format_stack()[:(-stack_frames_to_pop_off)]
        future.__original_result__ = future.result
        future.result = types.MethodType(result_with_proper_traceback, future)
        self.__future__ = future

    def __repr__(self):
        return repr(self.__future__.result())

    def __str__(self):
        return str(self.__future__.result())

    def __bytes__(self):
        return bytes(self.__future__.result())

    def __format__(self, format_spec):
        return format(self.__future__.result(), format_spec)

    def __lt__(self, other):
        return self.__future__.result() < other

    def __le__(self, other):
        return self.__future__.result() <= other

    def __eq__(self, other):
        return self.__future__.result() == other

    def __ne__(self, other):
        return self.__future__.result() != other

    def __gt__(self, other):
        return self.__future__.result() > other

    def __ge__(self, other):
        return self.__future__.result() >= other

    def __hash__(self):
        return hash(self.__future__.result())

    def __bool__(self):
        return bool(self.__future__.result())

    def __dir__(self):
        return dir(self.__future__.result())

    def __get__(self, instance, owner):
        return self.__future__.result().__get__(instance, owner)

    def __set__(self, instance, value):
        return self.__future__.result().__set__(instance, value)

    def __delete__(self, instance):
        return self.__future__.result().__delete__(instance)

    def __call__(self, *args, **kwargs):
        return self.__future__.result()(*args, **kwargs)

    def __len__(self):
        return len(self.__future__.result())

    def __length_hint__(self):
        return self.__future__.result().__length_hint__()

    def __getitem__(self, key):
        return self.__future__.result()[key]

    def __setitem__(self, key, value):
        self.__future__.result()[key] = value

    def __delitem__(self, key):
        del self.__future__.result()[key]

    def __iter__(self):
        return iter(self.__future__.result())

    def __reversed__(self):
        return reversed(self.__future__.result())

    def __contains__(self, item):
        return item in self.__future__.result()

    def __add__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 + x2, self.__future__, other))

    def __sub__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 - x2, self.__future__, other))

    def __mul__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 * x2, self.__future__, other))

    def __truediv__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 / x2, self.__future__, other))

    def __floordiv__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 // x2, self.__future__, other))

    def __mod__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 % x2, self.__future__, other))

    def __divmod__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: divmod(x1, x2), self.__future__, other))

    def __pow__(self, other, modulo=None):
        return pow(self.__future__.result(), other, modulo)

    def __lshift__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 << x2, self.__future__, other))

    def __rshift__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 >> x2, self.__future__, other))

    def __and__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 & x2, self.__future__, other))

    def __xor__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 ^ x2, self.__future__, other))

    def __or__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 | x2, self.__future__, other))

    def __radd__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 + x2, other, self.__future__))

    def __rsub__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 - x2, other, self.__future__))

    def __rmul__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 * x2, other, self.__future__))

    def __rtruediv__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 / x2, other, self.__future__))

    def __rfloordiv__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 // x2, other, self.__future__))

    def __rmod__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 % x2, other, self.__future__))

    def __rdivmod__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: divmod(x1, x2), other, self.__future__))

    def __rpow__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: pow(x1, x2), other, self.__future__))

    def __rlshift__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 << x2, other, self.__future__))

    def __rrshift__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 >> x2, other, self.__future__))

    def __rand__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 & x2, other, self.__future__))

    def __rxor__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 ^ x2, other, self.__future__))

    def __ror__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 | x2, other, self.__future__))

    def __neg__(self):
        return -self.__future__.result()

    def __pos__(self):
        return +self.__future__.result()

    def __abs__(self):
        return abs(self.__future__.result())

    def __invert__(self):
        return ~self.__future__.result()

    def __complex__(self):
        return complex(self.__future__.result())

    def __int__(self):
        return int(self.__future__.result())

    def __float__(self):
        return float(self.__future__.result())

    def __round__(self, n=None):
        return round(self.__future__.result(), n)

    def __index__(self):
        from operator import index
        return index(self.__future__.result())

    def __enter__(self):
        return self.__future__.result().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        return self.__future__.result().__exit__(exc_type, exc_value, traceback)

    def __objclass__(self):
        return self.__future__.result().__objclass__

    def __getattribute__(self, name):
        if name == '__future__':
            return super(ResultProxy, self).__getattribute__('__future__')
        if name == '__class__':
            return self.__future__.result().__class__
        return self.__future__.result().__getattribute__(name)


class OperatorFuture(object):

    def __init__(self, op, x1, x2):
        self.op = op
        self.x1 = x1
        self.x2 = x2
        self._cached = False

    def result(self):
        if not self._cached:
            stack = [self.evaluate(self)]
            result = None
            exception = None
            while stack:
                try:
                    node = stack[-1].send(result)
                    stack.append(self.evaluate(node))
                    result = None
                except StopIteration as exc:
                    stack.pop()
                    result, exception = exc.args[0]
                if exception:
                    break
            self._result = result
            self._exception = exception
            self._cached = True
        if self._exception:
            raise self._exception
        return self._result

    def evaluate(self, node):
        result = None
        exception = None
        if type(node) == ResultProxy:
            result = yield node.__future__
        elif type(node) == Future:
            try:
                result = node.result()
            except BaseException as exc:
                exception = exc
        elif type(node) == OperatorFuture:
            x1 = yield node.x1
            x2 = yield node.x2
            try:
                result = node.op(x1, x2)
            except BaseException as exc:
                exception = exc
        else:
            result = node
        raise StopIteration((result, exception))


def result_with_proper_traceback(future):
    try:
        return future.__original_result__()
    except ResultEvaluationError:
        raise
    except TransportException as exc:
        traceback_info = exc.traceback_info
    except BaseException as exc:
        traceback_info = traceback.format_exception_only(type(exc), exc)

    original_traceback = '\n    '.join(''.join(['\n\nOriginal Traceback (most recent call last):\n'] + future.__current_stack__ + traceback_info).split('\n'))
    raise ResultEvaluationError(original_traceback)
