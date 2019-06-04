import os
import re
from uuid import uuid4

from dataclasses import dataclass
from enum import Enum

from dataformat.xml_file import XMLFile
from dataformat.section import Section
from dataformat.decorators import readonly_check_methods


@readonly_check_methods('__setattr__')
@dataclass
class Attachment:
    origin: str
    name: str
    path: str
    uuid: str
    readonly: bool = False


@readonly_check_methods('new', 'save', '__setattr__')
class AttachmentCollection(object):
    META_FILE = 'attachments.xml'
    ATTCH_DIR = 'attachments'
    ELEM_NAME = 'attachment'
    ROOT_NAME = 'attachments'

    class Types(Enum):
        FILE = 'File'
        DIRECTORY = 'Directory'
        COMMAND = 'Command'
        URL = 'Url'

    @classmethod
    def open(cls, path, readonly=False):
        att_meta = XMLFile.open(os.path.join(path, cls.META_FILE))
        collection = []

        for attach in att_meta.root:
            collection.append(Attachment(attach.params['origin'], attach.params['name'], attach.params['path'],
                                         attach.params['uuid'], readonly))

        return cls(path, att_meta, collection, readonly)

    @classmethod
    def create(cls, path):
        os.mkdir(os.path.join(path, cls.ATTCH_DIR))
        att_meta = XMLFile.create(os.path.join(path, cls.META_FILE))
        att_meta.root = Section(cls.ROOT_NAME)
        return cls(path, att_meta, [], False)

    def __init__(self, path, att_meta, collection, readonly):
        self.path = path
        self.att_meta = att_meta
        self.collection = collection
        self.readonly = readonly

    def __str__(self):
        return "{}: {}\n\t{}".format(self.__class__.__name__, self.path, "\n\t".join(map(str, self.collection)))

    def __iter__(self):
        return iter(self.collection)

    def __len__(self):
        return len(self.collection)

    def save(self):
        self.att_meta.root = Section(self.ROOT_NAME)
        for att in self.collection:
            self.att_meta.root.subsections.append(Section(self.ELEM_NAME, dict(att.__dict__)))
        self.att_meta.save()

    def new(self, type, origin):
        def slugify(name):
            value = re.sub(r'[^\w\s-]', '-', name).strip().lower()
            return re.sub(r'[-\s]+', '--', value)

        new_uuid = str(uuid4())
        new_dir = os.path.join(self.ATTCH_DIR, type.value, slugify(origin))
        new_path = os.path.join(new_dir, new_uuid)

        new_att = Attachment(origin, type.value, new_path, new_uuid)
        self.collection.append(new_att)

        if type == self.Types.DIRECTORY:
            os.makedirs(os.path.join(self.path, new_path))
        else:
            os.makedirs(os.path.join(self.path, new_dir))

        return new_att


