class BaseDataFormatError(Exception):
    pass


class DataFormatFileNotFoundError(BaseDataFormatError):
    pass


class DataFormatFileExistsError(BaseDataFormatError):
    pass


class DataFormatReadOnlyExceptionError(BaseDataFormatError):
    pass


class DataFormatNullFileError(BaseDataFormatError):
    pass


class DataFormatDuplicateKeyError(BaseDataFormatError):
    pass


class DataFormatBadTypeError(BaseDataFormatError):
    pass
