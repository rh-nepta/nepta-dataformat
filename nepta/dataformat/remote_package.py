import logging
import os
import shutil
import tarfile
import traceback
from dataclasses import dataclass

from nepta.dataformat.attachments import Path
from nepta.dataformat.decorators import readonly_check_methods
from nepta.dataformat.xml_file import Section, XMLFile

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RemotePackage:
    host: str
    path: Path


# TODO: make generic collection maybe
@readonly_check_methods('new', 'save', '__setattr__')
class RemotePackageCollection:
    META_FILE = 'remote_packages.xml'
    RMPKG_DIR = 'remote_packages'
    ELEM_NAME = 'remote_package'
    ROOT_NAME = 'remote_packages'

    @classmethod
    def open(cls, path, readonly=False):
        meta = XMLFile.open(os.path.join(path, cls.META_FILE))
        collection = []
        for rem_pkg in meta.root:
            rem_pkg.params['path'] = Path(path, rem_pkg.params['path'])
            collection.append(RemotePackage(**rem_pkg.params))
        collection = cls(path, meta, collection, readonly)
        if not readonly:
            try:
                collection.unarchive()
            except Exception as e:
                logger.error('Cannot un-archive remote packages. Ignoring exception for compatibility.')
                logger.error(e)
                traceback.print_exc()
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
        self.collection.append(RemotePackage(hostname, Path(self.path, path)))
        return self.collection[-1]

    def archive(self):
        logger.info('Compressing remote packages directory')
        orig_dir = os.getcwd()
        with tarfile.open(os.path.join(self.path, f'{self.RMPKG_DIR}.tar.xz'), 'w:xz') as tf:
            os.chdir(self.path)
            for item in os.listdir(self.RMPKG_DIR):
                tf.add(os.path.join(self.RMPKG_DIR, item))
            os.chdir(orig_dir)
        shutil.rmtree(os.path.join(self.path, self.RMPKG_DIR))

    def unarchive(self):
        logger.info('Decompressing remote packages archive')
        orig_dir = os.getcwd()
        os.mkdir(os.path.join(self.path, self.RMPKG_DIR))
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
