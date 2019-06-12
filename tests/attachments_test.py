import os
import shutil
from unittest import TestCase
from collections import defaultdict

from dataformat.attachments import AttachmentCollection
from dataformat.exceptions import DataFormatReadOnlyException, DataFormatDuplicateKey
from dataformat import AttachmentTypes


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
        os.mkdir(cls.NEW)

    def setUp(self):
        os.mkdir(self.EXIST)
        shutil.copy(
            os.path.join(self.EXAMPLE_DIR, 'attch.xml'),
            os.path.join(self.EXIST, 'attachments.xml')
        )
        shutil.copytree(
            os.path.join(self.EXAMPLE_DIR, 'attachments'),
            os.path.join(self.EXIST, 'attachments')
        )

    def tearDown(self):
        shutil.rmtree(self.EXIST)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_DIR)

    def test_open(self):
        ac = AttachmentCollection.open(self.EXIST)
        self.assertEqual(len(ac), 4)

        counter = defaultdict(int)
        for att in ac:
            counter[att.name] += 1

        self.assertEqual(counter['Command'], 3)
        self.assertEqual(counter['Directory'], 1)

    def test_create(self):
        ac = AttachmentCollection.create(self.NEW)

        self.assertTrue(os.path.exists(self.NEW))
        self.assertTrue(os.path.exists(os.path.join(self.NEW, 'attachments')))
        self.assertTrue(os.path.exists(os.path.join(self.NEW, 'attachments.xml')))

        att1 = ac.new(AttachmentTypes.FILE, '/etc/krb5.conf')
        with open(os.path.join(self.NEW, att1.path), 'w') as f:
            f.write('sadljfhsaldjfhsadlkjfh')
        att2 = ac.new(AttachmentTypes.DIRECTORY, '/etc/')

        self.assertTrue(os.path.exists(os.path.join(self.NEW, att1.path)))
        self.assertTrue(os.path.exists(os.path.join(self.NEW, att2.path)))
        self.assertNotEqual(att1.uuid, att2.uuid)

        ac.save()
        ac.save()

        ac_check = AttachmentCollection.open(self.NEW)
        self.assertEqual(len(ac), len(ac_check))

        for att in ac_check:
            self.assertTrue(os.path.exists(os.path.join(self.NEW, att.path)))

        self.assertEqual(ac_check.collection[0], att1)
        self.assertEqual(ac_check.collection[1], att2)

    def test_readonly(self):
        ac = AttachmentCollection.open(self.EXIST, readonly=True)
        self.assertRaises(
            DataFormatReadOnlyException, AttachmentCollection.new, ac, AttachmentTypes.DIRECTORY, '/')
        self.assertRaises(DataFormatReadOnlyException, AttachmentCollection.save, ac)
        self.assertRaises(DataFormatReadOnlyException, setattr, ac, 'path', 'asdf')

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

        self.assertRaises(DataFormatDuplicateKey, ac1.new, AttachmentTypes.FILE, 'asdf', 'net')

