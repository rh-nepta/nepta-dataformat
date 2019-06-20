import shutil
import os
import operator

from nepta.dataformat import DataPackage, FileFlags
from nepta.dataformat.section import Section, SectionCollection
from nepta.dataformat.xml_file import XMLFile, MetaXMLFile
from nepta.dataformat.exceptions import DataFormatFileNotFound, DataFormatReadOnlyException, DataFormatFileExists, \
    DataFormatNullFile
from unittest import TestCase


class XMLFileTest(TestCase):
    EXAMPLE_DIR = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'examples'
    )
    TEST_DIR = 'tmp'
    NEW = os.path.join(TEST_DIR, 's1.xml')
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
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.TEST_DIR)

    def test_open(self):
        xml = XMLFile.open(self.EXIST)
        self.assertIsInstance(xml, XMLFile)
        self.assertIsInstance(xml.root, Section)
        self.assertIsInstance(xml.root.subsections, SectionCollection)

        self.assertEqual(xml.root.name, 'breakfast_menu')
        self.assertEqual(len(xml.root.subsections), 5)

        for sec in xml.root.subsections:
            self.assertEqual(sec.name, 'food')

        for sec in xml.root:
            self.assertEqual(sec.name, 'food')

    def test_open_n_write(self):
        sec_name = 'random_name'
        xml = XMLFile.open(self.EXIST)
        self.assertEqual(xml.root.name, 'breakfast_menu')
        self.assertEqual(len(xml.root.subsections), 5)
        xml.root.subsections.append(Section(sec_name, value='wwertret', value2='asdf2ew'))
        self.assertEqual(len(xml.root.subsections), 6)
        xml.save()

        xml2 = XMLFile.open(self.EXIST)
        sec_list = xml2.root.subsections.filter(sec_name)
        self.assertEqual(len(sec_list), 1)

    def test_create(self):
        xml = XMLFile.create(self.NEW)
        self.assertIsInstance(xml, XMLFile)
        self.assertIsInstance(xml.root, Section)
        self.assertIsInstance(xml.root.subsections, SectionCollection)
        self.assertEqual(len(xml.root.subsections), 0)

        data_sec = Section('data', sum="123", weather='sunny')
        xml.root.subsections.append(data_sec)

        data_sec.subsections.append(Section('avg_temp', number="15.5"))
        data_sec.subsections.append(Section('max_temp', number="15.9"))
        data_sec.subsections.append(Section('min_temp', number="15.2"))
        data_sec.subsections.append(Section('test_temp', number="15.x"))
        data_sec.subsections.append(Section('test_temp', number="15.x"))
        data_sec.subsections.append(Section('test_temp', number="15.x"))
        temps_sec = Section('temps')
        data_sec.subsections.append(temps_sec)
        for i in range(20):
            temps_sec.subsections.append(Section('temp', value=i))

        xml.save()
        self.assertTrue(os.path.exists(self.NEW))

        xml_ver = XMLFile.open(self.NEW)

        data_sec = xml_ver.root.subsections.filter('data')[0]
        self.assertEqual(data_sec.params['sum'], '123')
        self.assertEqual(data_sec.params['weather'], 'sunny')

        data_sec = xml_ver.root['data'][0]
        self.assertEqual(data_sec.params['sum'], '123')
        self.assertEqual(data_sec.params['weather'], 'sunny')

        for i, sec in enumerate(data_sec['temps'][0]):
            self.assertEqual(sec.name, 'temp')
            self.assertEqual(sec.params['value'], str(i))

        self.assertEqual(len(xml_ver.root['data'][0]['temps'][0].subsections), 20)
        data_sec['temps'][0].delete_subsections()
        self.assertEqual(len(xml_ver.root['data'][0]['temps'][0].subsections), 0)
        xml_ver.save()

        xml_ver2 = XMLFile.open(self.NEW)
        self.assertEqual(len(xml_ver2.root['data'][0]['temps'][0].subsections), 0)

        data_sec = xml_ver2.root['data'][0]
        self.assertEqual(len(data_sec.subsections.filter(number="15.9")), 1)
        self.assertEqual(data_sec.subsections.filter(number="15.9")[0].name, "max_temp")

        self.assertEqual(len(data_sec.subsections.filter(number="15.x")), 3)
        self.assertEqual(data_sec.subsections.filter(number="15.x")[0].name, "test_temp")

    def test_exceptions(self):
        self.assertRaises(DataFormatFileNotFound, XMLFile.open, 'asdfasdf')
        self.assertRaises(DataFormatFileExists, XMLFile.create, self.EXIST)

    def test_readonly(self):
        ro_xml = XMLFile.open(self.EXIST, readonly=True)

        self.assertRaises(DataFormatReadOnlyException, setattr, ro_xml, 'root', Section('ASDF'))
        self.assertRaises(DataFormatReadOnlyException, XMLFile.save, ro_xml)


