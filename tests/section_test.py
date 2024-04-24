import os
import shutil
from unittest import TestCase

from nepta.dataformat.exceptions import DataFormatReadOnlyExceptionError
from nepta.dataformat.safe_types import DataFormatList, DataFormatOrderedDict
from nepta.dataformat.section import Section, SectionCollection
from nepta.dataformat.xml_file import XMLFile


class SectionTest(TestCase):
    EXAMPLE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'examples')
    TEST_DIR = 'tmp'
    EXIST = os.path.join(TEST_DIR, 's2.xml')

    @classmethod
    def setUpClass(cls):
        os.mkdir(cls.TEST_DIR)

    @classmethod
    def setUp(cls):
        shutil.copy(os.path.join(cls.EXAMPLE_DIR, 'meta.xml'), cls.EXIST)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_DIR)

    def test_readonly(self):
        xml1 = XMLFile.open(self.EXIST, readonly=True)
        root = xml1.root

        self.assertEqual(root.readonly, True)
        self.assertEqual(root.subsections.readonly, True)

        # test Section
        self.assertRaises(DataFormatReadOnlyExceptionError, Section.delete_subsections, root)
        self.assertRaises(DataFormatReadOnlyExceptionError, Section.__setattr__, root, 'name', 'asdf')
        self.assertRaises(DataFormatReadOnlyExceptionError, Section.__setattr__, root, 'params', {})
        self.assertRaises(
            DataFormatReadOnlyExceptionError, DataFormatOrderedDict.__setitem__, root.params, 'key', 'value'
        )
        self.assertRaises(DataFormatReadOnlyExceptionError, DataFormatOrderedDict.update, root.params, 'key', 'value')
        self.assertRaises(DataFormatReadOnlyExceptionError, DataFormatOrderedDict.pop, root.params, 'key')

        subsec = root.subsections[0]
        self.assertRaises(DataFormatReadOnlyExceptionError, Section.delete_subsections, subsec)
        self.assertRaises(DataFormatReadOnlyExceptionError, Section.__setattr__, subsec, 'name', 'asdf')
        self.assertRaises(DataFormatReadOnlyExceptionError, Section.__setattr__, subsec, 'params', {})

    def test_section_tree(self):
        xml1 = XMLFile.open(self.EXIST, readonly=True)
        print()
        print(xml1.root.str_tree())


class SectionCollectionTest(TestCase):
    EXAMPLE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'examples')
    TEST_DIR = 'tmp'
    EXIST = os.path.join(TEST_DIR, 's2.xml')

    @classmethod
    def setUpClass(cls):
        os.mkdir(cls.TEST_DIR)

    @classmethod
    def setUp(cls):
        shutil.copy(os.path.join(cls.EXAMPLE_DIR, 'store.xml'), cls.EXIST)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_DIR)

    def test_readonly(self):
        xml1 = XMLFile.open(self.EXIST, readonly=True)
        root_subs = xml1.root.subsections

        self.assertRaises(DataFormatReadOnlyExceptionError, SectionCollection.append, root_subs, Section('asdf'))
        self.assertRaises(DataFormatReadOnlyExceptionError, SectionCollection.__setattr__, root_subs, 'sections', [])
        self.assertRaises(DataFormatReadOnlyExceptionError, DataFormatList.append, root_subs.sections, Section('adsf'))
        self.assertRaises(DataFormatReadOnlyExceptionError, DataFormatList.pop, root_subs.sections, Section('adsf'))
