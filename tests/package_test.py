import shutil
import os
from unittest import TestCase

from dataformat.package import DataPackage
from dataformat.xml_file import XMLFile,MetaXMLFile


class BasicPackageTests(TestCase):
    EXAMPLE_DIR = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'examples'
    )
    TEST_DIR = 'tmp'
    CREATE_PATH = os.path.join(TEST_DIR, 'p1')
    OPEN_PATH = os.path.join(TEST_DIR, 'p2')

    @classmethod
    def setUpClass(cls):
        os.mkdir(cls.TEST_DIR)
        os.mkdir(cls.OPEN_PATH)
        shutil.copy(os.path.join(cls.EXAMPLE_DIR, 'meta.xml'),
                    os.path.join(cls.OPEN_PATH, 'meta.xml'))
        shutil.copy(os.path.join(cls.EXAMPLE_DIR, 'menu.xml'),
                    os.path.join(cls.OPEN_PATH, 'store.xml'))
        shutil.copy(os.path.join(cls.EXAMPLE_DIR, 'attch.xml'),
                    os.path.join(cls.OPEN_PATH, 'attachments.xml'))

    def test_create(self):
        p = DataPackage.create(self.CREATE_PATH)
        self.assertIsInstance(p, DataPackage)
        p.close()

    def test_open(self):
        # TODO test more than just class type
        p = DataPackage.open(self.OPEN_PATH)
        self.assertIsInstance(p, DataPackage)
        self.assertIsInstance(p.meta, MetaXMLFile)
        self.assertIsInstance(p.store, XMLFile)
        p.close()

    def test_open_with(self):
        with DataPackage.open(self.OPEN_PATH) as p:
            self.assertIsInstance(p, DataPackage)
            self.assertIsInstance(p.meta, MetaXMLFile)
            self.assertIsInstance(p.store, XMLFile)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_DIR)


