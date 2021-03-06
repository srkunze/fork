# -*- coding: utf-8 -*-

import sys
import types
import traceback
import threading
import multiprocessing
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED

__version__ = '0.37'
__version_info__ = (0, 37)
__all__ = [
    'submit', 'process', 'thread',
    'map', 'map_process', 'map_thread',
    'block_map', 'block_map_process', 'block_map_thread',
    'await', 'await_all', 'await_any',
    'cpu_bound', 'io_bound',
    'ResultEvaluationError',
    'evaluate', 'go', 'fork',
]


def submit(callable_, *args, **kwargs):
    """
    Submit the callable to a background job as a process
    or as a thread depending on its io- or cpu-boundness.

    Return an proxy object for the future return value.
    """
    return _submit(callable_, getattr(callable_, '__blocking_type__', 'cpu'), *args, **kwargs)


def process(callable_, *args, **kwargs):
    """
    Submit a callable to a background process.

    Return an proxy object for the future return value.

    NOTE: Use only, if you really need control over the type of background execution.
    """
    return _submit(callable_, 'cpu', *args, **kwargs)


def thread(callable_, *args, **kwargs):
    """
    Submit a callable to a background thread.

    Return an proxy object for the future return value.

    NOTE: Use only, if you really need control over the type of background execution.
    """
    return _submit(callable_, 'io', *args, **kwargs)


def map(callable_, *iterables):
    """
    Submit the callable to a background job as a process
    or as a thread depending on its io- or cpu-boundness
    for each item in iterables with *item as arguments.

    Return an iterable of proxy objects for each future return value.
    """
    return [_submit(callable_, getattr(callable_, '__blocking_type__', 'cpu'), *args) for args in zip(*iterables)]


def map_process(callable_, *iterables):
    """
    Submit the callable to a background process for each item
    in iterables with *item as arguments.

    Return an iterable of proxy objects for each future return value.

    NOTE: Use only, if you really need control over the type of background execution.
    """
    return [_submit(callable_, 'cpu', *args) for args in zip(*iterables)]


def map_thread(callable_, *iterables):
    """
    Submit the callable to a background thread for each item
    in iterables with *item as arguments.

    Return an iterable of proxy objects for each future return value.

    NOTE: Use only, if you really need control over the type of background execution.
    """
    return [_submit(callable_, 'io', *args) for args in zip(*iterables)]


def block_map(callable_, timeout=None, *iterables):
    """
    Submit the callable to a foreground job as a process
    or as a thread depending on its io- or cpu-boundness
    for each item in iterables with *item as arguments.

    Return an iterable of return values.

    Raise concurrent.futures.TimeoutError if not all
    foreground jobs return in time.
    """
    return await_all([_submit(callable_, getattr(callable_, '__blocking_type__', 'cpu'), *args) for args in zip(*iterables)], timeout)


def block_map_process(callable_, timeout=None, *iterables):
    """
    Submit the callable to a new foreground process
    for each item in iterables with *item as arguments.

    Return an iterable of return values.

    Raise concurrent.futures.TimeoutError if not all
    foreground processes return in time.
    """
    return await_all([_submit(callable_, 'cpu', *args) for args in zip(*iterables)], timeout)


def block_map_thread(callable_, timeout=None, *iterables):
    """
    Submit the callable to a new foreground thread
    for each item in iterables with *item as arguments.

    Return an iterable of return values.

    Raise concurrent.futures.TimeoutError if not all
    foreground threads return in time.
    """
    return await_all([_submit(callable_, 'io', *args) for args in zip(*iterables)], timeout)


def await(result_proxy, timeout=None):
    """
    Awaits the completion of a background job of a given result_proxy
    and returns its result value or raises its exception.
    """
    return result_proxy.__future__.result(timeout)


def await_all(result_proxies, timeout=None):
    """
    Awaits the completion of the background jobs of all given result_proxies
    and returns their result values or raises the first exception encountered.
    """
    wait([result_proxy.__future__ for result_proxy in result_proxies], timeout=timeout, return_when=ALL_COMPLETED)
    return [result_proxy.__future__.result() for result_proxy in result_proxies]


def await_any(result_proxies, timeout=None):
    """
    Awaits the completion of a background job of at least one given result_proxy
    and return result values or raises the first exception encountered.
    """
    done_futures = wait([result_proxy.__future__ for result_proxy in result_proxies], timeout=timeout, return_when=FIRST_COMPLETED)
    return [result_proxy for result_proxy in result_proxies if result_proxy.__future__ in done_futures]


_pools_of = threading.local()
_pools_of.processes = None
_pools_of.threads = None


def _submit(callable_, blocking_type, *args, **kwargs):
    if blocking_type == 'cpu':
        if not _pools_of.processes:
            _pools_of.processes = ProcessPoolExecutor()
        return ResultProxy(_pools_of.processes.submit(_safety_wrapper, callable_, *args, **kwargs), 3)
    elif blocking_type == 'io':
        if not _pools_of.threads:
            _pools_of.threads = ThreadPoolExecutor(2 * (multiprocessing.cpu_count() or 1))
        return ResultProxy(_pools_of.threads.submit(_safety_wrapper, callable_, *args, **kwargs), 3)
    raise RuntimeError('unknown blocking_type {blocking_type}'.format(blocking_type=blocking_type))


