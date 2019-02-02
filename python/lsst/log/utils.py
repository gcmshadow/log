#!/usr/bin/env python
#
# LSST Data Management System
#
# Copyright 2016  AURA/LSST.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <https://www.lsstcorp.org/LegalNotices/>.
#
import os
import sys
import threading

from lsst.log import Log


def traceSetAt(name, number):
    """!Adjust logging level to display messages with trace number <= NUMBER

    Set the levels of loggers "TRACEn.name" with n > NUMBER to INFO,
    and those with n <= NUMBER to DEBUG, so that only tracing messages
    with n <= NUMBER are shown.

    @param[in] name  The logger name
    @param[in] number  The trace number threshold for display
    """
    for i in range(6):
        level = Log.INFO if i > number else Log.DEBUG
        Log.getLogger('TRACE%d.%s' % (i, name)).setLevel(level)


class LogRedirect:
    """Redirect a logging file descriptor to a Python stream.

    Parameters
    ----------
    fd : `int`
        File descriptor number, usually 1 for standard out, the default log
        output location.
    dest : `io.TextIOBase`
        Destination text stream, often `sys.stderr` for ipython or Jupyter
        notebooks.
    encoding : `str`
        Text encoding of the data written to fd.
    errors : `str`
        Encoding error handling.

    See Also
    --------
    https://stackoverflow.com/questions/41216215
    """

    def __init__(self, fd=1, dest=sys.stderr, encoding="utf-8", errors="strict"):
        self._fd = fd
        self._dest = dest
        # Save original filehandle so we can restore it later.
        self._filehandle = os.dup(fd)

        # Redirect `fd` to the write end of the pipe.
        pipe_read, pipe_write = os.pipe()
        os.dup2(pipe_write, fd)
        os.close(pipe_write)

        # This thread reads from the read end of the pipe.
        def consumer_thread(f, data):
            while True:
                buf = os.read(f, 1024)
                if not buf:
                    break
                data.write(buf.decode(encoding, errors))
            os.close(f)
            return

        # Spawn consumer thread with the desired destination stream.
        self._thread = threading.Thread(target=consumer_thread, args=(pipe_read, dest))
        self._thread.start()

    def finish(self):
        """Stop redirecting output.
        """

        # Cleanup: flush streams, restore `fd`
        self._dest.flush()
        # This dup2 closes the saved file descriptor, which is now the write
        # end of the pipe, causing the thread's read to terminate
        os.dup2(self._filehandle, self._fd)
        os.close(self._filehandle)
        self._thread.join()


_redirect = None


def enable_notebook_logging(dest=sys.stderr):
    """Enable notebook output for log4cxx messages."""
    global _redirect
    if _redirect is None:
        _redirect = LogRedirect(dest=dest)


def disable_notebook_logging():
    """Stop notebook output for log4cxx messages."""
    global _redirect
    if _redirect is not None:
        _redirect.finish()
        _redirect = None
