#!/usr/bin/env python3

"""Progress bar or progress text."""

import os
import subprocess
import sys
import time

import zmwangx.humansize
import zmwangx.humantime
from zmwangx.colorout import cwarning


def autopbar():
    """Check if it is desirable to print a progress bar.

    Returns True if the process has a stderr connected to a tty, and the
    process is in foreground.

    Returns
    -------
    bool

    """

    # check tty
    if not sys.stderr.isatty():
        return False

    # check foreground
    pid = os.getpid()
    try:
        ps_command_line = ["ps", "-o", "state", "-p", str(pid)]
        state = subprocess.check_output(ps_command_line).decode("utf-8")
        if "+" not in state:  # not in foreground
            return False
    except subprocess.CalledProcessError:
        cwarning("'%s' failed" % " ".join(ps_command_line))

    return True


class ProgressText(object):

    """Print textual progress information.

    To use this class, init a ``ProgressText`` instance, then update the
    progress text with the `text` method. The `text` method takes a
    textual string or a function to generate the textual string, and
    arguments and keyword arguments to the function can be passed via
    `text`. After you finish progressing, you must call the `finish`
    method to wrap it up. Any further calls after the `finish` method
    has been called lead to a ``RuntimeError``.

    Each ProgressText instance defines several public attributes listed
    below. Some are available during processing, and some after
    processing. These attributes are meant for informational purposes,
    and you should not manually tamper with them (which mostly likely
    leads to undefined behavior).

    Parameters
    ----------
    interval : float, optional
        Update (refresh) interval of the progress bar, in
        seconds. Default is 1.0.
    show_elapsed_time : bool, optional
        Whether to prefix textual progress information with elapsed
        time. The prefix is in the form ``H:MM:SS: ``. Default is
        ``True``.
    init_text : str, optional
        Initial text to print. Default is ``""``.

    Attributes
    ----------
    start : float
        Starting time (an absolute time returned by
        ``time.time()``). Available throughout.
    interval : float
        Update (refresh) interval of the progress bar, in
        seconds. Available only during processing (deleted after the
        `finish` call).
    show_elapsed_time : bool
        Whether to prefix textual progress information with elapsed
        time. Available only during processing (deleted after the
        `finish` call).
    elapsed : float
        Total elapsed time, in seconds. Only available after the
        `finish` call.

    Notes
    -----
    For developers: ProgressText also defines a private attribute
    ``_last`` during processing (deleted after the `finish` call) which
    stores the absolute time of last update (refresh).

    There is another private attribute ``_finished`` (bool) keeping
    track of whether `finish` has been called. Do not tamper with this
    attribute manually.

    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, interval=0.1, show_elapsed_time=True, init_text=""):
        """Initialize the ProgressText class.

        See class docstring for parameters of the constructor.

        """

        self.start = time.time()
        self.interval = interval
        self.show_elapsed_time = show_elapsed_time
        self._last = self.start
        self._finished = False

        self.text(init_text, force=True)

    def text(self, content, *args, force=False, **kwargs):
        """Update progress text.

        Whether the progress text is redrawn or not depends on whether
        we have reached the refresh interval since the last refresh
        (handled automatically).

        Parameters
        ----------
        content : str or function
            If ``content`` is ``str``, it will be the content printed to
            the user (optionally prefixed by time elapsed, if
            ``show_elapsed_time`` is set to ``True`` in ``__init__``).

            Otherwise, ``content`` is taken to be a callable function or
            method, and the content to be printed to the user
            (optionally prefixed by time elapsed) is generated
            dynamically by calling ``content(*args, **kwargs)``.

            Caution: ``content`` is only called after a decision to
            redraw is made, so it might be called every time ``update``
            is called.
        *args
            Arguments passed to ``content``, if it is callable.
        force : bool, optional
            Whether to disregard the refresh interval and force
            a redraw. Default is ``False``.
        **kwargs
            Keyword arguments to ``content``, if it is callable.

        Raises
        ------
        RuntimeError:
            If `finish` has been called on the ProgressText instance.

        """

        if self._finished:
            raise RuntimeError('operation on finished instance')

        if not force:
            elapsed_since_last = time.time() - self._last
            if elapsed_since_last < self.interval:
                return

        try:
            text = content(*args, **kwargs)
        except TypeError:
            text = content

        if self.show_elapsed_time:
            elapsed_time = time.time() - self.start
            text = "%s: " % self._humantime(elapsed_time) + text

        sys.stderr.write("\r\x1b[K%s" % text)
        sys.stderr.flush()

    def finish(self, content, *args, **kwargs):
        """Add finishing touches to the progress output.

        Always call this method exactly once after you finish
        processing. This method adds the finishing touches to the
        progress output, deletes several attributes (`interval`,
        `show_elapsed_time`, etc.), and adds a new attribute
        (`elapsed`).  After `finish` is called on a ProgressText
        instance, it enters a read-only mode: you may read the `start`
        and `elapsed` attributes, but any method call leads to a
        ``RuntimeError``.

        Parameters
        ----------
        finish_text : str or function
            Finishing text. Similar to the ``content`` argument of
            the ``update`` method.

        Raises
        ------
        RuntimeError:
            If `finish` has already been called on the ProgressText
            instance before.
        *args
            Arguments passed to ``content``, if it is callable.
        **kwargs
            Keyword arguments to ``content``, if it is callable.

        """

        # pylint: disable=attribute-defined-outside-init

        if self._finished:
            raise RuntimeError('operation on finished instance')

        self.elapsed = max(time.time() - self.start, 0.001)  # avoid division by zero

        try:
            text = content(*args, **kwargs)
        except TypeError:
            text = content

        if self.show_elapsed_time:
            elapsed_time = time.time() - self.start
            text = "%s: " % self._humantime(elapsed_time) + text

        sys.stderr.write("\r\x1b[K%s" % text)
        sys.stderr.write("\n")
        sys.stderr.flush()

        del self.interval
        del self.show_elapsed_time
        del self._last

        self._finished = True

    @staticmethod
    def _humantime(seconds):
        """Customized humantime for ProgressText."""
        return zmwangx.humantime.humantime(seconds, ndigits=0, one_hour_digit=True)


class ProgressBar(ProgressText):

    """Progress bar for file processing.

    To generate a progress bar, init a ProgressBar instance, then update
    frequently with the `update` method, passing in the size of newly
    processed chunk. The `force_update` method should only be called if
    you want to overwrite the processed size, which is automatically
    calculated incrementally. After you finish processing the
    file/stream, you must call the `finish` method to wrap it up. Any
    further calls after the `finish` method has been called lead to
    a ``RuntimeError``.

    Each ProgressBar instance defines several public attributes listed
    below. Some are available during processing, and some after
    processing. These attributes are meant for informational purposes,
    and you should not manually tamper with them (which mostly likely
    leads to undefined behavior).

    The progress bar format is inspired by ``pv(1)`` (pipe viewer).

    Parameters
    ----------
    totalsize : int
        Total size, in bytes, of the file/stream to be processed.
    preprocessed : int, optional
        Size of preprocessed portion, in bytes. The preprocessed portion
        counts towards the percentage processed, but does not count
        towards speed. Default is ``0``.
    interval : float, optional
        Update (refresh) interval of the progress bar, in
        seconds. Default is 1.0.
    speed_mode : {"cumulative", "instant"}, optional
        The mode in which current processing speed is calculated. If
        "cumulative", the speed is total processed size divided by total
        time elapsed; if "instant", the speed is size processed since
        the last update divided by time elapsed since last
        update. Default is "cumulative", which is more stable.

    Attributes
    ----------
    totalsize : int
        Total size of file/stream, in bytes. Available throughout.
    processed : int
        Process size. Available only during processing (deleted after
        the `finish` call).
    start : float
        Starting time (an absolute time returned by
        ``time.time()``). Available throughout.
    interval : float
        Update (refresh) interval of the progress bar, in
        seconds. Available only during processing (deleted after the
        `finish` call).
    speed_mode : {"cumulative", "instant"}
        The mode in which speed is calculated. Available only during
        processing (deleted after the `finish` call).
    elapsed : float
        Total elapsed time, in seconds. Only available after the
        `finish` call.

    Notes
    -----
    For developers: ProgressBar also defines three private attributes,
    `_last`, `_last_processed` and `_barlen`, during processing (deleted
    after the `finish` call). `_last` stores the absolute time of last
    update (refresh), `_last_processed` stores the processed size at the
    time of the last update (refresh), and `_barlen` stores the length
    of the progress bar (only the bar portion).

    There is another private attribute `_finished` (bool) keeping track
    of whether `finish` has been called. Do not tamper with this
    attribute manually.

    """

    # pylint: disable=too-many-instance-attributes

    # the format string for a progress bar line
    #
    # 0: processed size, e.g., 2.02GiB
    # 1: elapsed time (7 chars), e.g., 0:00:04
    # 2: current processing speed, e.g., 424MiB (/s is already hardcoded)
    # 3: the bar, in the form "=====>   "
    # 4: number of percent done, e.g., 99
    # 5: estimated time remaining (11 chars), in the form "ETA H:MM:SS";
    #    if finished, fill with space
    _FORMAT_STRING = '{0:>7s} {1} [{2:>7s}/s] [{3}] {4:>3s}% {5}'

    def __init__(self, totalsize, preprocessed=0, interval=1.0,
                 speed_mode="cumulative"):
        """Initialize the ProgressBar class.

        See class docstring for parameters of the constructor.

        """

        if totalsize <= 0:
            raise ValueError("total size must be positive; got %d" % totalsize)

        super().__init__(interval=interval, show_elapsed_time=False)

        self.totalsize = totalsize
        self.processed = preprocessed
        self.preprocessed = preprocessed
        self.speed_mode = speed_mode
        self._last_processed = 0

        # calculate bar length
        try:
            ncol, _ = os.get_terminal_size()
        except (AttributeError, OSError):
            # Python2 do not have os.get_terminal_size.  Also,
            # os.get_terminal_size fails if stdout is redirected to a
            # pipe (pretty stupid -- should check stderr; relevant
            # Python bug: https://bugs.python.org/issue14841). In either
            # case, Assume a minimum of 80 columns.
            ncol = 80
        self._barlen = (ncol - 48) if ncol >= 58 else 10

        super().text(self._generate_bar, force=True)

    def update(self, chunk_size):
        """Update the progress bar for a newly processed chunk.

        The size of the processed chunk is registered. Whether the
        progress bar is refreshed depends on whether we have reached the
        refresh interval since the last refresh (handled automatically).

        Parameters
        ----------
        chunk_size : int
            The size of the newly processed chunk (since last update),
            in bytes. This size will be added to the `processed`
            attribute.

        Raises
        ------
        RuntimeError:
            If `finish` has been called on the ProgressBar instance.

        """

        if self._finished:
            raise RuntimeError('operation on finished progress bar')

        self.processed += chunk_size
        if self.processed > self.totalsize:
            self.processed = self.totalsize
        super().text(self._generate_bar)

    def force_update(self, processed_size):
        """Force update the progress bar with a given processed size.

        The `processed` attribute is overwritten by the new value.

        Parameters
        ----------
        processed_size :
            Processed size of the file/stream, in bytes. Existing value
            is overwritten by this value.

        Raises
        ------
        RuntimeError:
            If `finish` has been called on the ProgressBar instance.

        """

        if self._finished:
            raise RuntimeError('operation on finished progress bar')

        self.processed = processed_size
        if self.processed > self.totalsize:
            self.processed = self.totalsize
        super().text(self._generate_bar, force=True)

    def finish(self):
        """Finish file progressing and wrap up on the progress bar.

        Always call this method exactly once after you finish
        processing. This method adds the finishing touches to the
        progress bar, deletes several attributes (`processed`,
        `interval`, etc.), and adds a new attribute (`elapsed`).
        After `finish` is called on a ProgressBar instance, it enters a
        read-only mode: you may read the `totalsize`, `start`, and
        `elapsed` attributes, but any method call leads to a
        ``RuntimeError``.

        Raises
        ------
        RuntimeError:
            If `finish` has already been called on the ProgressBar
            instance before.

        """

        # pylint: disable=attribute-defined-outside-init

        if self._finished:
            raise RuntimeError('operation on finished progress bar')

        del self.speed_mode
        del self._last_processed

        super().finish(self._generate_finish_bar)

    def _generate_bar(self):
        """Calculates the progress bar text to be printed.

        Raises
        ------
        RuntimeError:
            If `finish` has already been called on the ProgressBar
            instance before.

        """

        if self._finished:
            raise RuntimeError('operation on finished progress bar')

        if self.speed_mode == "instant":
            # speed in the last second, in bytes per second
            elapsed_since_last = max(elapsed_since_last, 0.001)  # avoid division by zero
            speed = ((self.processed - self._last_processed) / elapsed_since_last)
            if speed < 0:
                speed = 0
        else:
            # cumulative speed, in bytes per second
            elapsed = max(time.time() - self.start, 0.001)  # avoid division by zero
            speed = (self.processed - self.preprocessed) / elapsed

        # update last stats for the next update
        self._last = time.time()
        self._last_processed = self.processed

        # _s suffix stands for string
        processed_s = zmwangx.humansize.humansize(self.processed)
        elapsed_s = self._humantime(time.time() - self.start)
        speed_s = zmwangx.humansize.humansize(speed)
        percentage = self.processed / self.totalsize  # absolute
        percent_s = str(int(percentage * 100))
        # generate bar
        length = int(round(self._barlen * percentage))
        fill = self._barlen - length
        if length == 0:
            bar_s = " " * self._barlen
        else:
            bar_s = '=' * (length - 1) + '>' + ' ' * fill
        # calculate ETA
        remaining = self.totalsize - self.processed
        # estimate based on current speed
        if speed > 0:
            eta = remaining / speed
            eta_s = "ETA %s" % self._humantime(eta)
        else:
            eta_s = "ETA unknown"

        return self._FORMAT_STRING.format(
            processed_s, elapsed_s, speed_s, bar_s, percent_s, eta_s)

    def _generate_finish_bar(self):
        """Calculates the finishing progress bar text to be printed.

        Raises
        ------
        RuntimeError:
            If `finish` has already been called on the ProgressBar
            instance before.

        """

        processed_s = zmwangx.humansize.humansize(self.totalsize)
        elapsed_s = self._humantime(self.elapsed)
        speed_s = zmwangx.humansize.humansize(
            (self.totalsize - self.preprocessed) / self.elapsed)
        bar_s = '=' * (self._barlen - 1) + '>'
        percent_s = '100'
        eta_s = ' ' * 11
        return self._FORMAT_STRING.format(
            processed_s, elapsed_s, speed_s, bar_s, percent_s, eta_s)

    @staticmethod
    def _humantime(seconds):
        """Customized humantime for ProgressBar."""
        return zmwangx.humantime.humantime(seconds, ndigits=0, one_hour_digit=True)
