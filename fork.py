from functools import wraps
import threading
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor

__version__ = '0.16'
__version_info__ = (0, 16)
__all__ = [
    'cpu_bound', 'io_bound', 'cpu_bound_fork', 'io_bound_fork', 'contagious_result', 'unsafe',
    'fork', 'fork_contagious', 'fork_noncontagious',
    'contagious',
    'UnknownWaitingForError',
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

    @wraps(callable_)
    def fork_wrapper(*args, **kwargs):
        return fork(callable_, *args, **kwargs)
    fork_wrapper.__is_fork_wrapper__ = True
    fork_wrapper.__wrapped_callable__ = callable_

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
    fork_wrapper.__is_fork_wrapper__ = True
    fork_wrapper.__wrapped_callable__ = callable_
    return fork_wrapper


_settings = threading.local()


class contagious(object):

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self.__class__():
                return func(*args, **kwargs)
        return inner

    def __enter__(self):
        _settings.is_contagious = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        _settings.is_contagious = False
        return bool(exc_type)

contagious = contagious()


def contagious_result(callable_):
    if getattr(callable_, '__is_fork_wrapper__', False):
        callable_.__wrapped_callable__.__future_wrapper__ = ContagiousFutureWrapper
    else:
        callable_.__future_wrapper__ = ContagiousFutureWrapper
    return callable_


def unsafe(callable_):
    """
    Marks callable as not safe for running off the MainThread.
    """
    callable_.__has_side_effects__ = True
    return callable_


_pools_of = threading.local()
_pools_of.processes = ProcessPoolExecutor()
_pools_of.threads = ThreadPoolExecutor(_pools_of.processes._max_workers)


def _fork(future_wrapper, callable_, *args, **kwargs):
    has_side_effects = getattr(callable_, '__has_side_effects__', False)
    if has_side_effects:
        return callable_(*args, **kwargs)
    waiting_for = getattr(callable_, '__waiting_for__', 'cpu')
    if waiting_for == 'cpu':
        return future_wrapper(_pools_of.processes.submit(_safety_wrapper, callable_, *args, **kwargs))
    elif waiting_for == 'io':
        return future_wrapper(_pools_of.threads.submit(_safety_wrapper, callable_, *args, **kwargs))
    raise UnknownWaitingForError(waiting_for)


def fork(callable_, *args, **kwargs):
    """
    Submit a callable to another process or thread
    depending on its io- or cpu-boundness.
    Returns an a future wrapper that acts like the
    real return value.
    """
    if getattr(_settings, 'is_contagious', False):
        return _fork(ContagiousFutureWrapper, callable_, *args, **kwargs)
    future_wrapper = getattr(callable_, '__future_wrapper__', FutureWrapper)
    return  _fork(future_wrapper, callable_, *args, **kwargs)


def fork_noncontagious(callable_, *args, **kwargs):
    """
    Submit a callable to another process or thread
    depending on its io- or cpu-boundness.
    Returns an a future wrapper that acts like the
    real return value.
    Ensures noncontagious futures.
    """
    return _fork(FutureWrapper, callable_, *args, **kwargs)


def fork_contagious(callable_, *args, **kwargs):
    """
    Submit a callable to another process or thread
    depending on its io- or cpu-boundness.
    Returns an a future wrapper that acts like the
    real return value.
    Ensures contagious futures.
    """
    return _fork(ContagiousFutureWrapper, callable_, *args, **kwargs)


def _safety_wrapper(callable_, *args, **kwargs):
    _pools_of.processes = ProcessPoolExecutor()
    _pools_of.threads = ThreadPoolExecutor(_pools_of.processes._max_workers)
    tb = None
    result = None
    try:
        result = callable_(*args, **kwargs)
    except:
        import sys
        import traceback
        tb = traceback.format_tb(sys.exc_info()[2])[1:]
    _pools_of.processes.shutdown()
    _pools_of.threads.shutdown()
    return result, tb


def UnknownWaitingForError(Exception):

    pass


class ResultEvaluationError(Exception):

    pass


class FutureWrapper(object):
    
    def __init__(self, future):
        self.__future__ = future
        import traceback
        self.__future__.current_frame = traceback.format_stack()[:-4]
        def result(self):
            res, exc_info = self.old_result()
            if exc_info:
                original_traceback = ''.join(['\n\n\nOriginal Traceback (most recent call last):\n'] + self.current_frame + exc_info)
                raise ResultEvaluationError(original_traceback)
            return res
        future.old_result = future.result
        import types
        future.result = types.MethodType(result, future)

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
        return other +  self.__future__.result()

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
            return super(FutureWrapper, self).__getattribute__('__future__')
        if name == '__class__':
            return self.__future__.result().__class__
        return self.__future__.result().__getattribute__(name)


class ContagiousFutureWrapper(object):

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
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 + x2, self.__future__, other)

    def __sub__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 - x2, self.__future__, other)

    def __mul__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 * x2, self.__future__, other)

    def __truediv__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 / x2, self.__future__, other)

    def __floordiv__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 // x2, self.__future__, other)

    def __mod__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 % x2, self.__future__, other)

    def __divmod__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: divmod(x1, x2), self.__future__, other)

    def __pow__(self, other, modulo=None):
        return pow(self.__future__.result(), other, modulo)

    def __lshift__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 << x2, self.__future__, other)

    def __rshift__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 >> x2, self.__future__, other)

    def __and__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 & x2, self.__future__, other)

    def __xor__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 ^ x2, self.__future__, other)

    def __or__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 | x2, self.__future__, other)

    def __radd__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 + x2, other, self.__future__)

    def __rsub__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 - x2, other, self.__future__)

    def __rmul__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 * x2, other, self.__future__)

    def __rtruediv__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 / x2, other, self.__future__)

    def __rfloordiv__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 // x2, other, self.__future__)

    def __rmod__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 % x2, other, self.__future__)

    def __rdivmod__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: divmod(x1, x2), other, self.__future__)

    def __rpow__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: pow(x1, x2), other, self.__future__)

    def __rlshift__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 << x2, other, self.__future__)

    def __rrshift__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 >> x2, other, self.__future__)

    def __rand__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 & x2, other, self.__future__)

    def __rxor__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 ^ x2, other, self.__future__)

    def __ror__(self, other):
        return ContagiousOperatorFutureWrapper(lambda x1, x2: x1 | x2, other, self.__future__)

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
            return super(ContagiousFutureWrapper, self).__getattribute__('__future__')
        if name == '__class__':
            return self.__future__.result().__class__
        return self.__future__.result().__getattribute__(name)


class ContagiousOperatorFutureWrapper(ContagiousFutureWrapper):

    def __init__(self, op, x1, x2):
        self.__future__ = OperatorFuture(op, x1, x2)


class OperatorFuture(object):

    def __init__(self, op, x1, x2):
        self.op = op
        self.x1 = x1
        self.x2 = x2
        self._cached = False
        self._result = None
        self._exception = None

    def result(self):
        if not self._cached:
            try:
                x1 = self.x1
                if hasattr(x1, 'result'):
                    x1 = x1.result()
                x2 = self.x2
                if hasattr(x2, 'result'):
                    x2 = x2.result()
                self._result = self.op(x1, x2)
            except BaseException as e:
                self._exception = e
            self._cached = True
        if self._exception:
            raise self._exception
        else:
            return self._result
