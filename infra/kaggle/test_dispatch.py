from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dispatch  # noqa: E402


class ValidateKernelIdTests(unittest.TestCase):
    def test_accepts_owner_and_slug(self) -> None:
        self.assertEqual(
            dispatch.validate_kernel_id(" thuwon/narrativ-forge "),
            "thuwon/narrativ-forge",
        )

    def test_rejects_missing_or_malformed_id(self) -> None:
        for value in (None, "", "narrativ-forge", "owner/kernel/extra", "https://kaggle.com"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    dispatch.validate_kernel_id(value)

    def test_validates_full_git_sha(self) -> None:
        self.assertEqual(dispatch.validate_git_sha("a" * 40), "a" * 40)
        for value in (None, "", "a" * 39, "g" * 40, "a" * 41):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    dispatch.validate_git_sha(value)

    def test_injects_exact_sha_into_worker_source(self) -> None:
        source = 'TARGET_GIT_SHA = None\nprint("worker")\n'
        rendered = dispatch.render_worker_source(source, "b" * 40)
        self.assertIn('TARGET_GIT_SHA = "' + ("b" * 40) + '"', rendered)
        self.assertNotIn("TARGET_GIT_SHA = None", rendered)

    def test_rejects_missing_sha_marker(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one SHA marker"):
            dispatch.render_worker_source('print("worker")\n', "c" * 40)


class KernelStatusTests(unittest.TestCase):
    @patch("dispatch.subprocess.run")
    def test_parses_known_active_status(self, run: Mock) -> None:
        run.return_value = Mock(
            returncode=0,
            stdout="KernelWorkerStatus.RUNNING",
            stderr="",
        )
        self.assertEqual(dispatch.kernel_status("thuwon/narrativ-forge"), "RUNNING")

    @patch("dispatch.subprocess.run")
    def test_fails_closed_on_nonzero_status_command(self, run: Mock) -> None:
        run.return_value = Mock(returncode=1, stdout="", stderr="private provider detail")
        with self.assertRaisesRegex(RuntimeError, "status lookup failed"):
            dispatch.kernel_status("thuwon/narrativ-forge")

    @patch("dispatch.subprocess.run")
    def test_fails_closed_on_unrecognized_status(self, run: Mock) -> None:
        run.return_value = Mock(returncode=0, stdout="some unexpected output", stderr="")
        with self.assertRaisesRegex(RuntimeError, "unrecognized kernel status"):
            dispatch.kernel_status("thuwon/narrativ-forge")


if __name__ == "__main__":
    unittest.main()
