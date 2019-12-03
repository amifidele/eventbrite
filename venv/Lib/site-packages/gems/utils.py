# -*- coding: utf-8 -*-
#
# Decorators for managing repository
#
# @author <bprinty@gmail.com>
# ------------------------------------------------


# imports
# -------
from functools import wraps
import warnings


# decorators
# ----------
def depricated_name(newmethod):
    """
    Decorator for warning user of depricated functions before use.

    Args:
        newmethod (str): Name of method to use instead.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning) 
            warnings.warn(
                "Function {} is depricated, please use {} instead.".format(func.__name__, newmethod),
                category=DeprecationWarning, stacklevel=2
            )
            warnings.simplefilter('default', DeprecationWarning)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def deprecated(func):
    """
    Decorator for warning user of depricated functions before use.
    """
    @wraps(func)
    def decorator(*args, **kwargs):
        # warnings.simplefilter('always', DeprecationWarning)
        warnings.warn(
            "Function {} is depricated. Consult the documentation for a better way of performing this task.".format(func.__name__),
            category=DeprecationWarning, stacklevel=2
        )
        # warnings.simplefilter('default', DeprecationWarning)
        return func(*args, **kwargs)
    return decorator
