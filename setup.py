#!/usr/bin/env python3

"""A collection of shared utilities for day-to-day scripting."""

import os
import setuptools
import sys

PY_MAJOR_VERSION = sys.version_info[0]
PY_MINOR_VERSION = sys.version_info[1]
if PY_MAJOR_VERSION < 3 or PY_MAJOR_VERSION == 3 and PY_MINOR_VERSION < 3:
    raise Exception("python %d.%d detected; minimum version 3.3 required" %
                    (PY_MAJOR_VERSION, PY_MINOR_VERSION))

here = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# read version from version.py and save in __version__
with open(os.path.join(here, 'zmwangx', 'version.py')) as f:
    exec(f.read())

setuptools.setup(
    name='zmwangx',
    version=__version__,
    description='A collection of shared utilities for day-to-day scripting',
    long_description=long_description,
    url='https://github.com/zmwangx/pyzmwangx',
    author='Zhiming Wang',
    author_email='zmwangx@gmail.com',
    license='Public Domain',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='utilities',
    packages=['zmwangx'],
    install_requires=[
        'PyYAML',
        'beautifulsoup4>=4.4.0',
        'requests',
    ],
    extras_require={
        'test': [
            'coverage',
            'nose',
        ],
    },
    entry_points={
        'console_scripts': [
            'humansize=zmwangx.humansize:main',
            'humantime=zmwangx.humantime:main',
            'urlgrep=zmwangx.urlgrep:main',
        ]
    },
    test_suite='tests',
)
