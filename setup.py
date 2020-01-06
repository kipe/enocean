#!/usr/bin/env python3
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='enocean_async',
    version='1.0.0',
    description='EnOcean serial protocol async implementation',
    author='Angelo Cutaia',
    author_email='angeloxx92@hotmail.it',
    url='https://github.com/Angeloxx92/enocean_async',
    packages=[
        'enocean_async',
        'enocean_async.protocol',
        'enocean_async.communicators',
    ],
    scripts=[
        'examples/enocean_example.py',
    ],
    package_data={
        '': ['EEP.xml']
    },
    install_requires=[
        'enum-compat>=0.0.2',
        'pyserial-async>=0.4',
        'beautifulsoup4>=4.3.2',
        'aioconsole>0.1.15',
    ])
