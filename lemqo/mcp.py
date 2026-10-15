"""Small, sequential MCP stdio reference server, with no runtime dependencies.

Only proof data is tool-selected. Claims, references, backends, proof directory
and deadlines are selected by the operator at startup. Long batch checks are
better run with the phase-based producer. No HTTP, shell, or remote fetching.
"""

import json
import math
import sys
from pathlib import Path

from . import Rejection, __version__, verify_bytes
from .input import _object
from .lean import _read_small, read_claim, verify_lean_files
from .limits import MAX_FILE_BYTES

PROTOCOLS = ("2025-11-25", "2025-06-18", "2025-03-26")
MAX_MESSAGE_BYTES = 8 * 1024 * 1024


class RPCError(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message


def _integer(text):
    if len(text) > 20:
        raise ValueError("integer too large")
    return int(text)


def _float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("non-finite number")
    return value


def _constant(_):
    raise ValueError("non-finite number")


class Server:
    def __init__(self, options):
        self.options = options
        self.initialized = False
        self.negotiated = False
        self.ipl_claim = None
        self.tools = []
        if options.ipl_claim is not None:
            with Path(options.ipl_claim).open("rb") as stream:
                self.ipl_claim = stream.read(MAX_FILE_BYTES + 1)
            if len(self.ipl_claim) > MAX_FILE_BYTES:
                raise ValueError("IPL claim exceeds the byte limit")
            self.tools.append(self._tool("verify_ipl_proof", "Check a proof against the operator-selected IPL claim.", "proof"))
        if options.lean_claim is not None:
            read_claim(_read_small(options.lean_claim))
            self.proof_root = options.proof_root.resolve(strict=True)
            if not self.proof_root.is_dir():
                raise ValueError("proof root must be a directory")
            self.tools.append(self._tool("verify_lean_certificate", "Check a Lean NDJSON file under the operator-selected proof root, using fixed trust inputs.", "proof_path"))

    @staticmethod
    def _tool(name, description, argument):
        return {"name": name, "description": description,
                "inputSchema": {"type": "object", "properties": {argument: {"type": "string"}},
                                "required": [argument], "additionalProperties": False},
                "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False}}

    def call_tool(self, params):
        if set(params) - {"name", "arguments", "_meta"}:
            raise RPCError(-32602, "unexpected tool call fields")
        tool = next((tool for tool in self.tools if tool["name"] == params.get("name")), None)
        if tool is None:
            raise RPCError(-32602, "unknown or unconfigured tool")
        arguments = params.get("arguments", {})
        key = tool["inputSchema"]["required"][0]
        if type(arguments) is not dict or set(arguments) != {key} or type(arguments[key]) is not str:
            raise RPCError(-32602, f"expected only the string argument {key}")
        try:
            if key == "proof":
                receipt = verify_bytes(self.ipl_claim, arguments[key].encode("utf-8"))
            else:
                submitted = Path(arguments[key])
                if submitted.is_absolute() or submitted.drive or ".." in submitted.parts:
                    raise Rejection("mcp-path", "proof_path must be relative to the configured proof root")
                proof = (self.proof_root / submitted).resolve(strict=True)
                if not proof.is_relative_to(self.proof_root) or not proof.is_file():
                    raise Rejection("mcp-path", "proof_path escapes the configured proof root or is not a file")
                receipt = verify_lean_files(self.options.lean_claim, self.options.reference, proof,
                                            self.options.backends, timeout=self.options.timeout)
        except Rejection as error:
            receipt = {"status": "rejected", "code": error.code, "message": str(error)}
        except (OSError, UnicodeError):
            receipt = {"status": "error", "code": "io", "message": "could not read a proof input"}
        except Exception as error:
            receipt = {"status": "error", "code": "internal",
                       "message": f"{type(error).__name__}; verification did not complete"}
        return {"content": [{"type": "text", "text": json.dumps(receipt, ensure_ascii=True)}],
                "structuredContent": receipt, "isError": receipt.get("status") != "valid"}

    def dispatch(self, message):
        ident = None
        try:
            if type(message) is not dict or message.get("jsonrpc") != "2.0" or type(message.get("method")) is not str:
                raise RPCError(-32600, "invalid JSON-RPC request")
            if "id" in message:
                if type(message["id"]) not in (str, int):
                    raise RPCError(-32600, "request id must be a string or integer")
                ident = message["id"]
            else:
                if message["method"] == "notifications/initialized" and self.negotiated:
                    self.initialized = True
                return None
            params = message.get("params", {})
            if type(params) is not dict:
                raise RPCError(-32602, "params must be an object")
            method = message["method"]
            if method == "initialize":
                if self.negotiated or type(params.get("protocolVersion")) is not str or type(params.get("clientInfo")) is not dict or type(params.get("capabilities")) is not dict:
                    raise RPCError(-32602, "invalid or repeated initialization")
                self.negotiated = True
                requested = params["protocolVersion"]
                result = {"protocolVersion": requested if requested in PROTOCOLS else PROTOCOLS[0],
                          "capabilities": {"tools": {"listChanged": False}},
                          "serverInfo": {"name": "lemqo", "version": __version__},
                          "instructions": "Trust inputs are fixed by the operator. Submit only proof data. Rejection does not establish that a claim is false."}
            elif method == "ping":
                result = {}
            elif not self.initialized:
                raise RPCError(-32600, "complete initialization before calling tools")
            elif method == "tools/list":
                result = {"tools": self.tools}
            elif method == "tools/call":
                result = self.call_tool(params)
            else:
                raise RPCError(-32601, "method not found")
            return {"jsonrpc": "2.0", "id": ident, "result": result}
        except RPCError as error:
            return {"jsonrpc": "2.0", "id": ident, "error": {"code": error.code, "message": error.message}}


def serve(options, source=None, sink=None):
    server = Server(options)
    source = sys.stdin.buffer if source is None else source
    sink = sys.stdout.buffer if sink is None else sink
    while line := source.readline(MAX_MESSAGE_BYTES + 1):
        if len(line) > MAX_MESSAGE_BYTES:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "message exceeds 8 MiB"}}
        else:
            try:
                message = json.loads(line.decode("utf-8", errors="strict"), object_pairs_hook=_object,
                                     parse_int=_integer, parse_float=_float, parse_constant=_constant)
                reply = server.dispatch(message)
            except (ValueError, UnicodeError, RecursionError, Rejection):
                reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "invalid strict UTF-8 JSON"}}
        if reply is not None:
            sink.write(json.dumps(reply, ensure_ascii=True, separators=(",", ":")).encode("utf-8") + b"\n")
            sink.flush()
        if len(line) > MAX_MESSAGE_BYTES:
            return 2
    return 0
