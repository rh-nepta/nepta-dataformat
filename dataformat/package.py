import os

from dataformat.xml_file import XMLFile, MetaXMLFile, NullFile
from dataformat.attachments import AttachmentCollection


class DataPackage(object):

    @classmethod
    def is_package(cls, path):
        checked_files = ['meta.xml', 'store.xml', 'attachments.xml', 'attachments']
        return all([os.path.exists(os.path.join(path, file)) for file in checked_files])

    @classmethod
    def open(cls, path, readonly=False, meta=True, store=True, attach=True):
        meta_file = MetaXMLFile.open(os.path.join(path, 'meta.xml'), readonly) if meta else NullFile('MetaXMLFile')
        store_file = XMLFile.open(os.path.join(path, 'store.xml'), readonly) if store else NullFile('XMLFile')
        attach_col = AttachmentCollection.open(path, readonly) if attach else NullFile('AttachmentCollection')
        return cls(path, meta_file, store_file, attach_col)

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
