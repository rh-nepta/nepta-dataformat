import os
from dataclasses import dataclass

from dataformat.xml_file import XMLFile


@dataclass
class GenericAttachment:
    origin: str
    path: str
    uuid: str


class FileAttachment(GenericAttachment):
    pass


class CommandAttachment(GenericAttachment):
    pass


class DirectoryAttachment(GenericAttachment):
    pass


class UrlAttachment(GenericAttachment):
    pass


class AttachmentCollection(object):

    @classmethod
    def open(cls, path):
        att_meta = XMLFile.open(os.path.join(path, 'attachments.xml'))
        collection = []

        for attach in att_meta.root:
            if attach.params['name'] == 'Command':
                collection.append(CommandAttachment(attach.params['origin'], attach.params['path'], attach.params['uuid']))

        return cls(path, att_meta, collection)

    @classmethod
    def create(cls, path):
        raise NotImplemented

    def __init__(self, path, att_meta, collection):
        self.path = path
        self.att_meta = att_meta
        self.collection = collection

    def save(self):
        raise NotImplemented
    

