class BaseDataFormatException(Exception):
    pass


class DataFormatFileNotFound(BaseDataFormatException):
    pass


class DataFormatReadOnlyException(BaseDataFormatException):
    pass
