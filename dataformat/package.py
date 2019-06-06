import os

from dataformat.xml_file import XMLFile, MetaXMLFile, NullFile
from dataformat.attachments import AttachmentCollection


class DataPackage(object):

    @classmethod
    def is_package(cls, path):
        checked_files = ['meta.xml', 'store.xml', 'attachments.xml', 'attachments']
        return all([os.path.exists(os.path.join(path, file)) for file in checked_files])

    @classmethod
    def open(cls, path, readonly=False, meta=True, store=True, attachments=True):
        # TODO : better methods argument
        meta_file = MetaXMLFile.open(os.path.join(path, 'meta.xml'), readonly) if meta else NullFile('MetaXMLFile')
        store_file = XMLFile.open(os.path.join(path, 'store.xml'), readonly) if store else NullFile('XMLFile')
        attach_col = AttachmentCollection.open(path, readonly) if attachments else NullFile('AttachmentCollection')
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
