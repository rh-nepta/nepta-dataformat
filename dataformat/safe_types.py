from collections import OrderedDict

from dataformat.decorators import setattr_readonly_check, readonly_check


@setattr_readonly_check
class DataFormatOrderedDict(OrderedDict):

    def __init__(self, *args, **kwargs):
        self.readonly = False
        super().__init__(*args, **kwargs)

    @readonly_check
    def update(self, __m, **kwargs):
        super().update(__m, **kwargs)

    @readonly_check
    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    @readonly_check
    def pop(self, k):
        super().pop(k)

    @readonly_check
    def popitem(self, last: bool = ...):
        super().popitem(last)


@setattr_readonly_check
class DataFormatList(list):

    def __init__(self, *args, **kwargs):
        self.readonly = False
        super().__init__(*args, **kwargs)
# TODO make DataFormatList with read only checks
