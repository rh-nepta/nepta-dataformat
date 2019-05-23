from functools import wraps

from dataformat.exceptions import DataFormatReadOnlyException


def readonly_check(arg1=None):
    attr = 'readonly'

    def wrap(func):
        @wraps(func)
        def inner(instance, *args, **kwargs):
            if getattr(instance, attr):
                raise DataFormatReadOnlyException
            else:
                func(instance, *args, **kwargs)

        return inner
    if callable(arg1):
        return wrap(arg1)
    else:
        attr = arg1
        return wrap


def setattr_readonly_check(cls):
    attr = 'readonly'

    # TODO think about wraps for class
    class Wrapped(cls):
        def __setattr__(self, key, value):
            if hasattr(self, attr) and getattr(self, attr):
                raise DataFormatReadOnlyException
            else:
                super().__setattr__(key, value)

    Wrapped.__name__ = cls.__name__
    return Wrapped
