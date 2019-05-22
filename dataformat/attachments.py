import os
from dataclasses import dataclass
from enum import Enum

from dataformat.xml_file import XMLFile


@dataclass
class Attachment:
    origin: str
    type: str
    path: str
    uuid: str


class AttachmentCollection(object):
    META_FILE = 'attachments.xml'
    ATTCH_DIR = 'attachments'
    class Types(Enum):
        FILE = 'File'
        DIRECTORY = 'Directory'
        COMMAND = 'Command'
        URL = 'Url'

    @classmethod
    def open(cls, path):
        att_meta = XMLFile.open(os.path.join(path, cls.META_FILE))
        collection = []

        for attach in att_meta.root:
            collection.append(Attachment(attach.params['origin'], attach.params['type'], attach.params['path'],
                                         attach.params['uuid']))

        return cls(path, att_meta, collection)

    @classmethod
    def create(cls, path):
        os.mkdir(path)
        os.mkdir(os.path.join(path, cls.ATTCH_DIR))
        att_meta = XMLFile.create(os.path.join(path, cls.META_FILE))
        att_meta.root = Section(cls.ROOT_NAME)
        return cls(path, att_meta, [])

    def __init__(self, path, att_meta, collection):
        self.path = path
        self.att_meta = att_meta
        self.collection = collection

    def __str__(self):
        return "{}: {}\n\t{}".format(self.__class__.__name__, self.path, "\n\t".join(map(str, self.collection)))

    def save(self):
        self.att_meta.save()
        # TODO check if specified attachments are really here

    def new(self):
        raise NotImplemented
        # TODO copy factory from libres ?


