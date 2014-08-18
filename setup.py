#!/usr/bin/env python
from distutils.core import setup

setup(
    name='enocean',
    version='0.15',
    description='EnOcean serial protocol implementation',
    author='Kimmo Huoman',
    author_email='kipenroskaposti@gmail.com',
    url='https://github.com/kipe/enocean',
    packages=[
        'enocean',
        'enocean.protocol',
        'enocean.communicators',
    ],
    scripts=[
        'examples/enocean_example.py',
    ],
    package_data={
        '': ['EEP_2.6.1.xml']
    },
    install_requires=[
        'enum34>=1.0',
        'pyserial>=2.7',
        'beautifulsoup4>=4.3.2',
    ])
