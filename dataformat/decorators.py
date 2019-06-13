from functools import wraps
from dataformat.exceptions import DataFormatReadOnlyException


def readonly_check(arg1=None):
    """
    This is decorator method which wraps calling method and checks value of special attribute ('readonly') to verify
    if this operation can proceed or fail.

    :param arg1: decorated method or which attribute to check
    """
    attr = '_readonly'

    def wrap(func):
        @wraps(func)
        def inner(instance, *args, **kwargs):
            if hasattr(instance, attr) and getattr(instance, attr):
                raise DataFormatReadOnlyException
            else:
                return func(instance, *args, **kwargs)

        return inner
    if callable(arg1):
        return wrap(arg1)
    else:
        attr = arg1
        return wrap


def readonly_check_methods(*methods):
    """
    This is class decorator which iterates through provided method names and decorate each method with "readonly_check"
    decorator. This decorator does NOT create a new child class, but change methods of original class.
    :param methods: list of method names which will be decorate
    """
    def wrapper(cls):
        for mtd_name in methods:
            org_mtd = getattr(cls, mtd_name)
            setattr(cls, mtd_name, readonly_check(org_mtd))
        return cls
    return wrapper
