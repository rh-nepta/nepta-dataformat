#!/usr/bin/env python3

from setuptools import setup
import versioneer

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name='nepta-dataformat',
    version=versioneer.get_version(),
    description='Lib providing data scheme of nepta test result.',
    long_description=readme,
    author='Adrian Tomasov',
    author_email='atomasov@redhat.com',
    url='https://github.com/rh-nepta/nepta-dataformat',
    packages = ['dataformat'],
    install_requires = ['dataclasses==0.6'],
)
