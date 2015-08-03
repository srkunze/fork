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
        return self.__future__.result().__lt__(other)

    def __le__(self, other):
        return self.__future__.result().__le__(other)

    def __eq__(self, other):
        return self.__future__.result().__eq__(other)

    def __ne__(self, other):
        return self.__future__.result().__ne__(other)

    def __gt__(self, other):
        return self.__future__.result().__gt__(other)

    def __ge__(self, other):
        return self.__future__.result().__ge__(other)

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

