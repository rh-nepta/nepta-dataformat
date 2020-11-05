from unittest import TestCase
import os
import shutil

from nepta.dataformat.remote_package import RemotePackageCollection


class RemotePackageTest(TestCase):
    PATH = 'df_pkg'

    def setUp(self) -> None:
        os.mkdir(self.PATH)

    def tearDown(self) -> None:
        if os.path.exists(self.PATH):
            shutil.rmtree(self.PATH)

    def test_create(self):
        hosts = ['obrabec2', 'vales1', 'vales2']
        pkg = RemotePackageCollection.create(self.PATH)
        self.assertTrue(os.path.exists(os.path.join(self.PATH, RemotePackageCollection.RMPKG_DIR)))

        for host in hosts:
            pkg.new(host)

        for host in hosts:
            self.assertTrue(os.path.exists(os.path.join(
                pkg.path, RemotePackageCollection.RMPKG_DIR, host)))

        self.assertTrue(os.path.exists(os.path.join(pkg.path, pkg.RMPKG_DIR)))
        pkg.save()
        self.assertFalse(os.path.exists(os.path.join(pkg.path, pkg.RMPKG_DIR)),
                         'Saved packages should contain only archived remote packages.')

    def test_open(self):
        hosts = ['obrabec2', 'vales1', 'vales2']
        pkg = RemotePackageCollection.create(self.PATH)
        for host in hosts:
            pkg.new(host)

        pkg.save()
        for rem_pkg in pkg:
            self.assertFalse(os.path.exists(os.path.join(pkg.path, rem_pkg.path)),
                             'Remote packages are not archived correctly')

        pkg2 = RemotePackageCollection.open(self.PATH)
        self.assertEqual(len(hosts), len(pkg2))
        for rem_pkg in pkg2:
            self.assertIn(rem_pkg.host, hosts, 'Remote package meta: host is missing')
            self.assertTrue(os.path.exists(os.path.join(pkg2.path, rem_pkg.path)),
                            'Remote packages are not extracted correctly')
