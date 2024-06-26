import os
import xml.etree.ElementTree as ET
from collections import OrderedDict
from xml.dom import minidom

from nepta.dataformat.decorators import readonly_check_methods
from nepta.dataformat.exceptions import DataFormatFileExistsError, DataFormatFileNotFoundError, DataFormatNullFileError
from nepta.dataformat.section import Section


@readonly_check_methods('__setattr__', 'save')
class XMLFile:
    def __init__(self, path, root_section=None, readonly=False):
        self.path = path
        self.root = Section('root') if not root_section else root_section
        self._readonly = readonly

    @classmethod
    def open(cls, path, readonly=False):
        if not os.path.exists(path) and not os.path.isfile(path):
            raise DataFormatFileNotFoundError('File %s does not exists' % path)

        return cls(path, None, readonly=readonly)._load()

    @classmethod
    def create(cls, path):
        if os.path.exists(path):
            raise DataFormatFileExistsError('File %s already exists' % path)

        open(path, 'w').close()
        return cls(path)

    @property
    def readonly(self):
        return self._readonly

    def save(self):
        self._save()

    def _load(self):
        # Recursively load all child nodes (and its params)
        # and interpret them as sections
        def load_sections(root_node):
            params_list = OrderedDict(root_node.attrib.items())
            sec = Section(root_node.tag, params_list)

            for child_node in root_node:
                if child_node.attrib.get('type', '') == 'list':
                    sec.subsections.append(
                        Section(
                            child_node.tag,
                            value=[sub_node.attrib['value'] for sub_node in child_node],
                            params={k: v for k, v in child_node.attrib.items() if k != 'type'},
                        )
                    )
                else:
                    sec.subsections.append(load_sections(child_node))

            sec.readonly = self.readonly
            return sec

        tree = ET.parse(self.path)
        root = tree.getroot()
        self.__dict__['root'] = load_sections(root)
        return self

    def _save(self):
        def save_sections(sec):
            el = ET.Element(sec.name)
            for index, val in sec.params.items():
                if isinstance(val, list):
                    el.set('type', 'list')
                    for item in val:
                        el.append(ET.Element('item', value=item))
                else:
                    el.set(index, str(val))

            for subsec in sec.subsections:
                el.append(save_sections(subsec))

            return el

        root = save_sections(self.root)
        xml_str = ET.tostring(root)
        xml_minidom = minidom.parseString(xml_str)
        xml_file = open(self.path, 'w')
        xml_minidom.writexml(xml_file, indent='  ', addindent='  ', newl='\n')
        xml_file.close()


@readonly_check_methods('save', '__setitem__', 'update')
class MetaXMLFile:
    @classmethod
    def open(cls, path, readonly=False):
        file = XMLFile.open(path)
        meta_sec = file.root.subsections.filter('Settings')[0]
        return cls(file, meta_sec, readonly)

    @classmethod
    def create(cls, path):
        file = XMLFile.create(path)
        meta_sec = Section('Settings')
        file.root = Section('BeakerRunResult')
        file.root.subsections.append(meta_sec)
        file.save()
        return cls(file, meta_sec)

    def __init__(self, xml_file, meta_section, readonly=False):
        self._xml_file = xml_file
        self._meta_section_ptr = meta_section
        self._val_dict = {}
        self._readonly = readonly
        for sec in meta_section:
            self._val_dict[sec.name] = sec.params['value']

    def save(self):
        self._meta_section_ptr.delete_subsections()
        for k, v in self._val_dict.items():
            self._meta_section_ptr.subsections.append(Section(k, value=v))
        self._xml_file.save()

    def update(self, kw):
        return self._val_dict.update(kw)

    def get(self, *args, **kwargs):
        return self._val_dict.get(*args, **kwargs)

    def __iter__(self):
        yield from self._val_dict.items()

    def __setitem__(self, key, value):
        self._val_dict[key] = value

    def __getitem__(self, item):
        return self._val_dict[item]

    def __contains__(self, item):
        return self._val_dict.__contains__(item)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._readonly:
            self.save()


class NullFile:
    # TODO think about better solution of this

    def __init__(self, path, *args):  # noqa: ARG002
        self.file = path

    def throw(self):
        raise DataFormatNullFileError(f'{self.file} is not opened. Operation is not permitted!!!')

    def __getattr__(self, item):
        self.throw()

    def __setattr__(self, item, val):
        if item in ['throw', 'file']:
            return super().__setattr__(item, val)
        else:
            self.throw()

    def __getitem__(self, item):
        self.throw()

    def __setitem__(self, item, value):
        self.throw()

    def __len__(self):
        self.throw()

    def __iter__(self):
        self.throw()
