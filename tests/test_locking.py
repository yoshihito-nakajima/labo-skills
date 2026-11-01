"""Native process serialization plus explicitly mocked Windows CRT branches."""

import builtins
import errno
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from labo_tools import build, locking  # noqa: E402
from labo_tools.build import output_transaction  # noqa: E402
from labo_tools.paper import PaperError  # noqa: E402


SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
CHILD = r"""
from pathlib import Path
import os
import sys
sys.path.insert(0, sys.argv[1])
from labo_tools.build import output_transaction
workspace, marker, mode = Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
marker.with_suffix('.attempt').write_text('attempting', encoding='utf-8')
with output_transaction(workspace):
    marker.write_text('acquired', encoding='utf-8')
    if mode == 'hold':
        if sys.stdin.readline() != 'release\n':
            raise RuntimeError('holder was not released normally')
    elif mode == 'crash':
        os._exit(17)
"""


class OutputLockTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()

    def child(self, marker, mode="once"):
        process = subprocess.Popen(
            [sys.executable, "-I", "-B", "-u", "-c", CHILD,
             str(SOURCE_ROOT), str(self.root), str(marker), mode],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(self.stop, process)
        return process

    @staticmethod
    def stop(process):
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=10)

    def wait_for(self, path, process):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if path.exists():
                return
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=5)
                self.fail(f"child exited before {path.name}: {process.returncode}, {stdout}, {stderr}")
            time.sleep(0.01)
        self.fail(f"child did not reach {path.name} within 10 seconds")

    def assert_success(self, process, *, release=False):
        stdout, stderr = process.communicate(input="release\n" if release else None, timeout=10)
        self.assertEqual(process.returncode, 0, stdout + stderr)

    def test_native_processes_serialize_and_reuse_the_retained_file(self):
        first_marker = self.root / "first.acquired"
        first = self.child(first_marker, "hold")
        self.wait_for(first_marker, first)
        lock_path = self.root / ".labo-output.lock"
        inode = lock_path.stat().st_ino
        second_marker = self.root / "second.acquired"
        second = self.child(second_marker)
        self.wait_for(second_marker.with_suffix(".attempt"), second)
        # The second process has started acquisition but cannot enter while held.
        deadline = time.monotonic() + 0.2
        while time.monotonic() < deadline:
            self.assertFalse(second_marker.exists())
            self.assertIsNone(second.poll())
            time.sleep(0.01)
        self.assert_success(first, release=True)
        self.assert_success(second)
        self.assertTrue(second_marker.exists())
        self.assertTrue(lock_path.is_file())
        self.assertEqual(lock_path.stat().st_ino, inode)
        self.assertEqual(lock_path.read_bytes(), b"")
        self.assertFalse((self.root / "output/.labo-output.lock").exists())

    def test_native_exception_releases_lock_for_another_process(self):
        lock_path = self.root / ".labo-output.lock"
        lock_path.write_bytes(b"do not truncate or replace this file")
        inode = lock_path.stat().st_ino
        with self.assertRaisesRegex(RuntimeError, "synthetic body failure"):
            with output_transaction(self.root) as output:
                self.assertEqual(output, self.root / "output")
                raise RuntimeError("synthetic body failure")
        process = self.child(self.root / "after-exception.acquired")
        self.assert_success(process)
        self.assertEqual(lock_path.stat().st_ino, inode)
        self.assertEqual(lock_path.read_bytes(), b"do not truncate or replace this file")

    def test_native_process_exit_releases_os_lock(self):
        process = self.child(self.root / "crashed.acquired", "crash")
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 17, stdout + stderr)
        follower = self.child(self.root / "after-crash.acquired")
        self.assert_success(follower)

    def test_symlink_output_and_lock_remain_rejected_where_supported(self):
        actual = self.root / "actual"
        actual.mkdir()
        output = self.root / "output"
        try:
            output.symlink_to(actual, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"native symlink creation unavailable: {exc}")
        with self.assertRaisesRegex(PaperError, "output directory.*symlink"):
            with output_transaction(self.root):
                self.fail("symlinked output accepted")
        output.unlink()
        target = self.root / "target.lock"
        target.write_bytes(b"preserve")
        (self.root / ".labo-output.lock").symlink_to(target)
        with self.assertRaisesRegex(PaperError, "output lock.*symlink"):
            with output_transaction(self.root):
                self.fail("symlinked lock accepted")
        self.assertEqual(target.read_bytes(), b"preserve")


