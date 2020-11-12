import os
from dataclasses import dataclass
import tarfile
import shutil
import logging

from nepta.dataformat.xml_file import XMLFile, Section
from nepta.dataformat.decorators import readonly_check_methods

logger = logging.getLogger(__name__)


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
        collection = cls(path, meta, collection, readonly)
        collection.unarchive()
        return collection

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
        path = os.path.join(self.RMPKG_DIR, hostname)
        os.mkdir(os.path.join(self.path, path))
        self.collection.append(RemotePackage(hostname, path))
        return self.collection[-1]

    def archive(self):
        logger.info('Compressing remote packages directory')
        orig_dir = os.getcwd()
        with tarfile.open(os.path.join(self.path, f'{self.RMPKG_DIR}.tar.xz'), 'w:xz') as tf:
            os.chdir(self.path)
            for rem_pkg in self.collection:
                tf.add(rem_pkg.path)
            os.chdir(orig_dir)
        shutil.rmtree(os.path.join(self.path, self.RMPKG_DIR))

    def unarchive(self):
        logger.info('Decompressing remote packages archive')
        orig_dir = os.getcwd()
        tar_path = os.path.join(self.path, f'{self.RMPKG_DIR}.tar.xz')
        with tarfile.open(tar_path, 'r:xz') as tf:
            os.chdir(self.path)
            for mem in tf.getmembers():
                tf.extract(mem)
            os.chdir(orig_dir)
        os.remove(tar_path)

    def save(self):
        logger.debug('Saving remote packages')
        self.meta.root = Section(self.ROOT_NAME)
        for rem_pkg in self.collection:
            attachments_params = dict(rem_pkg.__dict__)
            self.meta.root.subsections.append(Section(self.ELEM_NAME, attachments_params))
        self.meta.save()
        self.archive()
