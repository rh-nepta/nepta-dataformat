import os
import re
from uuid import uuid4

from dataclasses import dataclass
from enum import Enum

from dataformat.xml_file import XMLFile
from dataformat.section import Section
from dataformat.decorators import readonly_check_methods
from dataformat.exceptions import DataFormatDuplicateKey, DataFormatBadType


class Types(Enum):
    FILE = 'File'
    DIRECTORY = 'Directory'
    COMMAND = 'Command'
    URL = 'Url'


@dataclass(frozen=True)
class Attachment:
    origin: str
    name: Types  # backward compatibility with libres, this attr specify type
    path: str
    uuid: str
    alias: str = None


@readonly_check_methods('new', 'save', '__setattr__')
class AttachmentCollection(object):
    META_FILE = 'attachments.xml'
    ATTCH_DIR = 'attachments'
    ELEM_NAME = 'attachment'
    ROOT_NAME = 'attachments'

    @classmethod
    def open(cls, path, readonly=False):
        attachment_metas = XMLFile.open(os.path.join(path, cls.META_FILE))
        collection = []
        alias_map = {}

        for attachment in attachment_metas.root:
            collection.append(Attachment(**attachment.params))
            if 'alias' in attachment.params.keys():
                alias_map[attachment.params['alias']] = collection[-1]

        return cls(path, attachment_metas, collection, alias_map, readonly)

    @classmethod
    def create(cls, path):
        os.mkdir(os.path.join(path, cls.ATTCH_DIR))
        att_meta = XMLFile.create(os.path.join(path, cls.META_FILE))
        att_meta.root = Section(cls.ROOT_NAME)
        return cls(path, att_meta, [], {}, False)

    def __init__(self, path, att_meta, collection, alias_map, readonly):
        self.path = path
        self.att_meta = att_meta
        self.collection = collection
        self.alias_map = alias_map
        self._readonly = readonly

    def __str__(self):
        return "{}: {}\n\t{}".format(self.__class__.__name__, self.path, "\n\t".join(map(str, self.collection)))

    def __iter__(self):
        return iter(self.collection)

    def __len__(self):
        return len(self.collection)

    def __getitem__(self, item):
        return self.alias_map[item]

    def save(self):
        self.att_meta.root = Section(self.ROOT_NAME)
        for attachment in self.collection:
            attachments_params = dict(attachment.__dict__)
            if attachment.alias is None:
                attachments_params.pop('alias')
            self.att_meta.root.subsections.append(Section(self.ELEM_NAME, attachments_params))
        self.att_meta.save()

    @staticmethod
    def slugify(name):
        value = re.sub(r'[^\w\s-]', '-', name).strip().lower()
        return re.sub(r'[-\s]+', '--', value)

    def new(self, type, origin, alias=None):
        if alias in self.alias_map.keys():
            raise DataFormatDuplicateKey
        if type not in Types:
            raise DataFormatBadType

        new_uuid = str(uuid4())
        new_dir = os.path.join(self.ATTCH_DIR, type.value, self.slugify(origin))
        new_path = os.path.join(new_dir, new_uuid)

        new_att = Attachment(origin, type.value, new_path, new_uuid, alias)

        self.collection.append(new_att)
        if alias:
            self.alias_map[alias] = new_att

        if type == Types.DIRECTORY:
            os.makedirs(os.path.join(self.path, new_path))
        else:
            os.makedirs(os.path.join(self.path, new_dir))

        return new_att


