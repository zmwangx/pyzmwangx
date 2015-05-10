#!/usr/bin/env python3

"""Convert size in bytes to human readable format."""

import argparse
import math
import sys

def round_up(number, ndigits=0):
    """Round a nonnegative number upward to a given precision.

    Parameters
    ----------
    number : float
        The number to be rounded.
    ndigits : int, optional
        Number of decimal digits to round to. Default is 0.

    Returns
    -------
    float

    """
    multiplier = 10 ** ndigits
    return math.ceil(number * multiplier) / multiplier

_PREFIXES = {
    'iec-i': ['Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'],
    'iec': ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'],
    'si': ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'],
}
"""SI (metric) and IEC (binary) prefixes.

Starting from the first nontrivial ones (Ki or K).

"""

def humansize(size, prefix="iec-i", unit="B", space=False):
    """Convert size in number of bytes to human readable format.

    Always display at least three significant figures. Size is rounded
    *upward* whenever rounding is needed. Therefore, 1001 bytes, being
    1.001 kilobyte, is rounded to 1.01 KB.

    Although this function is usually used for size in bytes,
    technically it can be used for converting any number in any unit
    system to using the SI or IEC prefixes.

    Parameters
    ----------
    size : int
        Integer to be converted. Must be nonnegative.
    prefix : {"iec-i", "iec", "si"}, optional
        Prefix system to use. ``"iec-i"`` results in unit prefixes like
        ``"Ki"`` (2^10), ``"Mi"`` (2^20), ``"Gi"`` (2^30), etc.;
        ``"iec"`` results in prefixes like ``"K"`` (2^10), ``"M"``
        (2^20), ``"G"`` (2^30); ``"si"`` results in prefixes like
        ``"K"`` (10^3), ``"M"`` (10^6), ``"G"`` (10^9). Default is
        ``"iec-i"``.
    unit : str, optional
        Unit to attach to the prefix. Default is ``"B"`` for byte. You
        may use empty string to leave out the ``B``.
    space : bool, optional
        Whether to print a space between the number and the prefixed
        unit. Default is ``False``.

    Returns
    -------
    str

    Examples
    --------
    >>> humansize(314)
    '314B'
    >>> humansize(3141)
    '3.07KiB'
    >>> humansize(31415, prefix="iec")
    '30.7KB'
    >>> humansize(314159, prefix="si")
    '315KB'
    >>> humansize(3141592, unit="")
    '3.00Mi'
    >>> humansize(31415926, space=True)
    '30.0 MiB'

    """

    if size < 0:
        raise ValueError("size must be positive")
    if prefix not in {"iec-i", "iec", "si"}:
        raise ValueError("expected iec-i, iec, or si; %s received" % prefix)

    connection = " " if space else ""
    multiplier = 1000 if prefix == "si" else 1024
    if size < multiplier:
        return "%d%s%s" % (size, connection, unit)

    unitprefix = ""  # suppress undefined-loop-variable
    for unitprefix in _PREFIXES[prefix]:
        size /= multiplier
        if size < multiplier:
            fullunit = "%s%s%s" % (connection, unitprefix, unit)
            # ensure at least three significant figures
            if size < 10:
                return "%.2f%s" % (round_up(size, 2), fullunit)
            elif size < 100:
                return "%.1f%s" % (round_up(size, 1), fullunit)
            else:
                return "%.0f%s" % (round_up(size, 0), fullunit)
    # use the largest unit
    return "%.1f%s%s%s" % (round_up(size, 1), connection, unitprefix, unit)

def main():
    """CLI interface."""
    description = "Convert size in number of bytes to human readable format."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-p", "--prefix",
                        choices=["iec-i", "iec", "si"],
                        default="iec-i",
                        help="""iec-i, iec, or si; default is iec-i""")
    parser.add_argument("-u", "--unit", default="B",
                        help="""Unit to attach to the prefix; default is
                        B. Pass an empty string to suppress unit.""")
    parser.add_argument("-s", "--space", action="store_true",
                        help="""Insert space between the number and the
                        prefix.""")
    parser.add_argument("sizes", type=int, nargs="*", metavar="SIZE",
                        help="""size in bytes""")
    args = parser.parse_args()

    prefix = args.prefix
    unit = args.unit
    space = args.space
    if args.sizes:
        sizes = args.sizes
    else:
        sizes = [int(line.strip()) for line in sys.stdin]

    for size in sizes:
        print(humansize(size, prefix, unit, space))
