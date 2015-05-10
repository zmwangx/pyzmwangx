#!/usr/bin/env python3

"""A collection of shared utilities for day-to-day scripting."""

import setuptools
import sys

PY_MAJOR_VERSION = sys.version_info[0]
PY_MINOR_VERSION = sys.version_info[1]
if PY_MAJOR_VERSION < 3 or PY_MAJOR_VERSION == 3 and PY_MINOR_VERSION < 3:
    raise Exception("python %d.%d detected; minimum version 3.3 required" %
                    (PY_MAJOR_VERSION, PY_MINOR_VERSION))

setuptools.setup(
    name='zmwangx',
    version='0.1',
    description='A collection of shared utilities for day-to-day scripting',
    long_description='',
    url='https://github.com/zmwangx/py-zmwangx',
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
    ],
    keywords='utilities',
    packages=['zmwangx'],
    install_requires=[
        'beautifulsoup4',
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
            'urlgrep=zmwangx.urlgrep:main',
        ]
    },
    test_suite='tests',
)
