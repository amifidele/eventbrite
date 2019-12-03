# -*- coding: utf-8 -*-
#
# Useful metaclasses.
#
# @author <bprinty@gmail.com>
# ------------------------------------------------


# imports
# -------
# none yet ...


# metaclasses
# -----------
class DocRequire(type):
    """
    Metaclass forcing requirement of docstrings on all public
    class methods.

    Example:
        >>> # class without docstrings will throw
        >>> # a TypeError
        >>> class A(object):
        >>>     def method(self):
        >>>         return 1
        >>>
        TypeError: method must have a docstring

        >>> # class with docstrings is fine
        >>> class A(object):
        >>>     ''' A class with docstrings '''
        >>>     def method(self):
        >>>         ''' A method  '''
        >>>         return 1
        >>>
    """

    def __init__(self, name, bases, attrs):
        for key, value in attrs.items():
            if key.startswith("__"):
                continue
            if not hasattr(value, "__call__"):
                continue
            if not getattr(value, '__doc__'):
                raise AssertionError("%s must have a docstring" % key)
        type.__init__(self, name, bases, attrs)