def _safety_wrapper(callable_, *args, **kwargs):
    _pools_of.processes = None
    _pools_of.threads = None
    try:
        return callable_(*args, **kwargs)
    except BaseException as exc:
        raise TransportException(exc, traceback.format_tb(sys.exc_info()[2])[1:] + traceback.format_exception_only(type(exc), exc))
    finally:
        if _pools_of.processes:
            _pools_of.processes.shutdown()
        if _pools_of.threads:
            _pools_of.threads.shutdown()


def cpu_bound(callable_):
    """
    Marks callable as mainly cpu-bound and safe for running off the MainThread.
    """
    callable_.__blocking_type__ = 'cpu'
    return callable_


def io_bound(callable_):
    """
    Marks callable as mainly io-bound and safe for running off the MainThread.
    """
    callable_.__blocking_type__ = 'io'
    return callable_


class TransportException(Exception):

    #FIXME: remove default parameters when https://github.com/agronholm/pythonfutures/issues/30 is fixed
    def __init__(self, exc=None, traceback_info=None):
        self.exc = exc
        self.traceback_info = traceback_info


class ResultEvaluationError(Exception):

    pass


class ResultProxy(object):

    def __init__(self, future, stack_frames_to_pop_off):
        self.__future__ = future
        future.__original_result__ = future.result
        future.result = types.MethodType(_result_with_proper_traceback, future)
        future.__current_stack__ = traceback.format_stack()[:-stack_frames_to_pop_off]

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
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 + x2, self.__future__, other), 2)

    def __sub__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 - x2, self.__future__, other), 2)

    def __mul__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 * x2, self.__future__, other), 2)

    def __truediv__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 / x2, self.__future__, other), 2)

    def __floordiv__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 // x2, self.__future__, other), 2)

    def __mod__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 % x2, self.__future__, other), 2)

    def __divmod__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: divmod(x1, x2), self.__future__, other), 2)

    def __pow__(self, other, modulo=None):
        return pow(self.__future__.result(), other, modulo)

    def __lshift__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 << x2, self.__future__, other), 2)

    def __rshift__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 >> x2, self.__future__, other), 2)

    def __and__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 & x2, self.__future__, other), 2)

    def __xor__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 ^ x2, self.__future__, other), 2)

    def __or__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 | x2, self.__future__, other), 2)

    def __radd__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 + x2, other, self.__future__), 2)

    def __rsub__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 - x2, other, self.__future__), 2)

    def __rmul__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 * x2, other, self.__future__), 2)

    def __rtruediv__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 / x2, other, self.__future__), 2)

    def __rfloordiv__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 // x2, other, self.__future__), 2)

    def __rmod__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 % x2, other, self.__future__), 2)

    def __rdivmod__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: divmod(x1, x2), other, self.__future__), 2)

    def __rpow__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: pow(x1, x2), other, self.__future__), 2)

    def __rlshift__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 << x2, other, self.__future__), 2)

    def __rrshift__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 >> x2, other, self.__future__), 2)

    def __rand__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 & x2, other, self.__future__), 2)

    def __rxor__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 ^ x2, other, self.__future__), 2)

    def __ror__(self, other):
        return ResultProxy(OperatorFuture(lambda x1, x2: x1 | x2, other, self.__future__), 2)

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

    _result = None
    _exception = None

    def __init__(self, op, x1, x2):
        self.op = op
        self.x1 = x1
        self.x2 = x2
        self._cached = False

    def result(self, timeout=None):
        if not self._cached:
            stack = [self.evaluate(self, timeout)]
            result = None
            exception = None
            while stack:
                try:
                    node = stack[-1].send(result)
                    stack.append(self.evaluate(node, timeout))
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

    @staticmethod
    def evaluate(node, timeout):
        result = None
        exception = None
        if type(node) == ResultProxy:
            result = yield node.__future__
        elif type(node) == Future:
            try:
                result = node.result(timeout)
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

    # Compatibility with concurrency.futures.Future for await_any
    @property
    def _state(self):
        from concurrent.futures._base import CANCELLED_AND_NOTIFIED, FINISHED, CANCELLED
        if self.x1._state == CANCELLED or self.x2._state == CANCELLED:
            return CANCELLED
        if self.x1._state == CANCELLED_AND_NOTIFIED or self.x2._state == CANCELLED_AND_NOTIFIED:
            return CANCELLED_AND_NOTIFIED
        if self.x1._state == FINISHED and self.x2._state == FINISHED:
            return FINISHED
        return None

    @property
    def _condition(self):
        class _condition:
            @classmethod
            def acquire(cls):
                self.x1._condition.acquire()
                self.x2._condition.acquire()
            @classmethod
            def release(cls):
                self.x1._condition.release()
                self.x2._condition.release()
        return _condition


def _result_with_proper_traceback(future, timeout=None):
    try:
        return future.__original_result__(timeout)
    except ResultEvaluationError:           # exception carrying original tracebacks
        raise
    except TransportException as exc:       # exception from the fork
        traceback_info = exc.traceback_info
    except BaseException as exc:            # exception from OperatorFuture
        traceback_info = traceback.format_exception_only(type(exc), exc)

    original_traceback = '\n    '.join(''.join(['\n\nOriginal Traceback (most recent call last):\n'] + future.__current_stack__ + traceback_info).split('\n'))
    raise ResultEvaluationError(original_traceback)


# aliases
go = submit
fork = submit
evaluate = await
