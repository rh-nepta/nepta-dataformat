import shutil
import os
from unittest import TestCase

from dataformat.package import DataPackage
from dataformat.xml_file import XMLFile
from .xml_file_test import XMLFileTest, MetaXMLFileTest


class BasicPackageTests(TestCase):
    CREATE_PATH = '/tmp/tests/p1'
    OPEN_PATH = '/tmp/tests/p2'

    @classmethod
    def setUpClass(cls):
        os.mkdir(cls.OPEN_PATH)
        with open(os.path.join(cls.OPEN_PATH, 'meta.xml'), 'w') as f:
            f.write(MetaXMLFileTest.EXAMPLE)
        with open(os.path.join(cls.OPEN_PATH, 'store.xml'), 'w') as f:
            f.write(XMLFileTest.EXAMPLE)

    def test_create(self):
        p = DataPackage.create(self.CREATE_PATH)
        self.assertIsInstance(p, DataPackage)
        p.close()

    def test_open(self):
        p = DataPackage.open(self.OPEN_PATH)
        self.assertIsInstance(p, DataPackage)
        self.assertIsInstance(p.meta, XMLFile)
        self.assertIsInstance(p.store, XMLFile)
        p.close()

    def test_open_with(self):
        with DataPackage.open(self.OPEN_PATH) as p:
            self.assertIsInstance(p, DataPackage)
            self.assertIsInstance(p.meta, XMLFile)
            self.assertIsInstance(p.store, XMLFile)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.CREATE_PATH):
            shutil.rmtree(cls.CREATE_PATH)
        if os.path.exists(cls.OPEN_PATH):
            shutil.rmtree(cls.OPEN_PATH)


