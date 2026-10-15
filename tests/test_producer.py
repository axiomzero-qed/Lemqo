import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lemqo import Rejection
from tests.support import ROOT
from tools import openai_certificates as producer
from tools.check_openai_sources import CatalogError, import_roots, theorem_names


class ProducerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.work = self.base / "work"
        self.work.mkdir()
        self.out = self.base / "output"
        self.backends = self.base / "backends.json"
        self.backends.write_text("{}")
        self.catalog = json.loads((ROOT / "corpus/openai/catalog.json").read_bytes())
        self.items = self.catalog["candidates"][:2]
        self.ids = [item["id"] for item in self.items]

    def produce(self, **options):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return producer.produce(self.work, self.out, self.backends, self.ids, **options)

    def test_per_target_rejection_continues_and_summary_is_durable(self):
        receipt = {"status": "valid", "checked_declarations": 7}
        with patch.object(producer, "validate_exports"), patch.object(producer, "check_target", side_effect=[Rejection("test-rejection", "bad proof"), receipt]) as check, patch.object(producer, "prepare_project") as prepare, patch.object(producer, "run") as run:
            rows = self.produce(phase="check")
        self.assertEqual(check.call_count, 2)
        prepare.assert_not_called()
        run.assert_not_called()
        self.assertEqual([r["status"] for r in rows], ["rejected", "valid"])
        self.assertFalse((self.out / self.ids[0] / "receipt.json").exists())
        failed = json.loads((self.out / self.ids[0] / "failed.json").read_bytes())
        self.assertEqual(failed["code"], "test-rejection")
        self.assertIn("duration_seconds", failed)
        self.assertEqual(json.loads((self.out / "batch-summary.json").read_bytes())["targets"], rows)
        self.assertEqual(json.loads((self.out / self.ids[1] / "receipt.json").read_bytes()), receipt)

    def test_reused_exports_need_no_build_or_lean_installation(self):
        with patch.object(producer, "validate_exports"), patch.object(producer, "check_target", return_value={"checked_declarations": 7}), patch.object(producer, "prepare_project") as prepare, patch.object(producer, "run") as run:
            rows = self.produce(reuse_exports=True)
        self.assertEqual([r["status"] for r in rows], ["valid", "valid"])
        prepare.assert_not_called()
        run.assert_not_called()

    def test_resume_does_not_recheck_but_stale_receipt_does(self):
        with patch.object(producer, "validate_exports"), patch.object(producer, "resume_receipt", side_effect=[{"checked_declarations": 9}, Rejection("stale", "changed backend")]), patch.object(producer, "check_target", return_value={"checked_declarations": 7}) as check, patch.object(producer, "prepare_project") as prepare:
            rows = self.produce(phase="check", resume=True)
        self.assertEqual([r["status"] for r in rows], ["reused", "valid"])
        self.assertEqual(check.call_count, 1)
        prepare.assert_not_called()

    def test_export_phase_never_builds_downloads_cache_or_checks(self):
        with patch.object(producer, "prepare_project"), patch.object(producer, "assert_lake_pins"), patch.object(producer, "export_target") as export, patch.object(producer, "build_target") as build, patch.object(producer, "check_target") as check, patch.object(producer, "run") as run:
            rows = self.produce(phase="export")
        self.assertEqual(export.call_count, 2)
        build.assert_not_called()
        run.assert_not_called()
        check.assert_not_called()
        self.assertTrue(all(row["status"] == "exported" for row in rows))

    def test_exact_export_checkpoint_and_multi_theorem_roots(self):
        item = dict(self.items[0])
        item["theorem_names"] = [item.pop("theorem"), "Extra.goal"]
        dest = self.base / "target"
        dest.mkdir()
        (self.work / "lake-manifest.json").write_bytes((ROOT / "bridge/openai/lake-manifest.json").read_bytes().replace(b"\r\n", b"\n"))
        commands = []

        def export(argv, _cwd, **kwargs):
            commands.append(argv)
            kwargs["stdout"].write(b"export checkpoint\n")

        with patch.object(producer, "run", side_effect=export):
            producer.export_target(self.work, dest, item, self.catalog, {}, True)
        producer.validate_exports(dest, item, self.catalog)
        self.assertEqual(json.loads((dest / "claim.json").read_bytes())["theorem_names"], item["theorem_names"])
        for command in commands:
            self.assertTrue(all(name in command for name in item["theorem_names"]))
        (dest / "solution.ndjson").write_bytes(b"tampered")
        with self.assertRaisesRegex(Rejection, "mismatch"):
            producer.validate_exports(dest, item, self.catalog)
        with patch.object(producer, "run", side_effect=RuntimeError("interrupted")), self.assertRaises(RuntimeError):
            producer.export_target(self.work, dest, item, self.catalog, {}, True)
        self.assertFalse((dest / "provenance.json").exists())

    def test_dynamic_selection_and_nonzero_batch_exit(self):
        self.assertEqual(producer.select_candidates({"candidates": [{"id": "new_target"}]}, ["new_target"]), [{"id": "new_target"}])
        with self.assertRaisesRegex(CatalogError, "available: new_target"):
            producer.select_candidates({"candidates": [{"id": "new_target"}]}, ["unknown"])
        with patch.object(producer, "produce", return_value=[{"status": "rejected"}]):
            self.assertEqual(producer.main(["--phase", "check", "--work", str(self.work), "--out", str(self.out), "--backends", str(self.backends)]), 1)

    def test_custom_local_import_roots_resolve_and_unknown_ones_fail(self):
        (self.work / "Custom").mkdir()
        (self.work / "Custom/Main.lean").write_text("/- import Ignored -/\nimport Mathlib.Data.Nat.Basic\npublic import Custom.Helper -- local\n")
        (self.work / "Custom/Helper.lean").write_text("import Lean\n")
        self.assertEqual(import_roots(self.work, ["Custom.Main"]), ["Mathlib.Data.Nat.Basic"])
        (self.work / "Custom/Helper.lean").write_text("import Missing.Local\n")
        with self.assertRaisesRegex(CatalogError, "unresolved local import: Missing.Local"):
            import_roots(self.work, ["Custom.Main"])

    def test_ambiguous_and_duplicate_theorem_arrays_are_rejected(self):
        for item in ({"theorem_names": []}, {"theorem_names": ["A.x", "A.x"]},
                     {"theorem": "A.x", "theorem_names": ["B.x"]}, {"theorem_names": [None]}):
            with self.subTest(item=item), self.assertRaises(CatalogError):
                theorem_names(item)
