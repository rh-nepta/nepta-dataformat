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
    CREATE_PATH2 = os.path.join(TEST_DIR, 'p3')
    OPEN_PATH = os.path.join(TEST_DIR, 'p2')

    @classmethod
    def setUpClass(cls):
        os.mkdir(cls.TEST_DIR)
        os.mkdir(cls.OPEN_PATH)
        os.mkdir(os.path.join(cls.OPEN_PATH, 'attachments'))
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

    def test_is_package(self):
        self.assertFalse(DataPackage.is_package('/etc/'))
        self.assertFalse(DataPackage.is_package(os.path.join(self.OPEN_PATH, 'attch.xml')))
        self.assertFalse(DataPackage.is_package(os.path.join(self.OPEN_PATH, 'store.xml')))
        self.assertFalse(DataPackage.is_package(os.path.join(self.OPEN_PATH, 'attachments')))

        self.assertTrue(DataPackage.is_package(self.OPEN_PATH))

        p2 = DataPackage.create(self.CREATE_PATH2)
        p2.close()
        self.assertTrue(DataPackage.is_package(self.CREATE_PATH2))
        self.assertFalse(DataPackage.is_package(os.path.join(self.CREATE_PATH2, os.pardir)))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_DIR)


