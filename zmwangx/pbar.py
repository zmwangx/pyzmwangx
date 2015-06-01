#!/usr/bin/env python3

"""Progress bar."""

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
    boolean

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


# default progress bar update interval
_PROGRESS_UPDATE_INTERVAL = 1.0
# the format string for a progress bar line
#
# 0: processed size, e.g., 2.02GiB
# 1: elapsed time (7 chars), e.g., 0:00:04
# 2: current processing speed, e.g., 424MiB (/s is already hardcoded)
# 3: the bar, in the form "=====>   "
# 4: number of percent done, e.g., 99
# 5: estimated time remaining (11 chars), in the form "ETA H:MM:SS"; if
#    finished, fill with space
_FORMAT_STRING = '\r{0:>7s} {1} [{2:>7s}/s] [{3}] {4:>3s}% {5}'


class ProgressBar(object):

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

    There is another private attribute `__finished` (bool) keeping track
    of whether `finish` has been called. (Protected with double leading
    underscores since no one should ever tamper with this.)

    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, totalsize, preprocessed=0,
                 interval=_PROGRESS_UPDATE_INTERVAL, speed_mode="cumulative"):
        """Initialize the ProgressBar class.

        See class docstring for parameters of the constructor.

        """

        if totalsize <= 0:
            raise ValueError("total size must be positive; got %d" % totalsize)

        self.totalsize = totalsize
        self.processed = preprocessed
        self.preprocessed = preprocessed
        self.start = time.time()
        self.interval = interval
        self.speed_mode = speed_mode
        self._last = self.start
        self._last_processed = 0
        self.__finished = False

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

        self._update_output(force=True)

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

        if self.__finished:
            raise RuntimeError('operation on finished progress bar')

        self.processed += chunk_size
        if self.processed > self.totalsize:
            self.processed = self.totalsize
        self._update_output()

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

        if self.__finished:
            raise RuntimeError('operation on finished progress bar')

        self.processed = processed_size
        if self.processed > self.totalsize:
            self.processed = self.totalsize
        self._update_output()

    def finish(self):
        """Finish file progressing and wrap up on the progress bar.

        Always call this method exactly once after you finish
        processing. This method adds the finishing touches to the
        progress bar, deletes several attributes (`processed`,
        `interval`), and adds a new attribute (`elapsed`).
        After `finish` is called on a ProgressBar attribute, it enters a
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

        if self.__finished:
            raise RuntimeError('operation on finished progress bar')

        self.elapsed = max(time.time() - self.start, 0.001)  # avoid division by zero
        del self.processed
        del self.interval
        del self.speed_mode
        del self._last
        del self._last_processed

        self.__finished = True

        processed_s = zmwangx.humansize.humansize(self.totalsize)
        elapsed_s = self._humantime(self.elapsed)
        speed_s = zmwangx.humansize.humansize(
            (self.totalsize - self.preprocessed) / self.elapsed)
        bar_s = '=' * (self._barlen - 1) + '>'
        percent_s = '100'
        eta_s = ' ' * 11
        sys.stderr.write(_FORMAT_STRING.format(
            processed_s, elapsed_s, speed_s, bar_s, percent_s, eta_s
        ))
        sys.stderr.write("\n")
        sys.stderr.flush()

    def _update_output(self, force=False):
        """Update the progress bar and surrounding data as appropriate.

        Whether the progress bar is refreshed depends on whether we have
        reached the refresh interval since the last refresh (handled
        automatically). If ``force`` is set to ``True`` though, the
        progress bar is refreshed regardless.

        Parameters
        ----------
        force : bool, optional
            Whether to force an update. Default is ``False``.

        Raises
        ------
        RuntimeError:
            If `finish` has already been called on the ProgressBar
            instance before.

        """

        if self.__finished:
            raise RuntimeError('operation on finished progress bar')

        if not force:
            elapsed_since_last = time.time() - self._last
            if elapsed_since_last < self.interval:
                return

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

        sys.stderr.write(_FORMAT_STRING.format(
            processed_s, elapsed_s, speed_s, bar_s, percent_s, eta_s
        ))
        sys.stderr.flush()

    @staticmethod
    def _humantime(seconds):
        """Customized humantime for ProgressBar."""
        return zmwangx.humantime.humantime(seconds, ndigits=0, one_hour_digit=True)
