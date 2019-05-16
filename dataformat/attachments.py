import os
from dataclasses import dataclass

from dataformat.xml_file import XMLFile


@dataclass
class GenericAttachment:
    origin: str
    type: str
    path: str
    uuid: str


class FileAttachment(GenericAttachment):
    pass


class DirectoryAttachment(GenericAttachment):
    pass


class AttachmentCollection(object):
    META_FILE = 'attachments.xml'
    ATTCH_DIR = 'attachments'

    @classmethod
    def open(cls, path):
        att_meta = XMLFile.open(os.path.join(path, cls.META_FILE))
        collection = []

        for attach in att_meta.root:
            if attach.params['name'] == 'Command':
                collection.append(FileAttachment(attach.params['origin'],attach.params['name'], attach.params['path'], attach.params['uuid']))
            elif attach.params['name'] == 'Directory':
                collection.append(DirectoryAttachment(attach.params['origin'], attach.params['name'], attach.params['path'], attach.params['uuid']))

        return cls(path, att_meta, collection)

    @classmethod
    def create(cls, path):
        os.mkdir(os.path.join(path, cls.ATTCH_DIR))
        att_meta = XMLFile.create(os.path.join(path, cls.META_FILE))
        return cls(path, att_meta, [])

    def __init__(self, path, att_meta, collection):
        self.path = path
        self.att_meta = att_meta
        self.collection = collection

    def save(self):
        self.att_meta.save()
        # TODO check if specified attachments are really here

    def new(self):
        raise NotImplemented
        # TODO copy factory from libres ?


