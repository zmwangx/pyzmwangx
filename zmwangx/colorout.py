#!/usr/bin/env python3

"""Define utilities for color output.

In this module:

* The ``c`` prefix in function names means color;
* The ``b`` prefix means bold;
* The ``cb`` prefix means bold and color (sometimes rendered as bright);
* Functions with ``print`` in name append a newline to the message;
* Functions with ``write`` in name do not append a newline to the message;
* Functions with ``err`` in name target ``sys.stderr``;
* The ``color`` argument is a case-insensitive string, with choices
  ``"default", "black", "red", "green", "yellow", "blue", "magenta",
  "cyan", "white"``. When default is used, the output is simply not
  colorized.
* Color and face are always reset at the end of printing/writing.

"""

import sys
import warnings

#: ANSI color and face codes.
COLORS = {
    "DEFAULT": "",
    "BLACK" : "\x1b[30m",
    "RED" : "\x1b[31m",
    "GREEN" : "\x1b[32m",
    "YELLOW" : "\x1b[33m",
    "BLUE" : "\x1b[34m",
    "MAGENTA" : "\x1b[35m",
    "CYAN" : "\x1b[36m",
    "WHITE" : "\x1b[37m",
    "BOLD" : "\x1b[1m",
    "RESET" : "\x1b[0m",
}

_COLOR_NAME_CHOICES = {
    "DEFAULT", "BLACK", "RED", "GREEN", "YELLOW",
    "BLUE", "MAGENTA", "CYAN", "WHITE",
}

def cerror(msg):
    """Print error to stderr in red."""
    sys.stderr.write("%serror: %s%s\n" % (COLORS["RED"], msg, COLORS["RESET"]))

def cfatal_error(msg):
    """Print fatal error to stderr in bold red."""
    sys.stderr.write("%s%sfatal error: %s%s\n" %
                     (COLORS["BOLD"], COLORS["RED"], msg, COLORS["RESET"]))

def cwarning(msg):
    """Print warning to stderr in yellow."""
    sys.stderr.write("%swarning: %s%s\n" %
                     (COLORS["YELLOW"], msg, COLORS["RESET"]))

def cprogress(msg):
    """Print progress to stderr in green."""
    sys.stderr.write("%s%s%s\n" % (COLORS["GREEN"], msg, COLORS["RESET"]))

def crprogress(msg):
    """Write progress to stderr in green, preceded by carriage return."""
    sys.stderr.write("\r%s%s%s" % (COLORS["GREEN"], msg, COLORS["RESET"]))

def _normalize_color_name(name):
    """Return a normalized color name.

    The color name is turned to uppercase, and if the name is not found
    in _COLOR_NAME_CHOICES, then "DEFAULT" is returned, but a
    RuntimeWarning will be raised.
    """
    name = name.upper()
    if name in _COLOR_NAME_CHOICES:
        return name
    else:
        warnings.warn("undefined color '%s'" % name, RuntimeWarning)
        return "DEFAULT"

def cprint(color, msg, file=sys.stdout):
    """Print in color."""
    color = _normalize_color_name(color)
    file.write("%s%s%s\n" % (COLORS[color], msg, COLORS["RESET"]))

def cerrprint(color, msg):
    """Print to sys.stderr in color."""
    cprint(color, msg, sys.stderr)

def cwrite(color, msg, file=sys.stdout):
    """Write in color."""
    color = _normalize_color_name(color)
    file.write("%s%s%s" % (COLORS[color], msg, COLORS["RESET"]))

def cerrwrite(color, msg, file=sys.stderr):
    """Write to sys.stderr in color."""
    cwrite(color, msg, sys.stderr)

def bprint(msg, file=sys.stdout):
    """Print in bold."""
    color = _normalize_color_name(color)
    file.write("%s%s%s\n" % (COLORS["BOLD"], msg, COLORS["RESET"]))

def berrprint(msg):
    """Print to sys.stderr in bold."""
    bprint(msg, sys.stderr)

def bwrite(msg, file=sys.stdout):
    """Write in bold."""
    color = _normalize_color_name(color)
    file.write("%s%s%s" % (COLORS["BOLD"], msg, COLORS["RESET"]))

def berrwrite(msg):
    """Write to sys.stderr in bold."""
    bwrite(msg, sys.stderr)

def cbprint(color, msg, file=sys.stdout):
    """Print in bold color."""
    color = _normalize_color_name(color)
    file.write("%s%s%s%s\n" %
               (COLORS["BOLD"], COLORS[color], msg, COLORS["RESET"]))

def cberrprint(color, msg):
    """Print to sys.stderr in bold color."""
    cbprint(color, msg, sys.stderr)

def cbwrite(color, msg, file=sys.stdout):
    """Write in bold color."""
    color = _normalize_color_name(color)
    file.write("%s%s%s%s" %
               (COLORS["BOLD"], COLORS[color], msg, COLORS["RESET"]))

def cberrwrite(color, msg, file=sys.stderr):
    """Write to sys.stderr in bold color."""
    cbwrite(color, msg, sys.stderr)
