import contextlib
import io
import json
import unittest
from unittest.mock import patch

from lemqo import Rejection
from lemqo.__main__ import main
from lemqo.audit import audit_receipt
from tests import test_lean


class ReceiptAuditTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_lean.LeanOrchestrationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        with patch("lemqo.lean.run_backend", side_effect=[self.fixture.matched, self.fixture.checked]):
            self.receipt = self.fixture.verify()
        self.path = self.fixture.work / "receipt.json"
        self.write()

    def write(self):
        self.path.write_text(json.dumps(self.receipt), encoding="utf-8")

    def audit(self):
        f = self.fixture
        return audit_receipt(self.path, f.reference, f.proof, f.claim)

    def test_consistency_does_not_call_a_backend_or_claim_proof_validity(self):
        with patch("lemqo.lean.run_backend") as backend:
            result = self.audit()
        backend.assert_not_called()
        self.assertEqual(result["status"], "consistent")
        self.assertIs(result["proof_verified"], False)
        self.assertGreaterEqual(self.receipt["duration_seconds"], 0)
        self.assertTrue(self.receipt["started_at"].endswith("Z"))

    def test_v02_receipts_without_new_fields_remain_auditable(self):
        for key in ("started_at", "duration_seconds", "reference_bytes", "reference_records", "reference_declarations"):
            self.receipt.pop(key)
        self.receipt["version"] = "0.2.0"
        self.write()
        self.assertEqual(self.audit()["status"], "consistent")

    def test_rejects_each_mismatched_evidence_field(self):
        original = self.receipt.copy()
        for key, value in (("status", "rejected"), ("claim", "other"), ("theorem_names", ["Other.goal"]),
                           ("permitted_axioms", ["propext"]), ("proof_sha256", "0" * 64),
                           ("reference_sha256", "0" * 64), ("claim_sha256", "0" * 64),
                           ("checked_declarations", True), ("proof_bytes", 0), ("proof_records", 0),
                           ("reference_declarations", 0), ("independent_kernel", "other")):
            with self.subTest(key=key):
                self.receipt = dict(original, **{key: value})
                self.write()
                with self.assertRaises(Rejection):
                    self.audit()

    def test_tampered_files_and_invalid_timing_fail(self):
        self.fixture.proof.write_bytes(self.fixture.proof.read_bytes() + b" ")
        with self.assertRaises(Rejection):
            self.audit()
        self.fixture.proof.write_bytes(self.fixture.reference.read_bytes())
        for value in (-1, True, float("inf")):
            self.receipt["duration_seconds"] = value
            self.write()
            with self.assertRaises(Rejection):
                self.audit()

    def test_cli_never_prints_valid(self):
        f = self.fixture
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = main(["audit-receipt", str(self.path), "--reference", str(f.reference),
                           "--solution", str(f.proof), "--claim", str(f.claim)])
        self.assertEqual(status, 0)
        self.assertIn("CONSISTENT", output.getvalue())
        self.assertNotIn("VALID", output.getvalue())
