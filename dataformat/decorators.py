from dataformat.exceptions import DataFormatReadOnlyException


def readonly_check(func):
    attr = 'readonly'

    def inner(instance, *args, **kwargs):
        if getattr(instance, attr):
            raise DataFormatReadOnlyException
        else:
            func(instance, *args, **kwargs)

    return inner
