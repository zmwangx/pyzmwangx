#!/usr/bin/env python3

import argparse

from zmwangx.colorout import cerror

def humantime(seconds, ndigits=0, one_hour_digit=False):
    """Format a duration as a human readable string.

    The duration in seconds (a nonnegative float) is formatted as
    ``HH:MM:SS.frac``, where the number of fractional digits is
    controlled by `ndigits`; if `ndigits` is 0, the decimal point is not
    printed. The number of hour digits (``HH``) can be reduced to one
    with the `one_hour_digits` option.

    Parameters
    ----------
    seconds : float
        Duration in seconds, must be nonnegative.
    ndigits : int, optional
        Number of digits after the decimal point for the seconds part.
        Default is 0. If 0, the decimal point is suppressed.
    one_hour_digit : bool, optional
        If ``True``, only print one hour digit (e.g., nine hours is
        printed as 9:00:00.00). Default is ``False``, i.e., two hour
        digits (nine hours is printed as 09:00:00.00).

    Returns
    -------
    human_readable_duration : str

    Raises
    ------
    ValueError:
        If `seconds` is negative.

    Examples
    --------
    >>> humantime(10.55)
    '00:00:11'
    >>> humantime(10.55, ndigits=1)
    '00:00:10.6'
    >>> humantime(10.55, ndigits=2)
    '00:00:10.55'
    >>> humantime(10.55, one_hour_digit=True)
    '0:00:11'
    >>> # two hours digits for >= 10 hours, even if one_hour_digit is
    >>> # set to True
    >>> humantime(86400, one_hour_digit=True)
    '24:00:00'
    >>> humantime(-1)
    Traceback (most recent call last):
        ...
    ValueError: seconds=-1.000000 is negative, expected nonnegative value

    """

    # pylint: disable=invalid-name
    if seconds < 0:
        raise ValueError("seconds=%f is negative, "
                         "expected nonnegative value" % seconds)

    hh = int(seconds) // 3600  # hours
    mm = (int(seconds) // 60) % 60  # minutes
    ss = seconds - (int(seconds) // 60) * 60  # seconds
    hh_str = "%01d" % hh if one_hour_digit else "%02d" % hh
    mm_str = "%02d" % mm
    if ndigits == 0:
        ss_str = "%02d" % round(ss)
    else:
        ss_format = "%0{0}.{1}f".format(ndigits + 3, ndigits)
        ss_str = ss_format % ss
    return "%s:%s:%s" % (hh_str, mm_str, ss_str)

def main():
    """CLI interface."""
    description = "Convert duration in seconds to human readable format."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-d", "--decimal-digits", metavar="NUM_DIGITS",
                        nargs="?", type=int, const=2, default=0,
                        help="""Print digits after the decimal point. By
                        default the duration is rounded to whole
                        seconds, but this option enables decimal
                        digits. If NUM_DIGITS argument is given, print
                        that many digits after the decimal point; if
                        this option is specified but no NUM_DIGITS is
                        given, print 2 digits after the decimal
                        point.""")
    parser.add_argument("-1", "--one-hour-digit", action="store_true",
                        help="""Only print one hour digit when the
                        duration is less than ten hours. By default the
                        hour is zero-padded to two digits.""")
    parser.add_argument("seconds", type=float,
                        help="Total number of seconds. Must be nonnegative.")
    args = parser.parse_args()
    try:
        print(humantime(args.seconds, ndigits=args.decimal_digits,
                        one_hour_digit=args.one_hour_digit))
    except ValueError as err:
        cerror(str(err))
        return 1
