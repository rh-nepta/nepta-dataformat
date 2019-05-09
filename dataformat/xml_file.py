import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from dataformat.section import Section
from dataformat.exceptions import DataFormatFileNotFound


class XMLFile(object):

    def __init__(self, path, root_section=None, overwrite=False):
        self.path = path
        self.root = Section('root') if not root_section else root_section
        self.overwrite = overwrite

    @classmethod
    def open(cls, path):
        if not os.path.exists(path) and not os.path.isfile(path):
            raise DataFormatFileNotFound('File %s does not exists' % path)

        return cls(path, cls._load(path))

    @classmethod
    def create(cls, path):
        if os.path.exists(path):
            raise DataFormatFileNotFound('File %s already exists' % path)

        open(path, 'w').close()
        return cls(path)

    def save(self):
        self._save(self.path, self.root)

    @staticmethod
    def _load(path):
        # Recursively load all child nodes (and its params)
        # and interpret them as sections
        def load_sections(root_node):
            params_list = dict()
            for index, val in root_node.attrib.items():
                params_list[index] = val
            sec = Section(root_node.tag, **params_list)
            for child_node in root_node:
                chld_sec = load_sections(child_node)
                sec.subsections.append(chld_sec)
            # sec.subsections.readonly = self.readonly
            return sec

        tree = ET.parse(path)
        root = tree.getroot()
        root_section = load_sections(root)
        # root_section.readonly = self.readonly
        return root_section

    @staticmethod
    def _save(path, root_section):
        def save_sections(sec):
            el = ET.Element(sec.name)
            for index, val in sec.params.items():
                el.set(index, str(val))

            for subsec in sec.subsections:
                chld = save_sections(subsec)
                el.append(chld)
            return el

        root = save_sections(root_section)
        xml_str = ET.tostring(root)
        xml_minidom = minidom.parseString(xml_str)
        xml_file = open(path, 'w')
        xml_minidom.writexml(xml_file, indent='  ', addindent='  ', newl='\n')
        xml_file.close()


class MetaXMLFile(object):

    @classmethod
    def open(cls, path):
        file = XMLFile.open(path)
        meta_sec = file.root.get_subsections_by_name('Settings')[0]
        return cls(file, meta_sec)

    @classmethod
    def create(cls, path):
        file = XMLFile.create(path)
        meta_sec = Section('Settings')
        file.root = Section('BeakerRunResult')
        file.root.add_subsection(meta_sec)
        file.save()
        return cls(file, meta_sec)

    def __init__(self, xml_file, meta_section):
        self._xml_file = xml_file
        self._meta_section_ptr = meta_section
        self._val_dict = {}
        for sec in meta_section:
            if 'value' in sec.params:
                self._val_dict[sec.name] = sec.params['value']
            elif 'type' in sec.params and sec.params['type'] == 'list':
                self._val_dict[sec.name] = [sec.params['value'] for sec in sec.subsections]

    def save(self):
        self._meta_section_ptr.delete_subsections()
        for k, v in self._val_dict.items():
            self._meta_section_ptr.add_subsection(Section(k, value=v))
        self._xml_file.save()

    def __setitem__(self, key, value):
        self._val_dict[key] = value

    def __getitem__(self, item):
        return self._val_dict[item]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()
