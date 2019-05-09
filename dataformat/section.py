from collections import OrderedDict


class Section(object):
    def __init__(self, name, **new_unordered_params):
        self.name = name
        self.readonly = False
        self.params = OrderedDict(new_unordered_params)
        self.subsections = SectionCollection()

    def __getitem__(self, index):
        return self.get_subsections_by_name(index)

    def __iter__(self):
        return iter(self.subsections)

    def __repr__(self):
        return 'Section %s (%s)' % (self.name, self.params or '')

    def add_subsection(self, sec):
        self.subsections.append(sec)
        return sec

    def delete_subsections(self):
        self.subsections = SectionCollection()

    def get_subsections_by_name(self, name):
        return self.subsections.filter(name)

    def get_subsections_by_param_val(self, **kwargs):
        return self.subsections.filter(None, **kwargs)


class SectionCollection(object):

    def __init__(self):
        self.sections = []
        self.readonly = False

    def __iter__(self):
        return iter(self.sections)

    def __len__(self):
        return len(self.sections)

    def __getitem__(self, index):
        return self.sections[index]

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
