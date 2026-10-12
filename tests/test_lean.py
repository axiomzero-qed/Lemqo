import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lemqo import Rejection
from lemqo.lean import BACKEND_SOURCES, _snapshot, verify_lean_files
from lemqo.lean_export import EXPORT_VERSION, LEAN_GITHASH, LEAN_VERSION
from tests.test_lean_export import encode, records


class LeanOrchestrationTests(unittest.TestCase):
    """Control-flow tests with mocked backends, not logical acceptance tests."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.reference = self.work / "reference.ndjson"
        self.proof = self.work / "proof.ndjson"
        data = encode(records())
        self.reference.write_bytes(data)
        self.proof.write_bytes(data)
        self.claim = self.work / "claim.json"
        self.claim_value = {"format": "lemqo-lean-claim-v1", "name": "demo", "theorem_names": ["Demo.goal"],
                            "permitted_axioms": [], "reference": {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)},
                            "lean_version": LEAN_VERSION, "lean_githash": LEAN_GITHASH, "export_format": EXPORT_VERSION}
        self.claim.write_text(json.dumps(self.claim_value))
        self.binary = self.work / "trusted-test-placeholder"
        self.binary.write_bytes(b"not executable; the runner is mocked")
        entry = {"path": self.binary.name, "sha256": hashlib.sha256(self.binary.read_bytes()).hexdigest()}
        self.backends = self.work / "backends.json"
        self.backends.write_text(json.dumps({"format": "lemqo-lean-backends-v1", "sources": BACKEND_SOURCES,
                                             "binding": entry, "nanoda": entry}))
        self.matched = b'{"status":"matched","theorem_names":["Demo.goal"]}\n'
        self.checked = b"Checked 1 declarations with no errors\n"

    def verify(self):
        return verify_lean_files(self.claim, self.reference, self.proof, self.backends, timeout=5)

    def test_requires_both_exact_success_receipts(self):
        with patch("lemqo.lean.run_backend", side_effect=[self.matched, self.checked]) as runner:
            result = self.verify()
        self.assertEqual(runner.call_count, 2)
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["checked_declarations"], 1)
        self.assertEqual(result["proof_sha256"], hashlib.sha256(self.proof.read_bytes()).hexdigest())

    def test_match_never_substitutes_for_a_proof_check(self):
        for response in (b"", b"Checked 0 declarations with no errors\n",
                         b"Checked 2 declarations with no errors\n",
                         b"Checked 1 declarations with no errors, skipping unpermitted axioms\n",
                         b"Checked 1 declarations with no typechecker errors, 1 pretty printer errors\n"):
            with self.subTest(response=response), patch("lemqo.lean.run_backend", side_effect=[self.matched, response]), self.assertRaises(Rejection):
                self.verify()
        with patch("lemqo.lean.run_backend", side_effect=[self.matched, Rejection("lean-backend", "failed")]), self.assertRaises(Rejection):
            self.verify()

    def test_wrong_target_or_extra_binding_fields_rejected(self):
        for response in (b'{"status":"matched","theorem_names":["other"]}',
                         b'{"status":"matched","theorem_names":["Demo.goal"],"extra":0}',
                         b'{"status":"matched","status":"matched","theorem_names":["Demo.goal"]}'):
            with self.subTest(response=response), patch("lemqo.lean.run_backend", return_value=response) as runner, self.assertRaises(Rejection):
                self.verify()
            self.assertEqual(runner.call_count, 1)

    def test_reference_mismatch_and_malformed_proof_do_not_start_backends(self):
        self.reference.write_bytes(self.reference.read_bytes() + b" ")
        with patch("lemqo.lean.run_backend") as runner, self.assertRaises(Rejection):
            self.verify()
        runner.assert_not_called()
        self.reference.write_bytes(encode(records()))
        self.proof.write_bytes(b"untrusted executable text\n")
        with patch("lemqo.lean.run_backend") as runner, self.assertRaises(Rejection):
            self.verify()
        runner.assert_not_called()

    def test_backend_checksums_enforced(self):
        self.binary.write_bytes(b"changed")
        with patch("lemqo.lean.run_backend") as runner, self.assertRaises(Rejection):
            self.verify()
        runner.assert_not_called()

    def test_both_processes_use_the_identical_private_snapshot(self):
        original = self.proof.read_bytes()
        seen = []

        def respond(_exe, config, directory, _deadline):
            value = json.loads(config.read_bytes())
            path = Path(value.get("solution_file", value.get("export_file_path")))
            self.assertEqual(path.parent, directory)
            self.assertNotEqual(path, self.proof)
            self.assertEqual(path.read_bytes(), original)
            seen.append(path)
            if "solution_file" in value:
                self.proof.write_bytes(b"source changed after copying")
                return self.matched
            self.assertTrue(value["unpermitted_axiom_hard_error"])
            self.assertFalse(value["unsafe_permit_all_axioms"])
            self.assertFalse(value["print_axioms"])
            self.assertEqual(value["permitted_axioms"], [])
            self.assertNotIn("pp_declars", value)
            return self.checked

        with patch("lemqo.lean.run_backend", side_effect=respond):
            result = self.verify()
        self.assertEqual(seen[0], seen[1])
        self.assertFalse(seen[0].exists())
        self.assertEqual(result["proof_sha256"], hashlib.sha256(original).hexdigest())

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX-only input kind")
    def test_fifo_rejected_without_waiting_for_a_writer(self):
        fifo = self.work / "input.fifo"
        os.mkfifo(fifo)
        with self.assertRaises(Rejection):
            _snapshot(fifo, self.work / "copy.ndjson", None)

    def test_invalid_timeout(self):
        for timeout in (True, 0, 7201, 1.5):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                verify_lean_files(self.claim, self.reference, self.proof, self.backends, timeout=timeout)
