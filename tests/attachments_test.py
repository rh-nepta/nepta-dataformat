from unittest  import TestCase
import os
import shutil

from dataformat.attachments import AttachmentCollection


class AttachmentCollectionTest(TestCase):
    EXAMPLE_DIR = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'examples'
    )
    TEST_DIR = 'tmp'
    NEW = os.path.join(TEST_DIR, 'ac1')
    EXIST = os.path.join(TEST_DIR, 'ac2')

    @classmethod
    def setUpClass(cls):
        os.mkdir(cls.TEST_DIR)

    @classmethod
    def setUp(cls):
        os.mkdir(cls.EXIST)
        shutil.copy(
            os.path.join(cls.EXAMPLE_DIR, 'attch.xml'),
            os.path.join(cls.EXIST, 'attachments.xml')
        )
        shutil.copytree(
            os.path.join(cls.EXAMPLE_DIR, 'attachments'),
            os.path.join(cls.EXIST, 'attachments')
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_DIR)

    def test_open(self):
        ac = AttachmentCollection.open(self.EXIST)
        print("asdf")
        

