=========
pyzmwangx
=========

|Build Status|

This is a collection of small Python utilities used in my day-to-day scripts.

.. raw:: html

   API doc is <ins cite="https://readthedocs.org/builds/pyzmwangx/2732792/" datetime="2015-05-09T21:50:47-0700">not</ins> hosted on Read the Docs, since their Python 3.x environment is fake. If you want to read the API documentation, either dive into the source files, or roll your own build.

------------
Installation
------------

Requires Python 3.3 or later and ``setuptools``::

  python3 setup.py develop

This will install the ``zmwangx`` package.

-------
Modules
-------

* ``humansize``: convert size in bytes to human readable string (IEC or SI). Installs a console script ``humansize``.
* ``infrastructure``: testing infrastructure.
* ``urlgrep``: parse and match URLs from HTML documents. Installs a console script ``urlgrep``.

.. |Build Status| image:: https://travis-ci.org/zmwangx/pyzmwangx.svg?branch=master
   :target: https://travis-ci.org/zmwangx/pyzmwangx