class MockWindowsLockTests(unittest.TestCase):
    """CRT call contracts mocked on every OS; these are not native Windows tests."""

    def setUp(self):
        self.crt = SimpleNamespace(LK_NBLCK=2, LK_UNLCK=0, locking=Mock())
        self.stream = Mock()
        self.stream.fileno.return_value = 41
        self.patches = (
            patch.object(locking, "_msvcrt", self.crt),
            patch.object(locking, "_fcntl", None),
            patch.object(locking.time, "sleep"),
        )
        for patcher in self.patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_windows_acquires_and_releases_byte_zero_even_after_seek(self):
        with locking.exclusive_lock(self.stream):
            self.stream.seek(99)
        self.assertEqual(self.crt.locking.call_args_list, [
            unittest.mock.call(41, self.crt.LK_NBLCK, 1),
            unittest.mock.call(41, self.crt.LK_UNLCK, 1),
        ])
        self.assertEqual(self.stream.seek.call_args_list,
                         [unittest.mock.call(0), unittest.mock.call(99), unittest.mock.call(0)])

    def test_windows_retries_only_contention(self):
        self.crt.locking.side_effect = [OSError(errno.EACCES, "contended"), None, None]
        with locking.exclusive_lock(self.stream):
            pass
        locking.time.sleep.assert_called_once_with(0.05)
        self.assertEqual(self.crt.locking.call_count, 3)

    def test_windows_noncontention_error_propagates_without_unlock(self):
        self.crt.locking.side_effect = OSError(errno.EBADF, "bad descriptor")
        with self.assertRaises(OSError) as caught:
            with locking.exclusive_lock(self.stream):
                self.fail("entered without acquiring")
        self.assertEqual(caught.exception.errno, errno.EBADF)
        self.crt.locking.assert_called_once_with(41, self.crt.LK_NBLCK, 1)
        locking.time.sleep.assert_not_called()

    def test_windows_body_exception_unlocks(self):
        with self.assertRaisesRegex(RuntimeError, "synthetic"):
            with locking.exclusive_lock(self.stream):
                raise RuntimeError("synthetic")
        self.assertEqual(self.crt.locking.call_args_list[-1],
                         unittest.mock.call(41, self.crt.LK_UNLCK, 1))

    def test_windows_interrupted_wait_does_not_unlock_unacquired_region(self):
        self.crt.locking.side_effect = OSError(errno.EACCES, "contended")
        locking.time.sleep.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            with locking.exclusive_lock(self.stream):
                self.fail("entered without acquiring")
        self.crt.locking.assert_called_once_with(41, self.crt.LK_NBLCK, 1)

    def test_windows_transaction_closes_handle_when_acquisition_fails(self):
        self.assert_transaction_closes_handle([OSError(errno.EBADF, "synthetic acquisition failure")])

    def test_windows_transaction_closes_handle_when_unlock_fails(self):
        self.assert_transaction_closes_handle([None, OSError(errno.EBADF, "synthetic unlock failure")])

    def assert_transaction_closes_handle(self, outcomes):
        self.crt.locking.side_effect = outcomes
        streams = []
        original = build.exclusive_lock

        def capture(stream):
            streams.append(stream)
            return original(stream)

        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(build, "exclusive_lock", side_effect=capture):
                with self.assertRaises(OSError):
                    with output_transaction(Path(temporary)):
                        pass
            self.assertEqual(len(streams), 1)
            self.assertTrue(streams[0].closed)
            self.assertTrue((Path(temporary) / ".labo-output.lock").is_file())

    def test_windows_import_does_not_request_fcntl(self):
        imports = []
        original_import = builtins.__import__

        def windows_import(name, *args, **kwargs):
            imports.append(name)
            if name == "os":
                return SimpleNamespace(name="nt")
            if name == "msvcrt":
                return self.crt
            if name == "fcntl":
                raise AssertionError("native Windows must not import fcntl")
            return original_import(name, *args, **kwargs)

        namespace = {"__name__": "synthetic_windows_locking",
                     "__builtins__": {**vars(builtins), "__import__": windows_import}}
        source = Path(locking.__file__).read_text(encoding="utf-8")
        exec(compile(source, "synthetic_windows_locking.py", "exec"), namespace)
        self.assertIn("msvcrt", imports)
        self.assertNotIn("fcntl", imports)
        self.assertIsNone(namespace["_fcntl"])


if __name__ == "__main__":
    unittest.main()
