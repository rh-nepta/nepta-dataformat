import os
from enum import Flag, auto
from collections import defaultdict

from nepta.dataformat.xml_file import XMLFile, MetaXMLFile, NullFile
from nepta.dataformat.attachments import AttachmentCollection
from nepta.dataformat.decorators import readonly_check_methods


class FileFlags(Flag):
    NONE = 0
    META = auto()
    STORE = auto()
    ATTACHMENTS = auto()
    ALL = META | STORE | ATTACHMENTS


@readonly_check_methods('__setattr__')
class DataPackage(object):
    _FILE_CONSTRUCT_MAP = defaultdict(lambda: NullFile, {
        FileFlags.META: MetaXMLFile.open,
        FileFlags.STORE: XMLFile.open,
        FileFlags.ATTACHMENTS: AttachmentCollection.open,
    })

    @classmethod
    def is_package(cls, path):
        checked_files = ['meta.xml', 'store.xml', 'attachments.xml', 'attachments']
        return all([os.path.exists(os.path.join(path, file)) for file in checked_files])

    @classmethod
    def open(cls, path, file_opts=FileFlags.ALL, readonly=False):
        meta_file = cls._FILE_CONSTRUCT_MAP[file_opts & FileFlags.META](os.path.join(path, 'meta.xml'), readonly)
        store_file = cls._FILE_CONSTRUCT_MAP[file_opts & FileFlags.STORE](os.path.join(path, 'store.xml'), readonly)
        attach_col = cls._FILE_CONSTRUCT_MAP[file_opts & FileFlags.ATTACHMENTS](path, readonly)
        return cls(path, meta_file, store_file, attach_col, readonly)

    @classmethod
    def create(cls, path):
        os.makedirs(path)
        metas = MetaXMLFile.create(os.path.join(path, 'meta.xml'))
        store = XMLFile.create(os.path.join(path, 'store.xml'))
        attachments = AttachmentCollection.create(path)
        return cls(path, metas, store, attachments)

    def __init__(self, path, metas, store, attachments, readonly=False):
        self.path = path
        self.metas = metas
        self.store = store
        self.attachments = attachments
        self._readonly = readonly

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if not self._readonly:
            self.metas.save()
            self.store.save()
            self.attachments.save()
