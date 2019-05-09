import os

from dataformat.xml_file import XMLFile


class DataPackage(object):

    @classmethod
    def open(cls, path, meta=True, store=True, attach=True):
        meta = XMLFile.open(os.path.join(path, 'meta.xml')) if meta else None
        store = XMLFile.open(os.path.join(path, 'store.xml')) if store else None
        return cls(path, meta, store)

    @classmethod
    def create(cls, path):
        os.makedirs(path)
        meta = XMLFile.create(os.path.join(path, 'meta.xml'))
        store = XMLFile.create(os.path.join(path, 'store.xml'))
        return cls(path, meta, store)

    def __init__(self, path, meta, store):
        self.path = path
        self.meta = meta
        self.store = store

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def close(self):
        self.meta.save()
        self.store.save()
