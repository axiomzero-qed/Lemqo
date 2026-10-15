import argparse
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lemqo.mcp import Server, serve
from tests.support import ROOT


def request(method, params=None, ident=1):
    result = {"jsonrpc": "2.0", "method": method, "params": {} if params is None else params}
    if ident is not None:
        result["id"] = ident
    return result


INITIALIZE = request("initialize", {"protocolVersion": "2025-11-25", "clientInfo": {"name": "test", "version": "1"}, "capabilities": {}})
INITIALIZED = request("notifications/initialized", ident=None)


class MCPTests(unittest.TestCase):
    def options(self, **extra):
        return argparse.Namespace(**dict({"ipl_claim": ROOT / "examples/identity.claim.json", "lean_claim": None,
                                         "reference": None, "backends": None, "proof_root": None, "timeout": 5}, **extra))

    def server(self):
        server = Server(self.options())
        server.dispatch(INITIALIZE)
        server.dispatch(INITIALIZED)
        return server

    def test_stdio_handshake_discovery_valid_and_rejected_proofs(self):
        messages = [INITIALIZE, INITIALIZED, request("tools/list", ident=2)]
        for ident, name in ((3, "identity.proof.json"), (4, "identity.invalid.proof.json")):
            messages.append(request("tools/call", {"name": "verify_ipl_proof", "arguments": {
                "proof": (ROOT / "examples" / name).read_text(encoding="utf-8")}}, ident))
        process = subprocess.run([sys.executable, "-m", "lemqo", "mcp", "--ipl-claim", "examples/identity.claim.json"],
                                 cwd=ROOT, input=b"".join(json.dumps(x).encode() + b"\n" for x in messages), capture_output=True, timeout=15)
        self.assertEqual(process.returncode, 0, process.stderr)
        replies = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertEqual(len(replies), 4)
        self.assertEqual(replies[0]["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(replies[1]["result"]["tools"][0]["name"], "verify_ipl_proof")
        self.assertEqual(replies[2]["result"]["structuredContent"]["status"], "valid")
        self.assertFalse(replies[2]["result"]["isError"])
        self.assertTrue(replies[3]["result"]["isError"])
        self.assertEqual(replies[3]["result"]["structuredContent"]["status"], "rejected")
        self.assertEqual(process.stderr, b"")

    def test_claim_or_backend_overrides_are_not_tool_arguments(self):
        server = self.server()
        for arguments in ({"proof": "{}", "claim": "evil"}, {"proof": "{}", "backends": "evil"}, {"proof": {}}, {}):
            reply = server.dispatch(request("tools/call", {"name": "verify_ipl_proof", "arguments": arguments}))
            self.assertEqual(reply["error"]["code"], -32602)
        self.assertIn("error", server.dispatch(request("tools/call", {"name": "verify_lean_certificate"})))

    def test_protocol_errors_notifications_and_no_preinit_execution(self):
        server = Server(self.options())
        self.assertIn("error", server.dispatch(request("tools/list")))
        self.assertIsNone(server.dispatch(INITIALIZED))
        self.assertEqual(server.dispatch(request("ping"))["result"], {})
        self.assertIn("error", server.dispatch([]))
        self.assertEqual(self.server().dispatch(request("unknown"))["error"]["code"], -32601)
        stream, sink = io.BytesIO(b'{"jsonrpc":"2.0","id":1,"id":2,"method":"ping"}\n'), io.BytesIO()
        self.assertEqual(serve(self.options(), stream, sink), 0)
        self.assertEqual(json.loads(sink.getvalue())["error"]["code"], -32700)

    def test_lean_proof_directory_is_enforced_and_trust_inputs_are_fixed(self):
        from tests.test_lean import LeanOrchestrationTests
        fixture = LeanOrchestrationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        server = Server(self.options(lean_claim=fixture.claim, reference=fixture.reference,
                                     backends=fixture.backends, proof_root=fixture.work))
        server.dispatch(INITIALIZE)
        server.dispatch(INITIALIZED)
        for name in ("../outside.ndjson", str(fixture.proof.resolve())):
            with patch("lemqo.mcp.verify_lean_files") as verify:
                result = server.dispatch(request("tools/call", {"name": "verify_lean_certificate", "arguments": {"proof_path": name}}))
            verify.assert_not_called()
            self.assertTrue(result["result"]["isError"])
        with patch("lemqo.mcp.verify_lean_files", return_value={"status": "valid"}) as verify:
            server.dispatch(request("tools/call", {"name": "verify_lean_certificate", "arguments": {"proof_path": fixture.proof.name}}))
        verify.assert_called_once_with(fixture.claim, fixture.reference, fixture.proof.resolve(), fixture.backends, timeout=5)

    def test_oversized_message_ends_session_without_processing_suffix(self):
        with patch("lemqo.mcp.MAX_MESSAGE_BYTES", 10):
            sink = io.BytesIO()
            self.assertEqual(serve(self.options(), io.BytesIO(b"x" * 12 + b"\n"), sink), 2)
        self.assertEqual(json.loads(sink.getvalue())["error"]["code"], -32600)
