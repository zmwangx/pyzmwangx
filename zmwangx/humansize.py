#!/usr/bin/env python3

"""Convert size in bytes to human readable format."""

import argparse
from decimal import *
import math
import sys

def round_up(number, ndigits=0):
    """Round a nonnegative decimal upward to a given precision.

    Parameters
    ----------
    number : float or decimal.Decimal
        The decimal to be rounded.
    ndigits : int, optional
        Number of decimal digits to round to. Default is 0.

    Returns
    -------
    float or decimal.Decimal
        Depending on type of ``number``.

    """
    if not isinstance(number, Decimal):
        number = Decimal(number)
        input_type = float
    else:
        input_type = Decimal

    rounded = number.quantize(Decimal(10) ** (-ndigits), rounding=ROUND_UP)

    if input_type is Decimal:
        return rounded
    else:
        return float(rounded)

_PREFIXES = {
    'iec-i': ['Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'],
    'iec': ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'],
    'si': ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'],
}
"""SI (metric) and IEC (binary) prefixes.

Starting from the first nontrivial ones (Ki or K).

"""

def humansize(size, prefix="iec-i", unit="B", space=False, numfmt=False):
    """Convert size in number of bytes to human readable format.

    If ``numfmt`` is False (default), display at least three significant
    figures. Size is rounded *upward* whenever rounding is
    needed. Therefore, 1001 bytes, being 1.001 kilobyte, is rounded to
    1.01 KB.

    If ``numfmt`` is True, mimick number of format of coreutils
    ``numfmt(1)``, which is also the format used by ``ls(1)``,
    ``du(1)``, etc. At most one decimal place is printed in this
    mode. Note that ``numfmt(1)`` compatibility is not guaranteed, due
    to its use of long double, the precision of which falls short at a
    certain point (while humansize uses PSL's decimal, which defaults to
    28 decimal places -- more than capable for the YB level). On OS X
    10.11.2 with Python 3.5.1, the difference manifests at
    18446744073709551617 = 2^64 + 1 (16E + 1). ``numfmt`` reports 16E,
    while rounding up should produce 17E. Thus, we only test ``numfmt``
    compatibility up to 1EiB.

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
    >>> humansize(31415926, numfmt=True)
    '30MiB'

    """

    if size < 0:
        raise ValueError("size must be nonnegative")
    if prefix not in {"iec-i", "iec", "si"}:
        raise ValueError("expected iec-i, iec, or si; %s received" % prefix)

    size = Decimal(size)
    connection = " " if space else ""
    multiplier = 1000 if prefix == "si" else 1024
    if size < multiplier:
        return "%d%s%s" % (size, connection, unit)

    unitprefix = ""  # suppress undefined-loop-variable
    for unitprefix in _PREFIXES[prefix]:
        size /= multiplier
        if size < multiplier:
            fullunit = "%s%s%s" % (connection, unitprefix, unit)
            if not numfmt:
                # ensure at least three significant figures
                # try two decimal digits
                rounded_size = round_up(size, 2)
                if rounded_size < 10:
                    return "%.2f%s" % (rounded_size, fullunit)
                # try one decimal digit
                rounded_size = round_up(size, 1)
                if rounded_size < 100:
                    return "%.1f%s" % (rounded_size, fullunit)
                # round to whole number
                rounded_size = round_up(size, 0)
                if rounded_size == multiplier:
                    # need to round up to the next unit
                    size = multiplier
                    continue
                return "%.0f%s" % (rounded_size, fullunit)
            else:
                # numfmt - at most one decimal digit
                rounded_size = round_up(size, 1)
                if rounded_size < 10:
                    return "%.1f%s" % (rounded_size, fullunit)
                rounded_size = round_up(size, 0)
                if rounded_size == multiplier:
                    size = multiplier
                    continue
                return "%.0f%s" % (rounded_size, fullunit)

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
    parser.add_argument("-n", "--numfmt", action="store_true",
                        help="""Use the number format of coreutils
                        numfmt(1).""")
    parser.add_argument("sizes", type=int, nargs="*", metavar="SIZE",
                        help="""size in bytes""")
    args = parser.parse_args()

    prefix = args.prefix
    unit = args.unit
    space = args.space
    numfmt = args.numfmt
    if args.sizes:
        sizes = args.sizes
    else:
        sizes = [int(line.strip()) for line in sys.stdin]

    for size in sizes:
        print(humansize(size, prefix, unit, space, numfmt))
