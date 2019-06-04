import shutil
import os
from unittest import TestCase

from dataformat.package import DataPackage
from dataformat.xml_file import XMLFile, MetaXMLFile
from dataformat.section import Section
from dataformat.attachments import AttachmentCollection as AttCol


class BasicPackageTests(TestCase):
    EXAMPLE_DIR = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'examples'
    )
    TEST_DIR = 'tmp'
    CREATE_PATH = os.path.join(TEST_DIR, 'p1')
    CREATE_PATH2 = os.path.join(TEST_DIR, 'p3')
    OPEN_PATH = os.path.join(TEST_DIR, 'p2')

    def setUp(self):
        os.mkdir(self.TEST_DIR)
        os.mkdir(self.OPEN_PATH)
        shutil.copytree(os.path.join(self.EXAMPLE_DIR, 'attachments'),
                        os.path.join(self.OPEN_PATH, 'attachments'))
        shutil.copy(os.path.join(self.EXAMPLE_DIR, 'meta.xml'),
                    os.path.join(self.OPEN_PATH, 'meta.xml'))
        shutil.copy(os.path.join(self.EXAMPLE_DIR, 'menu.xml'),
                    os.path.join(self.OPEN_PATH, 'store.xml'))
        shutil.copy(os.path.join(self.EXAMPLE_DIR, 'attch.xml'),
                    os.path.join(self.OPEN_PATH, 'attachments.xml'))

    def tearDown(self):
        shutil.rmtree(self.TEST_DIR)

    def test_create(self):
        p = DataPackage.create(self.CREATE_PATH)
        self.assertIsInstance(p, DataPackage)
        p.close()
        self.assertTrue(DataPackage.is_package(self.CREATE_PATH))

    def test_open(self):
        p = DataPackage.open(self.OPEN_PATH)
        self.assertIsInstance(p, DataPackage)
        self.assertIsInstance(p.meta, MetaXMLFile)
        self.assertIsInstance(p.store, XMLFile)

        self.assertEqual(p.meta['Family'], 'RHEL7')
        self.assertEqual(p.meta['SpecificTag'], 'Testing jobcreator')

        root = p.store.root
        self.assertEqual(root.name, 'breakfast_menu')
        food1 = root.subsections[0]
        self.assertEqual(len(food1.subsections.filter('name')), 1)
        self.assertEqual(len(food1.subsections.filter('price')), 1)
        self.assertEqual(len(food1.subsections.filter('calories')), 1)
        self.assertEqual(len(food1.subsections.filter('description')), 1)

        p.meta['Family'] = 'CentOS7'
        p.meta['SpecificTag'] = '#TAG'

        new_food = Section('food', hashtag='#tag')
        new_food.subsections.append(Section('name', value='Junky food'))
        new_food.subsections.append(Section('price', value='$5.50'))
        new_food.subsections.append(Section('description', value='asdf;lkjasdf;lkj'))
        new_food.subsections.append(Section('calories', value='500'))
        num_of_foods = len(p.store.root.subsections)
        p.store.root.subsections.append(new_food)

        num_of_attach = len(p.attch)
        attch1 = p.attch.new(AttCol.Types.FILE, 'cat ~/.bashrc')
        with open(os.path.join(self.OPEN_PATH, attch1.path), 'w') as f:
            f.write('asdfasdf')
        attch2 = p.attch.new(AttCol.Types.DIRECTORY, '/var/log/')

        p.close()
        del p

        # tests after write

        p1 = DataPackage.open(self.OPEN_PATH)
        self.assertIsInstance(p1, DataPackage)
        self.assertIsInstance(p1.meta, MetaXMLFile)
        self.assertIsInstance(p1.store, XMLFile)

        self.assertEqual(p1.meta['Family'], 'CentOS7')
        self.assertEqual(p1.meta['SpecificTag'], '#TAG')

        root = p1.store.root
        self.assertEqual(len(root.subsections), num_of_foods + 1)
        self.assertEqual(root.name, 'breakfast_menu')
        food1 = root.subsections[0]
        self.assertEqual(len(food1.subsections.filter('name')), 1)
        self.assertEqual(len(food1.subsections.filter('price')), 1)
        self.assertEqual(len(food1.subsections.filter('calories')), 1)
        self.assertEqual(len(food1.subsections.filter('description')), 1)

        my_food = p1.store.root.subsections.filter('food', hashtag='#tag')
        self.assertEqual(len(my_food), 1)
        my_food = my_food[0]
        self.assertEqual(len(my_food.subsections.filter('name')), 1)
        self.assertEqual(my_food.subsections.filter('name')[0].params['value'], 'Junky food')
        self.assertEqual(len(my_food.subsections.filter('price')), 1)
        self.assertEqual(my_food.subsections.filter('price')[0].params['value'], '$5.50')
        self.assertEqual(len(my_food.subsections.filter('calories')), 1)
        self.assertEqual(my_food.subsections.filter('calories')[0].params['value'], '500')
        self.assertEqual(len(my_food.subsections.filter('description')), 1)
        self.assertEqual(my_food.subsections.filter('description')[0].params['value'], 'asdf;lkjasdf;lkj')

        self.assertEqual(num_of_attach + 2, len(p1.attch))
        for attch in p1.attch:
            self.assertTrue(os.path.exists(os.path.join(self.OPEN_PATH, attch.path)))

        p1.close()

    def test_open_with(self):
        with DataPackage.open(self.OPEN_PATH) as p:
            self.assertIsInstance(p, DataPackage)
            self.assertIsInstance(p.meta, MetaXMLFile)
            self.assertIsInstance(p.store, XMLFile)

            self.assertEqual(p.meta['Family'], 'RHEL7')
            self.assertEqual(p.meta['SpecificTag'], 'Testing jobcreator')

            root = p.store.root
            self.assertEqual(root.name, 'breakfast_menu')
            food1 = root.subsections[0]
            self.assertEqual(len(food1.subsections.filter('name')), 1)
            self.assertEqual(len(food1.subsections.filter('price')), 1)
            self.assertEqual(len(food1.subsections.filter('calories')), 1)
            self.assertEqual(len(food1.subsections.filter('description')), 1)

            p.meta['Family'] = 'CentOS7'
            p.meta['SpecificTag'] = '#TAG'

            new_food = Section('food', hashtag='#tag')
            new_food.subsections.append(Section('name', value='Junky food'))
            new_food.subsections.append(Section('price', value='$5.50'))
            new_food.subsections.append(Section('description', value='asdf;lkjasdf;lkj'))
            new_food.subsections.append(Section('calories', value='500'))
            num_of_foods = len(p.store.root.subsections)
            p.store.root.subsections.append(new_food)

            num_of_attach = len(p.attch)
            attch1 = p.attch.new(AttCol.Types.FILE, 'cat ~/.bashrc')
            with open(os.path.join(self.OPEN_PATH, attch1.path), 'w') as f:
                f.write('asdfasdf')
            attch2 = p.attch.new(AttCol.Types.DIRECTORY, '/var/log/')

        del p

        with DataPackage.open(self.OPEN_PATH) as p1:
            self.assertIsInstance(p1, DataPackage)
            self.assertIsInstance(p1.meta, MetaXMLFile)
            self.assertIsInstance(p1.store, XMLFile)

            self.assertEqual(p1.meta['Family'], 'CentOS7')
            self.assertEqual(p1.meta['SpecificTag'], '#TAG')

            root = p1.store.root
            self.assertEqual(len(root.subsections), num_of_foods + 1)
            self.assertEqual(root.name, 'breakfast_menu')
            food1 = root.subsections[0]
            self.assertEqual(len(food1.subsections.filter('name')), 1)
            self.assertEqual(len(food1.subsections.filter('price')), 1)
            self.assertEqual(len(food1.subsections.filter('calories')), 1)
            self.assertEqual(len(food1.subsections.filter('description')), 1)

            my_food = p1.store.root.subsections.filter('food', hashtag='#tag')
            self.assertEqual(len(my_food), 1)
            my_food = my_food[0]
            self.assertEqual(len(my_food.subsections.filter('name')), 1)
            self.assertEqual(my_food.subsections.filter('name')[0].params['value'], 'Junky food')
            self.assertEqual(len(my_food.subsections.filter('price')), 1)
            self.assertEqual(my_food.subsections.filter('price')[0].params['value'], '$5.50')
            self.assertEqual(len(my_food.subsections.filter('calories')), 1)
            self.assertEqual(my_food.subsections.filter('calories')[0].params['value'], '500')
            self.assertEqual(len(my_food.subsections.filter('description')), 1)
            self.assertEqual(my_food.subsections.filter('description')[0].params['value'], 'asdf;lkjasdf;lkj')

            self.assertEqual(num_of_attach + 2, len(p1.attch))
            for attch in p1.attch:
                self.assertTrue(os.path.exists(os.path.join(self.OPEN_PATH, attch.path)))

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



