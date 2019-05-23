from dataformat.decorators import readonly_check, readonly_check_methods
from dataformat.safe_types import DataFormatOrderedDict, DataFormatList


@readonly_check_methods('__setattr__', 'delete_subsections')
class Section(object):
    def __init__(self, name, params=None, **kwargs):
        self.name = name
        self._readonly = False
        self.params = DataFormatOrderedDict(params) if params is not None else DataFormatOrderedDict()
        self.params.update(kwargs)
        self.subsections = SectionCollection()

    def __getitem__(self, index):
        return self.subsections.filter(index)

    def __iter__(self):
        return iter(self.subsections)

    def __repr__(self):
        return 'Section %s (%s)' % (self.name, self.params or '')

    @property
    def readonly(self):
        return self._readonly

    @readonly.setter
    def readonly(self, val):
        self._readonly = val
        self.params.readonly = val
        self.subsections.readonly = val

    def delete_subsections(self):
        self.subsections = SectionCollection()

    def str_tree(self):
        return "\n".join(str(x) for x in DisplayableSection.generate_tree(self))


@readonly_check_methods('append', '__setattr__')
class SectionCollection(object):

    def __init__(self):
        self.sections = DataFormatList()
        self._readonly = False

    def __iter__(self):
        return iter(self.sections)

    def __len__(self):
        return len(self.sections)

    def __getitem__(self, index):
        return self.sections[index]

    @property
    def readonly(self):
        return self._readonly

    @readonly.setter
    def readonly(self, val):
        self._readonly = val
        self.sections.readonly = val

    def filter(self, name=None, **params):
        ret = SectionCollection()
        for s in self:
            if name is None or s.name == name:
                if len(params):
                    matched = True
                    for k, v in params.items():
                        if k not in s.params or s.params[k] != v:
                            matched = False
                    if matched:
                        ret.append(s)
                else:
                    ret.append(s)
        return ret

    def append(self, s):
        self.sections.append(s)


class DisplayableSection(object):
    """
    Inspired by : https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
    """
    child_prefix_middle = '├──'
    child_prefix_last = '└──'
    parent_prefix_middle = '|   '
    parent_prefix_last = '    '

    def __init__(self, section, parent, is_last):
        self.section = section
        self.parent = parent
        self.parent_prefix = self.get_parent_prefix()
        self.is_last = is_last

    @classmethod
    def generate_tree(cls, section, parent=None, is_last=False):
        root = cls(section, parent, is_last)
        yield root
        i = 0
        last_id = len(section.subsections) - 1
        for subsection in section:
            yield from cls.generate_tree(subsection, root, i == last_id)
            i += 1

    def get_parent_prefix(self):
        parent_prefix_list = []
        parent = self.parent
        while parent and parent.parent is not None:
            parent_prefix_list.append(self.parent_prefix_last if parent.is_last else self.parent_prefix_middle)
            parent = parent.parent
        return "".join(reversed(parent_prefix_list))

    def __str__(self):
        if self.parent is None:
            return str(self.section)
        bundle_name = "{!s} {!s}".format(self.child_prefix_last if self.is_last else self.child_prefix_middle,
                                         self.section)
        return self.parent_prefix + bundle_name