class MetaXMLFileTest(TestCase):
    EXAMPLE_DIR = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'examples'
    )
    TEST_DIR = 'tmp'
    NEW = os.path.join(TEST_DIR, 'meta1.xml')
    EXIST = os.path.join(TEST_DIR, 'meta2.xml')

    @classmethod
    def setUpClass(cls):
        os.mkdir(cls.TEST_DIR)

    @classmethod
    def setUp(cls):
        shutil.copy(
            os.path.join(cls.EXAMPLE_DIR, 'meta.xml'),
            cls.EXIST
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_DIR)

    def test_create_new(self):
        test1 = "wertyuiohgfdsfgblaekduf87"
        test2 = '3524sa1fd653441rf63435t'
        self.assertFalse(os.path.exists(self.NEW))
        m1 = MetaXMLFile.create(self.NEW)
        self.assertIsInstance(m1, MetaXMLFile)
        m1['test1'] = test1
        m1['test2'] = test2
        m1.save()
        self.assertTrue(os.path.exists(self.NEW))

        m2 = MetaXMLFile.open(self.NEW)

        self.assertEqual(m2['test1'], test1)
        self.assertEqual(m2['test2'], test2)

        m2.save()

    def test_open_n_rewrite(self):
        area = "51 - UFO landing zone"
        m1 = MetaXMLFile.open(self.EXIST)
        self.assertIsInstance(m1, MetaXMLFile)

        self.assertEqual(m1['Family'], 'RHEL7')
        self.assertEqual(m1['Area'], 'net')
        self.assertEqual(m1['BeakerJobID'], '3483869')

        m1['Area'] = area
        m1.save()

        m2 = MetaXMLFile.open(self.EXIST)
        self.assertEqual(m1['Family'], 'RHEL7')
        self.assertEqual(m1['Area'], area)
        self.assertEqual(m1['BeakerJobID'], '3483869')
        self.assertIsInstance(m1['OtherHostNames'], list)
        m2.save()

    def test_open_with(self):
        area = "51 - UFO landing zone"
        with MetaXMLFile.open(self.EXIST) as m1:
            self.assertEqual(m1['Family'], 'RHEL7')
            self.assertEqual(m1['Area'], 'net')
            self.assertEqual(m1['BeakerJobID'], '3483869')
            m1['Area'] = area

        with MetaXMLFile.open(self.EXIST) as m2:
            self.assertEqual(m2['Family'], 'RHEL7')
            self.assertEqual(m2['Area'], area)
            self.assertEqual(m2['BeakerJobID'], '3483869')

    def test_readonly(self):
        with MetaXMLFile.open(self.EXIST, readonly=True) as m1:
            self.assertRaises(DataFormatReadOnlyException, MetaXMLFile.save, m1)
            self.assertRaises(DataFormatReadOnlyException, MetaXMLFile.__setitem__, m1, 'asdf', 'asdf')


class NullFileTest(TestCase):

    def test_raise(self):
        p = DataPackage.open('asdf', FileFlags.NONE)

        # meta
        self.assertRaises(DataFormatNullFile, operator.getitem, p.metas, 'Family')
        self.assertRaises(DataFormatNullFile, operator.setitem, p.metas, 'Version', '0.2')

        # store
        self.assertRaises(DataFormatNullFile, setattr, p.store, 'root', Section('asdf'))
        self.assertRaises(DataFormatNullFile, getattr, p.store, 'path')

        # attch
        self.assertRaises(DataFormatNullFile, len, p.attachments)
        self.assertRaises(DataFormatNullFile, iter, p.attachments)
