#!/usr/bin/env python3

"""
Easy logging setup.

This module only provides a one-stop setup. To actually log entries, use
the standard logging.info, logging.debug, etc.

"""

import logging
import os

_LOGGING_LEVEL_MAP = {
    "debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING,
    "error": logging.ERROR, "critical": logging.CRITICAL,
}

def logging_setup(name, destination="data", level="info", console_level="warning",
                  entryfmt="%(asctime)s %(levelname)s %(message)s",
                  datefmt="%Y-%m-%dT%H:%M:%S%z",
                  console_entryfmt="%(levelname)-8s %(message)s"):
    """
    Set up logging to both console and file.

    The log file is located in ``$XDG_DATA_HOME`` or ``$XDG_CACHE_HOME``
    (``~/.local/share`` or ``~/.cache`` if the corresponding environment
    variables are not set), based on your choice of ``destination``. For
    instance, if your program has ``name`` ``foo``, and you choose to
    log to ``data``, then the log file location is most likely
    ``~/.local/share/foo/foo.log``.

    Logging levels and formats are customizable for both console and
    file logging. However, sane defaults have been chosen so you usually
    don't need to specify anything other than the program name and
    optionally the destination (as a simple English word).

    Parameters
    ----------
    name : str
        The file to log to will be ``<name>/<name>.log`` within the
        destination directory (see ``destination``).
    destination : {"data", "cache"}
        If destination is ``"data"``, log to a file in
        ``$XDG_DATA_HOME`` (or ``~/.local/share``); if destination is
        ``cache``, log to a file in ``$XDG_CACHE_HOME`` or
        ``~/.cache``. Default is ``data``.
    level : {"info", "debug", "warning", "error", "critical"}
        Logging level to log file. Default is ``"info"``.
    console_level : {"info", "debug", "warning", "error", "critical", None}
        Logging level to console. Default is ``"warning"``. Set to
        ``None`` to turn off logging to console.
    entryfmt : str
        Log entry format, passed to the ``format`` argument of
        ``logging.basicConfig``. Default is
        ``"%(asctime)s %(levelname)s %(message)s"``.
    datefmt : str
        Date format, passed to the ``datefmt`` argument of
        ``logging.basicConfig``. Default is ``"%Y-%m-%dT%H:%M:%S%z"``.
    console_entryfmt : str
        Console log entry format. Default is
        ``"%(levelname)-8s %(message)s"``.

    """
    if destination == "data":
        rootdir_envvar = "XDG_DATA_HOME"
        rootdir_fallback = "~/.local/share"
    elif destination == "cache":
        rootdir_envvar = "XDG_CACHE_HOME"
        rootdir_fallback = "~/.cache"
    else:
        raise ValueError("cannot understand destination '%s';"
                         "should be 'data' or 'cache'" % destination)

    if rootdir_envvar in os.environ:
        rootdir = os.path.join(os.environ[rootdir_envvar])
    else:
        rootdir = os.path.expanduser(rootdir_fallback)
    logdir = os.path.join(rootdir, name)
    os.makedirs(logdir, mode=0o700, exist_ok=True)
    logfile = os.path.join(logdir, "%s.log" % name)

    level = _LOGGING_LEVEL_MAP[level]

    logging.basicConfig(
        filename=logfile,
        level=level,
        format=entryfmt,
        datefmt=datefmt,
    )

    # also set up logging to console
    if console_level is None:
        return

    console = logging.StreamHandler()
    console_level = _LOGGING_LEVEL_MAP[console_level]
    console.setLevel(console_level)
    console.setFormatter(logging.Formatter(console_entryfmt))
    logging.getLogger("").addHandler(console)
