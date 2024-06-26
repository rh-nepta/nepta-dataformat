import os
import shutil
from collections import defaultdict
from unittest import TestCase

from nepta.dataformat import AttachmentTypes, Compression
from nepta.dataformat.attachments import AttachmentCollection
from nepta.dataformat.exceptions import (
    DataFormatBadTypeError,
    DataFormatDuplicateKeyError,
    DataFormatReadOnlyExceptionError,
)


class AttachmentCollectionTest(TestCase):
    EXAMPLE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'examples')
    TEST_DIR = 'tmp'
    NEW = os.path.join(TEST_DIR, 'ac1')
    EXIST = os.path.join(TEST_DIR, 'ac2')

    @classmethod
    def setUpClass(cls):
        os.mkdir(cls.TEST_DIR)

    def setUp(self):
        os.mkdir(self.NEW)
        os.mkdir(self.EXIST)
        shutil.copy(os.path.join(self.EXAMPLE_DIR, 'attachments.xml'), os.path.join(self.EXIST, 'attachments.xml'))
        shutil.copytree(os.path.join(self.EXAMPLE_DIR, 'attachments'), os.path.join(self.EXIST, 'attachments'))

    def tearDown(self):
        shutil.rmtree(self.EXIST)
        shutil.rmtree(self.NEW)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_DIR)

    def test_open(self):
        ac = AttachmentCollection.open(self.EXIST)
        self.assertEqual(len(ac), 4)

        counter = defaultdict(int)
        for att in ac:
            counter[att.name] += 1

        print(counter)

        self.assertEqual(counter[AttachmentTypes.COMMAND], 3)
        self.assertEqual(counter[AttachmentTypes.DIRECTORY], 1)

    def test_create(self):
        ac = AttachmentCollection.create(self.NEW)

        self.assertTrue(os.path.exists(self.NEW))
        self.assertTrue(os.path.exists(os.path.join(self.NEW, 'attachments')))
        self.assertTrue(os.path.exists(os.path.join(self.NEW, 'attachments.xml')))

        att1 = ac.new(AttachmentTypes.FILE, '/etc/krb5.conf')
        att1.path.write('as;dlkfjas;dlfkj')
        att2 = ac.new(AttachmentTypes.DIRECTORY, '/etc/')
        os.makedirs(os.path.join(self.NEW, str(att2.path)))

        self.assertRaises(DataFormatBadTypeError, ac.new, 'asdf', 'adf')

        self.assertTrue(os.path.exists(os.path.join(self.NEW, str(att1.path))))
        self.assertTrue(os.path.exists(os.path.join(self.NEW, str(att2.path))))
        self.assertNotEqual(att1.uuid, att2.uuid)

        ac.save()
        ac.save()

        ac_check = AttachmentCollection.open(self.NEW)
        self.assertEqual(len(ac), len(ac_check))

        for att in ac_check:
            self.assertTrue(os.path.exists(os.path.join(self.NEW, str(att.path))))

        self.assertEqual(ac_check.collection[0], att1)
        self.assertEqual(ac_check.collection[1], att2)

    def test_readonly(self):
        ac = AttachmentCollection.open(self.EXIST, readonly=True)
        self.assertRaises(
            DataFormatReadOnlyExceptionError, AttachmentCollection.new, ac, AttachmentTypes.DIRECTORY, '/'
        )
        self.assertRaises(DataFormatReadOnlyExceptionError, AttachmentCollection.save, ac)
        self.assertRaises(DataFormatReadOnlyExceptionError, setattr, ac, 'path', 'asdf')

        for attch in ac:
            self.assertRaises(Exception, setattr, attch, 'name', 'asdf')

    def test_alias(self):
        ac = AttachmentCollection.open(self.EXIST)
        ac.new(AttachmentTypes.DIRECTORY, '/root/')
        att2 = ac.new(AttachmentTypes.DIRECTORY, '/etc/sysconfig', alias='net')
        att3 = ac.new(AttachmentTypes.DIRECTORY, '/etc/cert', 'cert')

        ac.save()

        del ac

        ac1 = AttachmentCollection.open(self.EXIST)

        self.assertEqual(att2, ac1['net'])
        self.assertEqual(att3, ac1['cert'])

        self.assertRaises(DataFormatDuplicateKeyError, ac1.new, AttachmentTypes.FILE, 'asdf', 'net')

    def test_compression(self):
        ac = AttachmentCollection.create(self.NEW)

        att1 = ac.new(AttachmentTypes.DIRECTORY, 'folder', compression=Compression.BZIP2)
        shutil.copytree(self.EXIST, att1.path.full_path)

        att2 = ac.new(AttachmentTypes.COMMAND, 'dmesg', compression=Compression.XZ)
        att2.path.write(os.popen('dmesg').read())

        ac.save()

        self.assertTrue(os.path.exists(att1.path.full_path + '.tar.bz2'))
        self.assertTrue(os.path.exists(att2.path.full_path + '.tar.xz'))
