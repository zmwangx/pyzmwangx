=========
pyzmwangx
=========

|Build Status|

This is a collection of small Python utilities used in my day-to-day scripts.

API doc is hosted on `Read the Docs <https://pyzmwangx.readthedocs.org/>`_.

------------
Installation
------------

Requires Python 3.3 or later and ``setuptools``::

  python3 setup.py develop

This will install the ``zmwangx`` package.

-------
Modules
-------

* ``colorout``: colorize stdout and stderr.
* ``humansize``: convert size in bytes to human readable string (IEC or SI). Installs a console script ``humansize``.
* ``infrastructure``: testing infrastructure.
* ``urlgrep``: parse and match URLs from HTML documents. Installs a console script ``urlgrep``.

.. |Build Status| image:: https://travis-ci.org/zmwangx/pyzmwangx.svg?branch=master
   :target: https://travis-ci.org/zmwangx/pyzmwangx
