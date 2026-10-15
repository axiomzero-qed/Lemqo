"""Command line interface. Successful output occurs only after full checking."""

import argparse
import json
import sys
from pathlib import Path

from . import Rejection, __version__, verify_bytes
from .limits import MAX_FILE_BYTES
from .lean import verify_lean_files
from .audit import audit_receipt


def _read(path):
    # Read only a bounded prefix even if a file changes size during the read.
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise Rejection("limit", "file exceeds the byte limit")
    return data


def _timeout(text):
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("expected seconds from 1 to 7200") from None
    if not 1 <= value <= 7200:
        raise argparse.ArgumentTypeError("expected seconds from 1 to 7200")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(prog="lemqo", description="Check explicit mathematical proof certificates.")
    parser.add_argument("--version", action="version", version=f"lemqo {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("check", help="verify against a separately supplied claim")
    command.add_argument("proof", help="lemqo-proof-v1 JSON file")
    command.add_argument("--claim", required=True, help="caller-selected lemqo-claim-v1 JSON file")
    command.add_argument("--json", action="store_true", help="emit a machine-readable receipt")
    lean = commands.add_parser("check-lean", help="bind a Lean export and check it independently with Nanoda")
    lean.add_argument("proof", help="complete solution NDJSON export")
    lean.add_argument("--claim", required=True, help="caller-selected lemqo-lean-claim-v1 JSON file")
    lean.add_argument("--reference", required=True, help="trusted reference NDJSON matching the claim's hash")
    lean.add_argument("--backends", required=True, help="caller-selected trusted backend configuration")
    lean.add_argument("--timeout", type=_timeout, default=1800, metavar="SECONDS",
                      help="total verification deadline, 1–7200 seconds (default: 1800)")
    lean.add_argument("--json", action="store_true", help="emit a machine-readable receipt")
    lean.add_argument("--quiet", action="store_true", help="suppress phase and elapsed-time heartbeats on stderr")
    audit = commands.add_parser("audit-receipt", help="check receipt hashes and counts without rerunning the proof check")
    audit.add_argument("receipt", help="existing Lean receipt JSON")
    audit.add_argument("--reference", required=True)
    audit.add_argument("--solution", required=True)
    audit.add_argument("--claim", required=True)
    audit.add_argument("--json", action="store_true")
    mcp = commands.add_parser("mcp", help="run a bounded stdio MCP server with caller-selected trust inputs")
    mcp.add_argument("--ipl-claim", type=Path)
    mcp.add_argument("--lean-claim", type=Path)
    mcp.add_argument("--reference", type=Path)
    mcp.add_argument("--backends", type=Path)
    mcp.add_argument("--proof-root", type=Path, help="directory containing submitted Lean exports")
    mcp.add_argument("--timeout", type=_timeout, default=1800)
    args = parser.parse_args(argv)
    if args.command == "mcp":
        from .mcp import serve
        lean_inputs = (args.lean_claim, args.reference, args.backends, args.proof_root)
        if any(lean_inputs) and not all(lean_inputs):
            parser.error("Lean MCP tools require --lean-claim, --reference, --backends and --proof-root")
        if args.ipl_claim is None and args.lean_claim is None:
            parser.error("MCP requires --ipl-claim or the four Lean trust inputs")
        try:
            return serve(args)
        except (OSError, Rejection, ValueError) as error:
            print(f"ERROR [mcp] {error}", file=sys.stderr)
            return 2
    try:
        if args.command == "check-lean":
            progress = None if args.quiet else lambda message: print("[lemqo] " + message, file=sys.stderr, flush=True)
            receipt = verify_lean_files(args.claim, args.reference, args.proof, args.backends,
                                        timeout=args.timeout, progress=progress)
        elif args.command == "audit-receipt":
            receipt = audit_receipt(args.receipt, args.reference, args.solution, args.claim)
        else:
            receipt = verify_bytes(_read(args.claim), _read(args.proof))
    except Rejection as error:
        if args.json:
            print(json.dumps({"status": "rejected", "code": error.code, "message": str(error)},
                             sort_keys=True), file=sys.stderr)
        else:
            print(f"REJECTED [{error.code}] {error}", file=sys.stderr)
        return 1
    except OSError:
        print("ERROR [io] could not read an input file", file=sys.stderr)
        return 2
    except Exception as error:
        # Includes environmental resource failures. Never turn an error into VALID.
        print(f"ERROR [internal] {type(error).__name__}; verification did not complete", file=sys.stderr)
        return 3
    # Printing the supplied bounded tree avoids expanding the certificate DAG.
    if args.json:
        print(json.dumps(receipt, sort_keys=True, ensure_ascii=True, separators=(",", ":")))
    elif args.command == "audit-receipt":
        print(f"CONSISTENT {receipt['claim']} ({receipt['checked_declarations']} declarations; hashes and counts match)")
        print(receipt["notice"])
    elif args.command == "check-lean":
        print(f"VALID {receipt['claim']} (Lean statement matched; Nanoda checked {receipt['checked_declarations']} declarations)")
        print("Theorems: " + json.dumps(receipt["theorem_names"]))
        print("Permitted axioms: " + json.dumps(receipt["permitted_axioms"]))
    else:
        print(f"VALID {receipt['claim']} ({receipt['kind']}; {receipt['checked_steps']} checked steps)")
        print("Goal: " + json.dumps(receipt["goal"]))
        print("Declared premises: " + json.dumps(receipt["declared_premises"]))
        print("Used premise indices: " + json.dumps(receipt["used_premise_indices"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
