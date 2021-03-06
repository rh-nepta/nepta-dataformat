class BaseDataFormatException(Exception):
    pass


class DataFormatFileNotFound(BaseDataFormatException):
    pass


class DataFormatFileExists(BaseDataFormatException):
    pass


class DataFormatReadOnlyException(BaseDataFormatException):
    pass


class DataFormatNullFile(BaseDataFormatException):
    pass


class DataFormatDuplicateKey(BaseDataFormatException):
    pass


class DataFormatBadType(BaseDataFormatException):
    pass
