#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='enocean',
    version='0.60.1',
    description='EnOcean serial protocol implementation (fork of https://github.com/kipe/enocean.git)',
    author='Klaus Hessenberger',
    author_email='hesse315@gmail.com',
    url='https://github.com/hesse315/enocean',
    packages=[
        'enocean',
        'enocean.protocol',
        'enocean.communicators',
    ],
    scripts=[
        'examples/enocean_example.py',
    ],
    package_data={
        '': ['EEP.xml', 'Eltako.xml']
    },
    install_requires=[
        'enum-compat>=0.0.2',
        'pyserial>=3.0',
        'beautifulsoup4[lxml]>=4.3.2',
    ])
