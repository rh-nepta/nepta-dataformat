from collections import OrderedDict

from nepta.dataformat.decorators import readonly_check_methods


@readonly_check_methods(
    'clear',
    'fromkeys',
    'pop',
    'popitem',
    'update',
    '__delattr__',
    '__delitem__',
    '__setattr__',
    '__setitem__',
)
class DataFormatOrderedDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        self._readonly = False
        super().__init__(*args, **kwargs)


@readonly_check_methods(
    'append',
    'clear',
    'extend',
    'insert',
    'pop',
    'remove',
    'reverse',
    'sort',
    '__iadd__',
    '__imul__',
    '__setattr__',
    '__setitem__',
)
class DataFormatList(list):
    def __init__(self, *args, **kwargs):
        self._readonly = False
        super().__init__(*args, **kwargs)
