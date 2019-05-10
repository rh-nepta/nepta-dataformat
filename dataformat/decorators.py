from functools import wraps

from dataformat.exceptions import DataFormatReadOnlyException


def readonly_check(func):
    attr = 'readonly'

    @wraps(func)
    def inner(instance, *args, **kwargs):
        if getattr(instance, attr):
            raise DataFormatReadOnlyException
        else:
            func(instance, *args, **kwargs)

    return inner


def setattr_readonly_check(cls):
    attr = 'readonly'

    # TODO think about wraps for class
    class Wrapped(cls):
        def __setattr__(self, key, value):
            if hasattr(self, attr) and getattr(self, attr):
                raise DataFormatReadOnlyException
            else:
                super().__setattr__(key, value)
    return Wrapped
