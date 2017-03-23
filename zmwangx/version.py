#!/usr/bin/env python3

"""Version of the package.

The version string is stored in __version__.

"""

from contextlib import contextmanager
import os
import subprocess

@contextmanager
def chdir(newdir):
    saved_dir = os.getcwd()
    try:
        os.chdir(newdir)
        yield newdir
    finally:
        os.chdir(saved_dir)

BASE_VERSION = 0.2
with chdir(os.path.dirname(os.path.realpath(__file__))):
    try:
        git_describe_version = subprocess.check_output(["git", "describe"]).strip().decode("utf-8")
        __version__ = git_describe_version.replace("-", ".", 1).replace("-", "+")
    except subprocess.CalledProcessError:
        __version__ = BASE_VERSION

if __name__ == "__main__":
    print(__version__)
