#!/usr/bin/env python3

"""Version of the package.

The version string is stored in __version__.

"""

import subprocess

BASE_VERSION = 0.1
try:
    git_describe_version = subprocess.check_output(["git", "describe"]).strip().decode("utf-8")
    __version__ = git_describe_version.replace("-", ".", 1)
except subprocess.CalledProcessError:
    __version__ = BASE_VERSION

if __name__ == "__main__":
    print(__version__)
