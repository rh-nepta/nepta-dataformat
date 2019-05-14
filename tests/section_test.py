import shutil
import os
from unittest import TestCase

from dataformat.section import Section, SectionCollection
from dataformat.xml_file import XMLFile
from dataformat.exceptions import DataFormatReadOnlyException
from dataformat.safe_types import DataFormatOrderedDict


class SectionTest(TestCase):
    EXAMPLE_DIR = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'examples'
    )
    TEST_DIR = 'tmp'
    EXIST = os.path.join(TEST_DIR, 's2.xml')

    @classmethod
    def setUpClass(cls):
        os.mkdir(cls.TEST_DIR)

    @classmethod
    def setUp(cls):
        shutil.copy(
            os.path.join(cls.EXAMPLE_DIR, 'menu.xml'),
            cls.EXIST
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_DIR)

    def test_readonly(self):
        xml1 = XMLFile.open(self.EXIST, readonly=True)
        root = xml1.root

        self.assertEqual(root.readonly, True)
        self.assertEqual(root.subsections.readonly, True)

        # test Section
        self.assertRaises(DataFormatReadOnlyException, Section.add_subsection, root, Section('asdf'))
        self.assertRaises(DataFormatReadOnlyException, Section.delete_subsections, root)
        self.assertRaises(DataFormatReadOnlyException, Section.__setattr__, root, 'name', 'asdf')
        self.assertRaises(DataFormatReadOnlyException, Section.__setattr__, root, 'params', dict())
        self.assertRaises(DataFormatReadOnlyException, DataFormatOrderedDict.__setitem__, root.params, 'key', 'value')
        self.assertRaises(DataFormatReadOnlyException, DataFormatOrderedDict.update, root.params, 'key', 'value')
        self.assertRaises(DataFormatReadOnlyException, DataFormatOrderedDict.pop, root.params, 'key')


class SectionCollectionTest(TestCase):
    EXAMPLE_DIR = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'examples'
    )
    TEST_DIR = 'tmp'
    EXIST = os.path.join(TEST_DIR, 's2.xml')

    @classmethod
    def setUpClass(cls):
        os.mkdir(cls.TEST_DIR)

    @classmethod
    def setUp(cls):
        shutil.copy(
            os.path.join(cls.EXAMPLE_DIR, 'menu.xml'),
            cls.EXIST
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_DIR)

    def test_readonly(self):
        xml1 = XMLFile.open(self.EXIST, readonly=True)
        root_subs = xml1.root.subsections

        self.assertRaises(DataFormatReadOnlyException, SectionCollection.append, root_subs, Section('asdf'))
        self.assertRaises(DataFormatReadOnlyException, SectionCollection.__setattr__, root_subs, 'sections', [])
        # TODO do we need DF_RO exception ?
        self.assertRaises(Exception, list.append, root_subs.sections, Section('adsf'))
