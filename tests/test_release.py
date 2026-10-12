import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from tests.support import ROOT


class ReleaseTests(unittest.TestCase):
    def test_reproducible_archives_and_isolated_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            outputs = (base / "first", base / "second")
            for output in outputs:
                result = subprocess.run([sys.executable, str(ROOT / "tools/build_release.py"),
                                         "--out", str(output)], cwd=base,
                                        capture_output=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)
            names = sorted(p.name for p in outputs[0].iterdir())
            self.assertEqual(names, ["SHA256SUMS", "lemqo-0.1.0-source.zip", "lemqo-0.1.0.pyz"])
            for name in names:
                self.assertEqual((outputs[0] / name).read_bytes(), (outputs[1] / name).read_bytes())
            for line in (outputs[0] / "SHA256SUMS").read_text().splitlines():
                digest, name = line.split("  ")
                self.assertEqual(digest, hashlib.sha256((outputs[0] / name).read_bytes()).hexdigest())
            source = outputs[0] / "lemqo-0.1.0-source.zip"
            with zipfile.ZipFile(source) as archive:
                self.assertIsNone(archive.testzip())
                self.assertTrue(all("__pycache__" not in p and "/.git/" not in p for p in archive.namelist()))
                archive.extractall(base / "extracted")
            # Remove Python path overrides; execute outside the source checkout.
            env = dict(os.environ)
            env.pop("PYTHONPATH", None)
            env.pop("PYTHONHOME", None)
            examples = base / "extracted/lemqo-0.1.0/examples"
            runnable = outputs[0] / "lemqo-0.1.0.pyz"
            for invalid, expected in ((False, 0), (True, 1)):
                name = "identity.invalid.proof.json" if invalid else "identity.proof.json"
                result = subprocess.run([sys.executable, "-I", str(runnable), "check", str(examples / name),
                                         "--claim", str(examples / "identity.claim.json")],
                                        cwd=base, env=env, capture_output=True, timeout=15)
                self.assertEqual(result.returncode, expected, result.stderr)
                if invalid:
                    self.assertEqual(result.stdout, b"")
            checkout = base / "extracted/lemqo-0.1.0"
            result = subprocess.run([sys.executable, "-m", "lemqo", "check", "examples/identity.proof.json",
                                     "--claim", "examples/identity.claim.json"], cwd=checkout,
                                    env=env, capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
