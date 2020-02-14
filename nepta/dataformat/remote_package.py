import os
from dataclasses import dataclass

from nepta.dataformat.xml_file import XMLFile, Section
from nepta.dataformat.decorators import readonly_check_methods


@dataclass(frozen=True)
class RemotePackage(object):
    host: str
    path: str


# TODO: make generic collection maybe
@readonly_check_methods('new', 'save', '__setattr__')
class RemotePackageCollection(object):
    META_FILE = 'remote_packages.xml'
    RMPKG_DIR = 'remote_packages'
    ELEM_NAME = 'remote_package'
    ROOT_NAME = 'remote_packages'

    @classmethod
    def open(cls, path, readonly=False):
        meta = XMLFile.open(os.path.join(path, cls.META_FILE))
        collection = []
        for rem_pkg in meta.root:
            collection.append(RemotePackage(**rem_pkg.params))
        return cls(path, meta, collection, readonly)

    @classmethod
    def create(cls, path):
        os.mkdir(os.path.join(path, cls.RMPKG_DIR))
        pckg_meta = XMLFile.create(os.path.join(path, cls.META_FILE))
        pckg_meta.root = Section(cls.ROOT_NAME)
        return cls(path, pckg_meta, [], False)

    def __init__(self, path, meta, collection, readonly):
        self.path = path
        self.meta = meta
        self.collection = collection
        self._readonly = readonly

    def __iter__(self):
        return iter(self.collection)

    def __len__(self):
        return len(self.collection)

    def new(self, hostname):
        path = os.path.join(self.path, self.RMPKG_DIR, hostname)
        os.mkdir(path)
        self.collection.append(RemotePackage(hostname, path))
        return self.collection[-1]

    def save(self):
        self.meta.root = Section(self.ROOT_NAME)
        for rem_pkg in self.collection:
            attachments_params = dict(rem_pkg.__dict__)
            self.meta.root.subsections.append(Section(self.ELEM_NAME, attachments_params))
        self.meta.save()
