"""Native process locks for a retained file; callers own path safety checks."""

from __future__ import annotations

from contextlib import contextmanager
import errno
import os
import time
from typing import BinaryIO, Iterator

if os.name == "nt":
    import msvcrt as _msvcrt
    _fcntl = None
else:
    import fcntl as _fcntl
    _msvcrt = None


@contextmanager
def try_exclusive_lock(stream: BinaryIO) -> Iterator[bool]:
    """Try once to acquire the retained file lock, yielding whether it succeeded."""
    if _msvcrt is not None:
        stream.seek(0)
        try:
            _msvcrt.locking(stream.fileno(), _msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            if exc.errno != errno.EACCES:
                raise
            yield False
            return
        try:
            yield True
        finally:
            stream.seek(0)
            _msvcrt.locking(stream.fileno(), _msvcrt.LK_UNLCK, 1)
    else:
        assert _fcntl is not None
        try:
            _fcntl.flock(stream.fileno(), _fcntl.LOCK_EX | _fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            _fcntl.flock(stream.fileno(), _fcntl.LOCK_UN)


@contextmanager
def exclusive_lock(stream: BinaryIO) -> Iterator[None]:
    """Hold a native exclusive lock until exit, including exceptional exit.

    Keep the same file in place: deleting/replacing it would let waiters lock
    distinct inodes. Windows locks byte zero (which may legally be past EOF),
    so no initialization write or truncation race is needed. Its nonblocking
    primitive is retried only for contention, matching POSIX blocking flock
    without the CRT LK_LOCK primitive's ten-attempt acquisition limit.
    """
    if _msvcrt is not None:
        while True:
            stream.seek(0)
            try:
                _msvcrt.locking(stream.fileno(), _msvcrt.LK_NBLCK, 1)
                break
            except OSError as exc:
                if exc.errno != errno.EACCES:
                    raise
                time.sleep(0.05)
        try:
            yield
        finally:
            stream.seek(0)
            _msvcrt.locking(stream.fileno(), _msvcrt.LK_UNLCK, 1)
    else:
        assert _fcntl is not None
        _fcntl.flock(stream.fileno(), _fcntl.LOCK_EX)
        try:
            yield
        finally:
            _fcntl.flock(stream.fileno(), _fcntl.LOCK_UN)
