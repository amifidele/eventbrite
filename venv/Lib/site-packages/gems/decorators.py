# -*- coding: utf-8 -*-
#
# Useful decorators.
#
# @author <bprinty@gmail.com>
# ------------------------------------------------


# imports
# -------
from functools import wraps
import inspect
from future.utils import raise_with_traceback
from .datatypes import composite


# class-related
# -------------
def require(method):
    """
    Decorator for managing chained dependencies of different class
    properties. The @require decorator allows developers to specify
    that a function call must be operated on before another property
    or function call is accessed, so that data and processing for an
    entire class can be evaluated in a lazy way (i.e. not all upon
    instantiation).

    Examples:

        >>> class Foo(Bar):
        >>>
        >>>    def a(self):
        >>>        print 'a!'
        >>>        return 1
        >>>
        >>>    @require('a')
        >>>    @property
        >>>    def b(self):
        >>>        print 'b!'
        >>>        return self.a + 1
        >>>
        >>> foo = Foo()
        >>> print foo.b
        >>>
        'a!'
        'b!'
        2
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # throw exception if input class doesn't have requirement
            if not hasattr(args[0], method):
                raise AssertionError('{} class has no method {}()'.format(args[0].__class__.__name__, method))

            # create property to record that method has been called
            callmethod = method + '_called'
            if not hasattr(args[0], callmethod):
                setattr(args[0], callmethod, False)

            # call the method if it hasn't yet been called
            if not getattr(args[0], callmethod):
                getattr(args[0], method)()
                setattr(args[0], callmethod, True)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class cached(object):
    """
    Special implementation of cached_property by pydanny to allow for
    tagging and invalidation of caches.

    Examples:
        >>> class Foo(object):
        >>> @cached.tag('stateful')
        >>> def time(self)
        >>>     return str(datetime.now().time())
        >>>
        >>> obj = Foo()
        >>> obj.time
        '11:24:33.613401'
        >>> time.sleep(5)
        >>> obj.time
        '11:24:33.613401'
        >>> cached.invalidate(obj, 'stateful')
        >>> obj.time
        '11:26:35.197487'
    """

    def __init__(self, func, *tags):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func
        self.tags = frozenset(tags)
        return

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

    @classmethod
    def tag(cls, *tags):
        return lambda f: cls(f, *tags)

    @staticmethod
    def invalidate(obj, tag):
        for base in obj.__class__.mro():
            for key, value in base.__dict__.items():
                if isinstance(value, cached) and tag in value.tags:
                    obj.__dict__.pop(key, None)
        return


# exception-related
# -----------------
def exception(exception):
    """
    Wrap function/method with specific exception if any
    exception occurs during function execution.
 
    Args:
        exception (Exception): Exception to re-cast error as.

    Examples:
        >>> from gems import exception
        >>>
        >>> class MyCustomException(Exception):
        >>>     pass
        >>>
        >>> @exception(MyCustomException)
        >>> def func():
        >>>     return 1 / 0
        >>>
        >>> func()
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "gems/decorators.py", line 96, in wrapper
            return func(*args, **kwargs)
          File "<stdin>", line 3, in func
        __main__.MyCustomException: integer division or modulo by zero
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exe:
                raise raise_with_traceback(exception(exe))
        return wrapper
    return decorator


# function-related
# ----------------
def keywords(func):
    """
    Accumulate all dictionary and named arguments as
    keyword argument dictionary. This is generally useful for
    functions that try to automatically resolve inputs.

    Examples:
        >>> @keywords
        >>> def test(*args, **kwargs):
        >>>     return kwargs
        >>>
        >>> print test({'one': 1}, two=2)
        {'one': 1, 'two': 2}
    """
    @wraps(func)
    def decorator(*args, **kwargs):
        idx = 0 if inspect.ismethod(func) else 1
        if len(args) > idx:
            if isinstance(args[idx], (dict, composite)):
                for key in args[idx]:
                    kwargs[key] = args[idx][key]
                args = args[:idx]
        return func(*args, **kwargs)
    return decorator
