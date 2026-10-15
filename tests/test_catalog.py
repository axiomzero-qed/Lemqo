import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT
from tools.check_openai_sources import CatalogError, check_catalog


def _record(path, data):
    return {"path": path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _write(root, relative, data):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def make_tiny_snapshot(repository):
    corpus = repository / "corpus" / "openai"
    lean_files = {
        "OAI/Main.lean": b"theorem target : True := True.intro\n",
        "ComparatorChallenges/Example.lean": b"import Mathlib\nexample : True := True.intro\n",
        "lakefile.lean": b"import Lake\n",
    }
    for path, data in lean_files.items():
        _write(corpus, "lean/" + path, data)
    project_data = {
        "lean-toolchain": b"leanprover/lean4:v4.34.1\n",
        "ComparatorChallenges/README.md": b"Local challenge metadata.\n",
        "formalization.yaml": b"version: test\n",
    }
    for path, data in project_data.items():
        _write(corpus, "lean/" + path, data)
    license_bytes = b"Apache License\n"
    _write(corpus, "LICENSE", license_bytes)

    config = {
        "challenge_module": "ComparatorChallenges.Example",
        "solution_module": "OAI.Main",
        "theorem_names": ["OAI.target"],
        "definition_names": [],
        "permitted_axioms": ["propext", "Quot.sound", "Classical.choice"],
        "enable_nanoda": False,
    }
    config_bytes = json.dumps(config, separators=(",", ":")).encode("utf-8")
    _write(corpus, "lean/ComparatorChallenges/Example.json", config_bytes)

    sources = [_record(path, data) for path, data in sorted(lean_files.items())
               if path != "lakefile.lean"]
    projects = [_record(path, data) for path, data in project_data.items()]
    projects.append(_record("lakefile.lean", lean_files["lakefile.lean"]))
    candidate = {
        "id": "example",
        "title": "Example result",
        "theorem": "OAI.target",
        "challenge_module": config["challenge_module"],
        "solution_module": config["solution_module"],
        "challenge_spec": "lean/ComparatorChallenges/Example.lean",
        "challenge_config": "lean/ComparatorChallenges/Example.json",
        "definition_names": [],
        "permitted_axioms": config["permitted_axioms"],
        "enable_nanoda": False,
        "independent_check_status": "pending",
        "challenge_config_bytes": len(config_bytes),
        "challenge_config_sha256": hashlib.sha256(config_bytes).hexdigest(),
    }
    inventory = {item["path"] for item in sources + projects}
    inventory.add(candidate["challenge_config"])
    catalog = {
        "schema_version": 1,
        "upstream": {
            "repository": "https://github.com/openai/math",
            "commit": "0" * 40,
            "license": "LICENSE",
            "license_spdx": "Apache-2.0",
            "license_sha256": hashlib.sha256(license_bytes).hexdigest(),
        },
        "lean_sources_root": "lean/",
        "upstream_catalogue": "lean/formalization.yaml",
        "candidates": [candidate],
        "project_files": projects,
        "source_files": sources,
        "source_file_count": len(sources),
        "source_bytes": sum(item["bytes"] for item in sources),
        "unique_upstream_file_count": len(inventory),
    }
    _write(corpus, "lean/formalization.yaml", project_data["formalization.yaml"])
    (corpus / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
    return corpus


class CatalogTests(unittest.TestCase):
    def test_multi_theorem_candidate_and_config_match(self):
        with tempfile.TemporaryDirectory() as temp:
            repository = Path(temp)
            corpus = make_tiny_snapshot(repository)
            path = corpus / "catalog.json"
            catalog = json.loads(path.read_bytes())
            item = catalog["candidates"][0]
            item.pop("theorem")
            item["theorem_names"] = ["OAI.target", "OAI.second"]
            config_path = corpus / item["challenge_config"]
            config = json.loads(config_path.read_bytes())
            config["theorem_names"] = item["theorem_names"]
            data = json.dumps(config).encode()
            config_path.write_bytes(data)
            item["challenge_config_bytes"] = len(data)
            item["challenge_config_sha256"] = hashlib.sha256(data).hexdigest()
            path.write_text(json.dumps(catalog))
            self.assertEqual(check_catalog(repository).candidates, 1)
            item["theorem_names"] = ["OAI.target"]
            path.write_text(json.dumps(catalog))
            with self.assertRaisesRegex(CatalogError, "theorem target does not match"):
                check_catalog(repository)

    def test_real_snapshot_and_cli(self):
        summary = check_catalog(ROOT)
        self.assertEqual(summary.candidates, 3)
        self.assertEqual(summary.source_files, 349)
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_openai_sources.py")],
            cwd=ROOT, text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("349 Lean files, 3 candidates", result.stdout)
        self.assertIn("no Lean execution", result.stdout)

    def test_tampered_source_fails_with_nonzero_cli_status(self):
        with tempfile.TemporaryDirectory() as temp:
            repository = Path(temp)
            corpus = make_tiny_snapshot(repository)
            source = corpus / "lean" / "OAI" / "Main.lean"
            source.write_bytes(source.read_bytes().replace(b"theorem", b"Theorem", 1))
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "check_openai_sources.py"),
                 "--root", str(repository)],
                cwd=ROOT, text=True, capture_output=True, timeout=15,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("SHA256 mismatch", result.stderr)

    def test_extra_lean_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repository = Path(temp)
            corpus = make_tiny_snapshot(repository)
            _write(corpus, "lean/Unexpected.lean", b"-- not in catalog\n")
            with self.assertRaisesRegex(CatalogError, "unlisted .lean source"):
                check_catalog(repository)

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repository = Path(temp)
            corpus = make_tiny_snapshot(repository)
            catalog_path = corpus / "catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["source_files"][0]["path"] = "../outside.lean"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            with self.assertRaisesRegex(CatalogError, "must not contain"):
                check_catalog(repository)

    def test_duplicate_source_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repository = Path(temp)
            corpus = make_tiny_snapshot(repository)
            catalog_path = corpus / "catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["source_files"].append(catalog["source_files"][0])
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            with self.assertRaisesRegex(CatalogError, "duplicate path in source_files"):
                check_catalog(repository)


if __name__ == "__main__":
    unittest.main()
