import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from lemqo import __version__
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
            prefix = f"lemqo-{__version__}"
            self.assertEqual(names, ["SHA256SUMS", f"{prefix}-source.zip", f"{prefix}.pyz"])
            for name in names:
                self.assertEqual((outputs[0] / name).read_bytes(), (outputs[1] / name).read_bytes())
            for line in (outputs[0] / "SHA256SUMS").read_text().splitlines():
                digest, name = line.split("  ")
                self.assertEqual(digest, hashlib.sha256((outputs[0] / name).read_bytes()).hexdigest())
            source = outputs[0] / f"{prefix}-source.zip"
            with zipfile.ZipFile(source) as archive:
                self.assertIsNone(archive.testzip())
                source_names = set(archive.namelist())
                self.assertTrue(all(
                    not ({"__pycache__", ".lake", ".cache", "cache", "caches", "build", "dist"}
                         & set(Path(name).parts))
                    and not any(part.endswith(".egg-info") for part in Path(name).parts)
                    and ".git" not in Path(name).parts
                    for name in source_names
                ))
                self.assertIn(f"{prefix}/corpus/openai/LICENSE", source_names)
                self.assertIn(f"{prefix}/corpus/openai/lean/formalization.yaml", source_names)
                self.assertIn(f"{prefix}/corpus/openai/lean/OAI/Combinatorics/SecondNeighborhood/Main.lean",
                              source_names)
                self.assertIn(f"{prefix}/bridge/lean/Main.lean", source_names)
                self.assertIn(f"{prefix}/bridge/lean/lean-toolchain", source_names)
                self.assertIn(f"{prefix}/bridge/lean/.gitignore", source_names)
                archive.extractall(base / "extracted")
            # Remove Python path overrides; execute outside the source checkout.
            env = dict(os.environ)
            env.pop("PYTHONPATH", None)
            env.pop("PYTHONHOME", None)
            examples = base / "extracted" / prefix / "examples"
            runnable = outputs[0] / f"{prefix}.pyz"
            with zipfile.ZipFile(runnable) as archive:
                runnable_names = archive.namelist()
                self.assertTrue(all(name.endswith(".py") or name == "LICENSE"
                                    for name in runnable_names))
                self.assertFalse(any(name.startswith(("bridge/", "corpus/"))
                                     for name in runnable_names))
                self.assertEqual(archive.read("LICENSE"), (ROOT / "LICENSE").read_bytes())
            for invalid, expected in ((False, 0), (True, 1)):
                name = "identity.invalid.proof.json" if invalid else "identity.proof.json"
                result = subprocess.run([sys.executable, "-I", str(runnable), "check", str(examples / name),
                                         "--claim", str(examples / "identity.claim.json")],
                                        cwd=base, env=env, capture_output=True, timeout=15)
                self.assertEqual(result.returncode, expected, result.stderr)
                if invalid:
                    self.assertEqual(result.stdout, b"")
            checkout = base / "extracted" / prefix
            # Packaging must retain the complete pinned corpus, not just a sample.
            from tools.check_openai_sources import check_catalog
            self.assertEqual(check_catalog(checkout).source_files, 349)
            result = subprocess.run([sys.executable, "-m", "lemqo", "check", "examples/identity.proof.json",
                                     "--claim", "examples/identity.claim.json"], cwd=checkout,
                                    env=env, capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
