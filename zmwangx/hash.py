#!/usr/bin/env python3

import hashlib
import io
import logging
import os

import zmwangx.pbar

DEFAULT_CHUNK_SIZE = 65536

def chunks(fileobj, chunk_size=DEFAULT_CHUNK_SIZE):
    """Read file in chunks.

    Parameters
    ----------
    fileobj : file-like object
    chunk_size : int, optional
        Default is ``DEFAULT_CHUNK_SIZE`` bytes.

    Returns
    -------
    chunks : generator
        Generator for chunks of a file, each chunk being a ``bytes``
        object of length ``chunk_size``.

    """
    while True:
        chunk = fileobj.read(chunk_size)
        if not chunk:
            break
        if isinstance(chunk, str):
            chunk = chunk.encode("utf-8")
        yield chunk

def _fileobj_size(fileobj):
    """
    Try to determine the size of a file object.

    The size is determined by subtracting the current postion from the
    position of the end of file (i.e., the size we would be able to read
    if we starting reading from the current position).

    Returns
    -------
    size : int or None
        None is returned if the size cannot be determined (for instance,
        because the stream is not seekable).

    """
    try:
        if not fileobj.seekable():
            return None
        current_pos = fileobj.tell()
        fileobj.seek(0, io.SEEK_END)
        end_pos = fileobj.tell()
        fileobj.seek(current_pos)
        return end_pos - current_pos if end_pos >= current_pos else None
    except AttributeError:
        return None

def _fileobj_hash(fileobj, algorithm="sha1", chunk_size=DEFAULT_CHUNK_SIZE,
                  show_progress_bar=False, total_size=None):
    """Calculate the hash of a file object.

    See documentation of `file_hash` for details. The only difference is
    that the ``fileobj`` parameter can only be a file-like object.

    """
    if show_progress_bar and total_size is None:
        total_size = _fileobj_size(fileobj)
        if total_size is None:
            logging.warn("cannot determine the size of the file object; "
                         "progress bar not shown")
            show_progress_bar = False

    if show_progress_bar:
        pbar = zmwangx.pbar.ProgressBar(total_size)
    hashalg = hashlib.new(algorithm)
    for chunk in chunks(fileobj, chunk_size=chunk_size):
        hashalg.update(chunk)
        if show_progress_bar:
            pbar.update(chunk_size)
    if show_progress_bar:
        pbar.finish()

    return hashalg.hexdigest()

def file_hash(file, algorithm="sha1", chunk_size=DEFAULT_CHUNK_SIZE,
              show_progress_bar=False, total_size=None):
    r"""Calculate the hash of a file.

    The file object is read into memory in small chunks so as to not to
    consume too much memory.

    Parameters
    ----------
    file : str or file-like object
        Path to the file on disk, or an opened file-like
        object. File-like object should be opened in binary mode.
    algorithm : str, optional
        The hash algorithm to use; should be one of
        ``hashlib.algorithms_available``. Default is ``"sha1"``.
    chunk_size : int, optional
        Default is ``DEFAULT_CHUNK_SIZE``.
    show_progress_bar : bool, optional
        Whether to print progress bar. Default is ``False``.
    total_size : int, optional
        Total size in bytes, used for the progress bar. Only useful when
        ``show_progress_bar`` is ``True``, and ``file`` is a file-like
        object. Default is ``None``, in which case the program will try
        to infer the total size.

    Returns
    -------
    hexdigest : str
       The hexadecimal digest of the file.

    Raises
    ------
    ValueError
       If the algorithm is unrecognized.
    OSError
       If there is error reading the file or file-like object.

    Examples
    --------
    >>> import sys, tempfile
    >>> with tempfile.TemporaryFile() as fileobj:
    ...     content = "hello, world!\n"
    ...     written = fileobj.write(content.encode("utf-8"))
    ...     pos = fileobj.seek(0)
    ...     md5digest = file_hash(fileobj, "md5")
    ...     pos = fileobj.seek(0)
    ...     sha1digest = file_hash(fileobj)  # default algorithm
    ...     pos = fileobj.seek(0)
    ...     sha256digest = file_hash(fileobj, "sha256")
    ...     written = sys.stdout.write("content: %s" % content)
    ...     written = sys.stdout.write("MD5 digest: %s\n" % md5digest)
    ...     written = sys.stdout.write("SHA-1 digest: %s\n" % sha1digest)
    ...     written = sys.stdout.write("SHA-256 digest: %s\n" % sha256digest)
    content: hello, world!
    MD5 digest: 910c8bc73110b0cd1bc5d2bcae782511
    SHA-1 digest: e91ba0972b9055187fa2efa8b5c156f487a8293a
    SHA-256 digest: 4dca0fd5f424a31b03ab807cbae77eb32bf2d089eed1cee154b3afed458de0dc

    """
    if hasattr(file, "read"):
        return _fileobj_hash(file, algorithm, chunk_size,
                             show_progress_bar, total_size)
    else:
        total_size = os.path.getsize(file)
        with open(file, "rb") as fileobj:
            return _fileobj_hash(fileobj, algorithm, chunk_size,
                                 show_progress_bar, total_size)
