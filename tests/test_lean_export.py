import copy
import json
import tempfile
import time
import unittest
from pathlib import Path

from lemqo import Rejection
from lemqo.lean import read_claim
from lemqo.lean_export import (EXPORT_VERSION, LEAN_GITHASH, LEAN_VERSION,
                              inspect_export, load_json)


def records():
    # Structurally valid; deliberately NOT a logically valid Lean theorem.
    # Real proof checking is tested separately with the actual native backends.
    return [
        {"meta": {"lean": {"version": LEAN_VERSION, "githash": LEAN_GITHASH},
                  "exporter": {"name": "lean4export", "version": EXPORT_VERSION},
                  "format": {"version": EXPORT_VERSION}}},
        {"str": {"pre": 0, "str": "Demo"}, "in": 1},
        {"str": {"pre": 1, "str": "goal"}, "in": 2},
        {"sort": 0, "ie": 0},
        {"thm": {"name": 2, "levelParams": [], "type": 0, "value": 0, "all": [2]}},
    ]


def encode(rows):
    return b"".join(json.dumps(row, separators=(",", ":")).encode() + b"\n" for row in rows)


class LeanExportTests(unittest.TestCase):
    def inspect(self, data, **kwargs):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.ndjson"
            path.write_bytes(data)
            return inspect_export(path, ["Demo.goal"], [], **kwargs)

    def test_preflight_is_structure_only(self):
        result = self.inspect(encode(records()))
        self.assertEqual(result["declarations"], 1)
        self.assertEqual(result["expressions"], 1)
        self.assertEqual(result["records"], 5)
        self.assertNotIn("status", result)

    def test_strict_json(self):
        for data in (b'{"x":1,"x":2}', b'{"x":1.0}', b'{"x":NaN}', b'{"x":-0}',
                     b'{"x":-1}', b'{"x":18446744073709551616}', b'{"x":"\\ud800"}',
                     b'{"x":0} trailing', b'\xef\xbb\xbf{}', b'\xff', b'[' * 17 + b']' * 17):
            with self.subTest(data=data), self.assertRaises(Rejection):
                load_json(data)

    def test_empty_blank_repeated_metadata_and_unknown_tags(self):
        good = encode(records())
        for data in (b"", encode(records()[:1]), b"\n" + good, good + b"\n",
                     good + encode(records()[:1]), good + b'{"mdata":{},"ie":1}\n'):
            with self.subTest(data=data[:30]), self.assertRaises(Rejection):
                self.inspect(data)

    def test_metadata_must_match_all_pins(self):
        for group, key, value in (("lean", "version", "4.35.0"), ("lean", "githash", "0" * 40),
                                  ("exporter", "name", "other"), ("exporter", "version", "3.1.1"),
                                  ("format", "version", "3.0.0")):
            rows = records()
            rows[0]["meta"][group][key] = value
            with self.subTest(group=group, key=key), self.assertRaises(Rejection):
                self.inspect(encode(rows))

    def test_shape_and_graph_mutations(self):
        mutations = [
            (1, "in", True), (1, "in", 2), (1, "extra", 0),
            (3, "sort", 1), (3, "ie", 1), (3, "ie", False),
        ]
        for row, key, value in mutations:
            rows = records()
            rows[row][key] = value
            with self.subTest(row=row, key=key, value=value), self.assertRaises(Rejection):
                self.inspect(encode(rows))
        for key, value in (("type", True), ("value", 1), ("name", 0), ("all", [99]),
                           ("levelParams", [99])):
            rows = records()
            rows[-1]["thm"][key] = value
            with self.subTest(key=key), self.assertRaises(Rejection):
                self.inspect(encode(rows))

    def test_axiom_is_not_a_theorem_and_duplicates_rejected(self):
        rows = records()
        rows[-1] = {"axiom": {"name": 2, "levelParams": [], "type": 0, "isUnsafe": False}}
        with self.assertRaises(Rejection):
            self.inspect(encode(rows))
        with self.assertRaises(Rejection):
            self.inspect(encode(records() + [records()[-1]]))

    def test_unsafe_and_partial_and_unapproved_axioms(self):
        base = {"name": 2, "levelParams": [], "type": 0, "value": 0, "all": [2], "hints": "abbrev"}
        for safety in ("unsafe", "partial"):
            rows = records()[:-1] + [{"def": dict(base, safety=safety)}]
            with self.subTest(safety=safety), self.assertRaises(Rejection):
                self.inspect(encode(rows))
        rows = records() + [{"str": {"pre": 0, "str": "surprise"}, "in": 3},
                            {"axiom": {"name": 3, "levelParams": [], "type": 0, "isUnsafe": False}}]
        with self.assertRaises(Rejection):
            self.inspect(encode(rows))

    def test_deadline(self):
        with self.assertRaises(Rejection) as error:
            self.inspect(encode(records()), deadline=time.monotonic() - 1)
        self.assertEqual(error.exception.code, "lean-timeout")

    def test_claim_policy(self):
        claim = {"format": "lemqo-lean-claim-v1", "name": "demo", "theorem_names": ["Demo.goal"],
                 "permitted_axioms": [], "reference": {"sha256": "1" * 64, "bytes": 1},
                 "lean_version": LEAN_VERSION, "lean_githash": LEAN_GITHASH, "export_format": EXPORT_VERSION}
        self.assertEqual(read_claim(json.dumps(claim).encode()), claim)
        for key, value in (("theorem_names", []), ("theorem_names", ["Demo.goal", "Demo.goal"]),
                           ("theorem_names", ["Classical.choice"]), ("theorem_names", ["a..b"]),
                           ("permitted_axioms", ["sorryAx"]), ("extra", 0),
                           ("reference", {"sha256": "Z" * 64, "bytes": 1})):
            altered = copy.deepcopy(claim)
            altered[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(Rejection):
                read_claim(json.dumps(altered).encode())
