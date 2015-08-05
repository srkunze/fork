from functools import wraps
import threading
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor


__version__ = '0.11'
__version_info__ = (0, 11)
__all__ = ['fork', 'cpu_bound', 'io_bound', 'cpu_bound_fork', 'io_bound_fork', 'unsafe', 'UnknownWaitingForError']


_pools_of = threading.local()
_pools_of.processes = ProcessPoolExecutor()
_pools_of.threads = ThreadPoolExecutor(_pools_of.processes._max_workers)


def fork(callable_, *args, **kwargs):
    """
    Submit a callable to another process or thread
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
    raise UnknownWaitingForError(waiting_for)


def _safety_wrapper(callable_, *args, **kwargs):
    _pools_of.processes = ProcessPoolExecutor()
    _pools_of.threads = ThreadPoolExecutor(_pools_of.processes._max_workers)
    result = callable_(*args, **kwargs)
    _pools_of.processes.shutdown()
    _pools_of.threads.shutdown()
    return result


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

    @wraps(callable_)
    def fork_wrapper(*args, **kwargs):
        return fork(callable_, *args, **kwargs)

    import sys
    new_name = '__decorated_{name}__'.format(name=callable_.__name__)
    callable_.__name__ = new_name
    setattr(sys.modules[callable_.__module__], new_name, callable_)

    return fork_wrapper


def io_bound_fork(callable_):
    """
    Converts callable into a fork marked as mainly
    io-bound and safe for running off the MainThread.
    """
    callable_ = io_bound(callable_)
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


def UnknownWaitingForError(Exception):

    pass


class BlockingFuture(object):
    
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

        return self.__future__.result() + other

    def __sub__(self, other):
        return self.__future__.result() - other

    def __mul__(self, other):
        return self.__future__.result() * other

    def __truediv__(self, other):
        return self.__future__.result() / other

    def __floordiv__(self, other):
        return self.__future__.result() // other

    def __mod__(self, other):
        return self.__future__.result() % other

    def __divmod__(self, other):
        return divmod(self.__future__.result(), other)

    def __pow__(self, other, modulo=None):
        return pow(self.__future__.result(), other, modulo)

    def __lshift__(self, other):
        return self.__future__.result() << other

    def __rshift__(self, other):
        return self.__future__.result() >> other

    def __and__(self, other):
        return self.__future__.result() & other

    def __xor__(self, other):
        return self.__future__.result() ^ other

    def __or__(self, other):
        return self.__future__.result() | other

    def __radd__(self, other):
        return other + self.__future__.result()

    def __rsub__(self, other):
        return other - self.__future__.result()

    def __rmul__(self, other):
        return other * self.__future__.result()

    def __rtruediv__(self, other):
        return other / self.__future__.result()

    def __rfloordiv__(self, other):
        return other // self.__future__.result()

    def __rmod__(self, other):
        return other % self.__future__.result()

    def __rdivmod__(self, other):
        return divmod(other, self.__future__.result())

    def __rpow__(self, other):
        return pow(other, self.__future__.result())

    def __rlshift__(self, other):
        return other << self.__future__.result()

    def __rrshift__(self, other):
        return other >> self.__future__.result()

    def __rand__(self, other):
        return other & self.__future__.result()

    def __rxor__(self, other):
        return other ^ self.__future__.result()

    def __ror__(self, other):
        return other | self.__future__.result()

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
            return super(BlockingFuture, self).__getattribute__('__future__')
        if name == '__class__':
            return self.__future__.result().__class__
        return self.__future__.result().__getattribute__(name)
