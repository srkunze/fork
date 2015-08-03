from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future


__all__ = ['fork', 'unsafe', 'cpu_bound', 'io_bound', 'UnknownWaitingTypeError']


_process_pool = ProcessPoolExecutor()
_thread_pool = ThreadPoolExecutor(_process_pool._max_workers)


def fork(callable_, *args, **kwargs):
    waiting_type = getattr(callable_, '__waiting_type__', 'cpu')
    if waiting_type == 'cpu':
        return BlockingFuture(_process_pool.submit(callable_, *args, **kwargs))
    elif waiting_type == 'io':
        return BlockingFuture(_thread_pool.submit(callable_, *args, **kwargs))
    elif waiting_type == 'unsafe':
        return callable_(*args, **kwargs)
    raise UnknownWaitingTypeError(waiting_type)


class BlockingFuture:

    def __init__(self, future):
        self.__future__ = future

    def __repr__(self):
        return repr(self.__future__.result())

    def __str__(self):
        return str(self.__future__.result())

    def __hash__(self):
        return hash(self.__future__.result())

    def __dir__(self):
        return dir(self.__future__.result())

    def __objclass__(self):
        return self.__future__.result().__objclass__

    def __getattr__(self, name):
        return getattr(self.__future__.result(), name)

    def __getattribute__(self, name):
        if name == '__class__':
            return self.__future__.result().__class__
        return super().__getattribute__(name)


def unsafe(callable_):
    callable_.__waiting_type__ = 'unsafe'
    return callable_


def cpu_bound(callable_):
    callable_.__waiting_type__ = 'cpu'
    return callable_


def io_bound(callable_):
    callable_.__waiting_type__ = 'io'
    return callable_


def UnknownWaitingTypeError(Exception):
    pass
