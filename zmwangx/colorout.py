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

def ccommand(cmd):
    """Print command to run in bold blue."""
    sys.stderr.write("%s%s%s%s\n" %
                     (COLORS["BOLD"], COLORS["BLUE"], cmd, COLORS["RESET"]))

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
        warnings.warn("undefined color '%s'" % name)
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

def cerrwrite(color, msg):
    """Write to sys.stderr in color."""
    cwrite(color, msg, sys.stderr)

def bprint(msg, file=sys.stdout):
    """Print in bold."""
    file.write("%s%s%s\n" % (COLORS["BOLD"], msg, COLORS["RESET"]))

def berrprint(msg):
    """Print to sys.stderr in bold."""
    bprint(msg, sys.stderr)

def bwrite(msg, file=sys.stdout):
    """Write in bold."""
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

def cberrwrite(color, msg):
    """Write to sys.stderr in bold color."""
    cbwrite(color, msg, sys.stderr)

def cnewline(file=sys.stdout):
    """Write a newline to file."""
    file.write("\n")

def cerrnewline():
    """Write a newline to sys.stderr."""
    sys.stderr.write("\n")

def cprompt(prompt, info=None, allow_empty=False, color="green"):
    """Prompt for user input.

    See `cyesno` for documentation of parameters. The `allow_empty`
    parameter dictates whether empty input is allowed; if False, this
    function loops on empty input.

    """
    with open("/dev/tty", "w", encoding="utf-8") as devtty:
        if info is not None:
            cprint(color, info, file=devtty)
        while True:
            cprint(color, prompt, file=devtty)
            devtty.flush()
            response = input()
            if response or allow_empty:
                break
            else:
                cprint("default", "Input should not be empty.", file=devtty)
        return response

def cyesno(info=None, prompt="Continue? [yN] ", default="n", color="yellow"):
    """Prompt for yes/no. Loop on invalid responses.

    Example usage::

        cyesno(info="We are having a bit of trouble here; "
               "continuing execution might blow up your computer.")

    And a session with the parameters above (user input are surrounded
    with * * for clarity)::

        We are having a bit of trouble here; continuing execution might
        blow up your computer.
        Continue? [yN] *what the heck?*
        Please answer yes or no.
        Continue? [yN] *i don't understand!*
        Please answer yes or no.
        Continue? [yN] *n*

    And the return value will be ``False``, for "no".

    Parameters
    ----------
    info : str
        Info string printed at the very beginning. If ``None``, no info
        string is printed. Default is ``None``.
    prompt : str
        Prompt/question printed to the user before asking for yes/no
        each time. (The prompt may be printed multiple times if the user
        provides invalid responses. Default is ``"Continue? [yN] "``.
    default : {"n", "y", None}
        Default response (used in case user's response is empty, i.e.,
        user only presses enter). If ``None``, then there's no default
        response, and an empty response is considered invalid. Default
        is ``"n"``.
    color : str
        Color for info and prompt. Default is yellow.

    Returns
    -------
    boolean
        ``True`` if the interpreted response is "yes", ``False``
        otherwise.

    """
    with open("/dev/tty", "w", encoding="utf-8") as devtty:
        if default is not None:
            if default.startswith(("y", "Y")):
                default = "y"
            elif default.startswith(("n", "N")):
                default = "n"
            else:
                warnings.warn("invalid default '%s', falling back to 'no'" %
                              default)
                default = "n"

        if info is not None:
            cprint(color, info, file=devtty)

        while True:
            cwrite(color, prompt, file=devtty)
            devtty.flush()
            response = input()
            yesno = None
            if not response and default is not None:
                yesno = default
            elif response.startswith(("y", "Y")):
                yesno = "y"
            elif response.startswith(("n", "N")):
                yesno = "n"
            else:
                cprint("default", "Please answer yes or no.", file=devtty)
            if yesno is not None:
                break

        return yesno == "y"
