import threading
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future


__all__ = ['fork', 'cpu_bound', 'io_bound', 'unsafe', 'UnknownWaitingForError']


_pools_of = threading.local()
_pools_of.processes = ProcessPoolExecutor()
_pools_of.threads = ThreadPoolExecutor(_pools_of.processes._max_workers)


def fork(callable_, *args, **kwargs):
    """
    Submit the given callable to another process or thread
    depending on its io- or cpu-boundness.
    """
    has_side_effects = getattr(callable_, '__has_side_effects__', False)
    if has_side_effects:
        return callable_(*args, **kwargs)
    waiting_for = getattr(callable_, '__waiting_for__', 'cpu')
    if waiting_for == 'cpu':
        return BlockingFuture(_pools_of.processes.submit(_safety_wrapper, callable_, *args, **kwargs))
    elif waiting_for == 'io':
        return BlockingFuture(_pools_of.threads.submit(_safety_wrapper, callable_, *args, **kwargs))
    raise UnknownWaitingForError(waiting_type)


def _safety_wrapper(callable_, *args, **kwargs):
    _pools_of.processes = ProcessPoolExecutor()
    _pools_of.threads = ThreadPoolExecutor(_pools_of.processes._max_workers)
    result = callable_(*args, **kwargs)
    _pools_of.processes.shutdown()
    _pools_of.threads.shutdown()
    return result


def cpu_bound(callable_):
    """
    Mark the given callable as mainly cpu-bound and safe for running off the MainThread.
    """
    callable_.__has_side_effects__ = False
    callable_.__waiting_for__ = 'cpu'
    return callable_


def io_bound(callable_):
    """
    Mark the given callable as mainly io-bound and safe for running off the MainThread.
    """
    callable_.__has_side_effects__ = False
    callable_.__waiting_for__ = 'io'
    return callable_


def unsafe(callable_):
    """
    Mark the given callable as not safe for running somewhere else than the MainThread.
    """
    callable_.__has_side_effects__ = True
    return callable_


def UnknownWaitingForError(Exception):
    pass


class BlockingFuture:
    def __init__(self, future):
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

    def __objclass__(self):
        return self.__future__.result().__objclass__

    def __getattribute__(self, name):
        if name == '__future__':
            return super().__getattribute__('__future__')
        if name == '__class__':
            return self.__future__.result().__class__
        return self.__future__.result().__getattribute__(name)

