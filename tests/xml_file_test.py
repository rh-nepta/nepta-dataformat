import shutil
import os

from dataformat.package import DataPackage
from dataformat.section import Section, SectionCollection
from dataformat.xml_file import XMLFile, MetaXMLFile
from dataformat.exceptions import DataFormatFileNotFound
from unittest import TestCase


class XMLFileTest(TestCase):
    NEW = '/tmp/tests/xml1.xml'
    EXIST = '/tmp/tests/xml2.xml'
    EXAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<breakfast_menu>
  <food>
    <name>Belgian Waffles</name>
    <price>$5.95</price>
    <description>Two of our famous Belgian Waffles with plenty of real maple syrup</description>
    <calories>650</calories>
  </food>
  <food>
    <name>Strawberry Belgian Waffles</name>
    <price>$7.95</price>
    <description>Light Belgian waffles covered with strawberries and whipped cream</description>
    <calories>900</calories>
  </food>
  <food>
    <name>Berry-Berry Belgian Waffles</name>
    <price>$8.95</price>
    <description>Light Belgian waffles covered with an assortment of fresh berries and whipped cream</description>
    <calories>900</calories>
  </food>
  <food>
    <name>French Toast</name>
    <price>$4.50</price>
    <description>Thick slices made from our homemade sourdough bread</description>
    <calories>600</calories>
  </food>
  <food>
    <name>Homestyle Breakfast</name>
    <price>$6.95</price>
    <description>Two eggs, bacon or sausage, toast, and our ever-popular hash browns</description>
    <calories>950</calories>
  </food>
</breakfast_menu>
"""
    @classmethod
    def setUp(cls):
        with open(cls.EXIST, 'w') as f:
            f.write(cls.EXAMPLE)

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists(cls.EXIST):
            os.remove(cls.EXIST)

        if os.path.exists(cls.NEW):
            os.remove(cls.NEW)

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

    def test_create(self):
        xml = XMLFile.create(self.NEW)
        self.assertIsInstance(xml, XMLFile)
        self.assertIsInstance(xml.root, Section)
        self.assertIsInstance(xml.root.subsections, SectionCollection)
        self.assertEqual(len(xml.root.subsections), 0)

        data_sec = Section('data', sum="123", weather='sunny')
        xml.root.add_subsection(data_sec)

        data_sec.add_subsection(Section('avg_temp', number="15.5"))
        data_sec.add_subsection(Section('max_temp', number="15.9"))
        data_sec.add_subsection(Section('min_temp', number="15.2"))
        data_sec.add_subsection(Section('test_temp', number="15.x"))
        data_sec.add_subsection(Section('test_temp', number="15.x"))
        data_sec.add_subsection(Section('test_temp', number="15.x"))
        temps_sec = Section('temps')
        data_sec.add_subsection(temps_sec)
        for i in range(20):
            temps_sec.add_subsection(Section('temp', value=i))

        xml.save()
        self.assertTrue(os.path.exists(self.NEW))

        xml_ver = XMLFile.open(self.NEW)

        data_sec = xml_ver.root.get_subsections_by_name('data')[0]
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
        self.assertEqual(len(data_sec.get_subsections_by_param_val(number="15.9")), 1)
        self.assertEqual(data_sec.get_subsections_by_param_val(number="15.9")[0].name, "max_temp")

        self.assertEqual(len(data_sec.get_subsections_by_param_val(number="15.x")), 3)
        self.assertEqual(data_sec.get_subsections_by_param_val(number="15.x")[0].name, "test_temp")

    def test_exceptions(self):
        try:
            xml1 = XMLFile.open('asdfasdf')
        except DataFormatFileNotFound as d:
            pass
        else:
            raise AssertionError


class MetaXMLFileTest(TestCase):
    NEW = '/tmp/tests/meta1.xml'
    EXIST = '/tmp/tests/meta2.xml'
    EXAMPLE = """<?xml version="1.0" ?>
  <BeakerRunResult>
    <Settings>
      <DateTime value="2018-04-18 18:23:39"/>
      <UUID value="666f97a3-314b-4ffe-8331-9c2ac712d868"/>
      <Family value="RHEL7"/>
      <Workflow value="manual"/>
      <SpecificTag value="Testing jobcreator"/>
      <BeakerHUB value="https://abc.com"/>
      <TestCase value="Test"/>
      <Kernel value="kernel-3.10.0"/>
      <Area value="net"/>
      <BenchmarkName value="iperf3"/>
      <BenchmarkVersion value="3.5-1.el7eng.x86_64"/>
      <Arguments value="--prepare --execute --sync perfqe --submit --store --store-logs --configuration Standard --meta Family 'RHEL7' --meta Workflow 'manual' --meta SpecificTag 'Testing jobcreator' "/>
      <HostName value="struska1.com"/>
      <OtherHostNames type="list">
        <value value="struska1.com"/>
        <value value="struska2.com"/>
      </OtherHostNames>
      <SELinux value="Enforcing"/>
      <InRHTS value="True"/>
      <Distribution value="RHEL-7.2"/>
      <BeakerJobID value="3483869"/>
      <TunedProfile value="throughput-performance"/>
      <Architecture value="x86_64"/>
      <NetworkPerftestVersion value="14.1-24.noarch"/>
    </Settings>
  </BeakerRunResult>"""

    @classmethod
    def setUp(cls):
        with open(cls.EXIST, 'w') as f:
            f.write(cls.EXAMPLE)

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists(cls.EXIST):
            os.remove(cls.EXIST)

        if os.path.exists(cls.NEW):
            os.remove(cls.NEW)

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
