import atexit
import errno
import os
import shutil
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from ..core.config import settings

if os.name == "nt":
    import msvcrt
else:
    import fcntl


class ProcessingSemaphore:
    def __init__(self, limit: int):
        self._limit = limit
        self._thread_slots = threading.BoundedSemaphore(limit)
        self._owner_pid = os.getpid()
        # Kernel locks are released if a prefork worker exits unexpectedly.
        self._lock_directory = Path(tempfile.mkdtemp(prefix="narrativ-processing-"))
        atexit.register(self._cleanup)

    def _cleanup(self) -> None:
        if os.getpid() == self._owner_pid:
            shutil.rmtree(self._lock_directory, ignore_errors=True)

    @contextmanager
    def acquire(self) -> Iterator[None]:
        with self._thread_slots:
            descriptor = self._acquire_file_slot()
            try:
                yield
            finally:
                self._release_file_slot(descriptor)

    def _acquire_file_slot(self) -> int:
        while True:
            for slot in range(self._limit):
                path = self._lock_directory / f"{slot}.lock"
                descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
                try:
                    locked = self._try_lock(descriptor)
                except BaseException:
                    os.close(descriptor)
                    raise
                if locked:
                    return descriptor
                os.close(descriptor)
            time.sleep(0.05)

    @staticmethod
    def _try_lock(descriptor: int) -> bool:
        try:
            if os.name == "nt":
                if os.fstat(descriptor).st_size == 0:
                    os.write(descriptor, b"\0")
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if exc.errno in {errno.EACCES, errno.EAGAIN} or getattr(exc, "winerror", None) == 33:
                return False
            raise
        return True

    @staticmethod
    def _release_file_slot(descriptor: int) -> None:
        try:
            if os.name == "nt":
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


processing_semaphore = ProcessingSemaphore(settings.worker_max_concurrency)
