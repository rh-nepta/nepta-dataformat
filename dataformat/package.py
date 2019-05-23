import os

from dataformat.xml_file import XMLFile, MetaXMLFile
from dataformat.attachments import AttachmentCollection


class DataPackage(object):

    @classmethod
    def is_package(cls, path):
        raise NotImplemented  # TODO

    @classmethod
    def open(cls, path, readonly=False, meta=True, store=True, attach=True):
        # TODO think about NullObj mainly to delete None
        meta = MetaXMLFile.open(os.path.join(path, 'meta.xml'), readonly) if meta else None
        store = XMLFile.open(os.path.join(path, 'store.xml'), readonly) if store else None
        attach = AttachmentCollection.open(path, readonly) if attach else None
        return cls(path, meta, store, attach)

    @classmethod
    def create(cls, path):
        os.makedirs(path)
        meta = MetaXMLFile.create(os.path.join(path, 'meta.xml'))
        store = XMLFile.create(os.path.join(path, 'store.xml'))
        attach = AttachmentCollection.create(path)
        return cls(path, meta, store, attach)

    def __init__(self, path, meta, store, attch, readonly=False):
        self.path = path
        self.meta = meta
        self.store = store
        self.attch = attch
        self.readonly = readonly

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if not self.readonly:
            self.meta.save()
            self.store.save()
            self.attch.save()
