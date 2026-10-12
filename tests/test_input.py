import unittest

from lemqo import Rejection, verify_bytes
from lemqo.input import decode
from lemqo.limits import MAX_FILE_BYTES
from tests.support import encoded, example


class InputTests(unittest.TestCase):
    def rejected(self, raw, code=None):
        with self.assertRaises(Rejection) as caught:
            decode(raw)
        if code:
            self.assertEqual(caught.exception.code, code)

    def test_duplicate_keys_at_every_level(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":{"a":1,"a":1}}',
                    b'{"format":1,"form\\u0061t":2}'):
            self.rejected(raw, "json")

    def test_numbers_are_not_coerced(self):
        for raw in (b"1.0", b"1e0", b"NaN", b"Infinity", b"-Infinity", b"-0"):
            self.rejected(raw, "json")
        self.rejected(b"1234567890", "limit")

    def test_strict_utf8_and_unicode(self):
        for raw in (b'"\xff"', b'"\xc0\xaf"', b'"\\ud800"', b'"\\udfff"', b'\xef\xbb\xbf{}'):
            self.rejected(raw, "json")
        self.assertEqual(decode(b'"\\ud83d\\ude00"'), "😀")

    def test_depth_guard_ignores_quoted_brackets_and_escapes(self):
        self.assertEqual(decode(encoded("[" * 100)), "[" * 100)
        self.assertEqual(decode(encoded('"\\[{}]')), '"\\[{}]')
        self.rejected(b"[" * 97 + b"0" + b"]" * 97, "limit")

    def test_large_inputs_rejected_before_parsing(self):
        self.rejected(b" " * (MAX_FILE_BYTES + 1), "limit")
        self.rejected(encoded("x" * 129), "limit")
        self.rejected(b"[" + b"0," * 200000 + b"0]", "limit")

    def test_malformed_json_and_trailing_data(self):
        for raw in (b"", b"{}{}", b"[] 1", b"{", b"[}", b"[1,]", b'"unterminated',
                    b'{"x":1,}', b"// comment\n{}", b'"\\x00"', b"+1", b"01"):
            self.rejected(raw, "json")

    def test_bytes_only_public_api(self):
        with self.assertRaises(TypeError):
            verify_bytes("{}", b"{}")

    def test_both_documents_use_strict_parser(self):
        c, p = encoded(example("identity", "claim")), encoded(example("identity", "proof"))
        for cc, pp in ((c[:-1] + b',"logic":"ipl"}', p), (c, p[:-1] + b',"root":1}')):
            with self.assertRaises(Rejection):
                verify_bytes(cc, pp)

    def test_escaped_identifiers_have_same_decoded_identity(self):
        c, p = encoded(example("identity", "claim")), encoded(example("identity", "proof"))
        verify_bytes(c.replace(b'"P"', b'"\\u0050"'), p)

    def test_deterministic_random_bytes_fail_closed(self):
        import random
        rng = random.Random(20261012)
        valid_claim = encoded(example("identity", "claim"))
        for _ in range(500):
            raw = bytes(rng.randrange(256) for _ in range(rng.randrange(1, 200)))
            try:
                verify_bytes(valid_claim, raw)
            except Rejection:
                pass
            else:
                self.fail("random malformed certificate was accepted")
