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
