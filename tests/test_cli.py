import contextlib
import io
import json
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

from lemqo.__main__ import main
from tests.support import ROOT


class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "lemqo", *args], cwd=ROOT,
                              text=True, capture_output=True, timeout=15)

    def test_valid_receipt(self):
        result = self.run_cli("check", "examples/identity.proof.json", "--claim",
                              "examples/identity.claim.json", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout)["status"], "valid")

    def test_invalid_certificate_nonzero_and_no_success(self):
        result = self.run_cli("check", "examples/identity.invalid.proof.json", "--claim",
                              "examples/identity.claim.json", "--json")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr)["status"], "rejected")

    def test_claim_is_required(self):
        result = self.run_cli("check", "examples/identity.proof.json")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_io_failure(self):
        result = self.run_cli("check", "does-not-exist", "--claim", "examples/identity.claim.json")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_internal_failure_never_prints_valid(self):
        output, errors = io.StringIO(), io.StringIO()
        with patch("lemqo.__main__.verify_bytes", side_effect=MemoryError), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = main(["check", "examples/identity.proof.json", "--claim", "examples/identity.claim.json"])
        self.assertEqual(status, 3)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("internal", errors.getvalue())

    def test_version_and_help(self):
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn("0.1.0", result.stdout)
        self.assertEqual(self.run_cli("--help").returncode, 0)

    def test_receipt_unchanged_by_hash_seed(self):
        outputs = []
        for seed in ("1", "873"):
            env = dict(os.environ, PYTHONHASHSEED=seed)
            result = subprocess.run([sys.executable, "-m", "lemqo", "check", "examples/distributivity.proof.json",
                                     "--claim", "examples/distributivity.claim.json", "--json"],
                                    cwd=ROOT, env=env, capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            outputs.append(result.stdout)
        self.assertEqual(outputs[0], outputs[1])
