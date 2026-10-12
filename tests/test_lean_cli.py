import contextlib
import io
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from lemqo import Rejection
from lemqo.__main__ import main
from tests.support import ROOT


class LeanCLITests(unittest.TestCase):
    args = ["check-lean", "solution.ndjson", "--claim", "claim.json", "--reference", "reference.ndjson",
            "--backends", "backends.json", "--json"]

    def test_all_trusted_inputs_are_required(self):
        for flag in ("--claim", "--reference", "--backends"):
            args = self.args.copy()
            index = args.index(flag)
            del args[index:index + 2]
            process = subprocess.run([sys.executable, "-m", "lemqo", *args], cwd=ROOT, capture_output=True, timeout=10)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(process.stdout, b"")

    def test_rejection_and_internal_error_never_write_a_receipt(self):
        for failure, expected in ((Rejection("lean-kernel", "failed"), 1), (MemoryError(), 3)):
            output, errors = io.StringIO(), io.StringIO()
            with patch("lemqo.__main__.verify_lean_files", side_effect=failure), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                status = main(self.args)
            self.assertEqual(status, expected)
            self.assertEqual(output.getvalue(), "")
            if expected == 1:
                self.assertEqual(json.loads(errors.getvalue())["status"], "rejected")

    def test_bad_timeout_has_bounded_usage_error(self):
        process = subprocess.run([sys.executable, "-m", "lemqo", *self.args, "--timeout", "0"], cwd=ROOT, capture_output=True, timeout=10)
        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, b"")
        self.assertLess(len(process.stderr), 2000)
