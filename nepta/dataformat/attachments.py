import os
import re
from uuid import uuid4

from dataclasses import dataclass
from enum import Enum

from nepta.dataformat.xml_file import XMLFile
from nepta.dataformat.section import Section
from nepta.dataformat.decorators import readonly_check_methods
from nepta.dataformat.exceptions import DataFormatDuplicateKey, DataFormatBadType


class _EnumFinder(Enum):

    @classmethod
    def from_value(cls, value):
        for _, member in cls.__members__.items():
            if member.value == value:
                return member

    def __str__(self):
        return self.value


class Types(_EnumFinder):
    FILE = 'File'
    DIRECTORY = 'Directory'
    COMMAND = 'Command'
    URL = 'Url'


class Compression(_EnumFinder):
    NONE = 'None'
    ZIP = 'zip'
    BZIP2 = 'bzip2'
    XZ = 'xz'


@dataclass(frozen=True)
class Path(object):
    root_dir: str
    path: str

    def __str__(self):
        return self.path

    def read(self):
        with open(os.path.join(self.root_dir, self.path), 'r') as f:
            return f.read()

    def write(self, content):
        with open(os.path.join(self.root_dir, self.path), 'w') as f:
            f.write(content)


@dataclass(frozen=True)
class Attachment:
    origin: str
    name: Types  # backward compatibility with libres, this attr specify type
    path: Path
    uuid: str
    alias: str = None
    compression: Compression = Compression.NONE


@readonly_check_methods('new', 'save', '__setattr__')
class AttachmentCollection(object):
    META_FILE = 'attachments.xml'
    ATTCH_DIR = 'attachments'
    ELEM_NAME = 'attachment'
    ROOT_NAME = 'attachments'

    SPACE = '\n\t'

    @classmethod
    def open(cls, path, readonly=False):
        attachment_metas = XMLFile.open(os.path.join(path, cls.META_FILE))
        collection = []
        alias_map = {}

        for attachment in attachment_metas.root:
            attachment.params['path'] = Path(path, attachment.params['path'])
            attachment.params['name'] = Types.from_value(attachment.params['name'])
            if 'compression' in attachment.params.keys():
                attachment.params['compression'] = Compression.from_value(attachment.params['compression'])
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
        return f'{self.__class__.__name__}: {self.path}{self.SPACE}{self.SPACE.join(map(str, self.collection))}'

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

    def new(self, att_type, origin, alias=None, compression=Compression.NONE):
        if alias in self.alias_map:
            raise DataFormatDuplicateKey
        if att_type not in Types:
            raise DataFormatBadType

        new_uuid = str(uuid4())
        new_dir = os.path.join(self.ATTCH_DIR, att_type.value, self.slugify(origin))
        new_path = os.path.join(new_dir, new_uuid)

        new_att = Attachment(origin, att_type, Path(self.path, new_path), new_uuid, alias, compression)

        self.collection.append(new_att)
        if alias:
            self.alias_map[alias] = new_att

        os.makedirs(os.path.join(self.path, new_dir))

        return new_att
