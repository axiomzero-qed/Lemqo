"""Command line interface. Successful output occurs only after full checking."""

import argparse
import json
import sys
from pathlib import Path

from . import Rejection, __version__, verify_bytes
from .limits import MAX_FILE_BYTES


def _read(path):
    # Read only a bounded prefix even if a file changes size during the read.
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise Rejection("limit", "file exceeds the byte limit")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(prog="lemqo", description="Check explicit IPL proof certificates.")
    parser.add_argument("--version", action="version", version=f"lemqo {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("check", help="verify against a separately supplied claim")
    command.add_argument("proof", help="lemqo-proof-v1 JSON file")
    command.add_argument("--claim", required=True, help="caller-selected lemqo-claim-v1 JSON file")
    command.add_argument("--json", action="store_true", help="emit a machine-readable receipt")
    args = parser.parse_args(argv)
    try:
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
    else:
        print(f"VALID {receipt['claim']} ({receipt['kind']}; {receipt['checked_steps']} checked steps)")
        print("Goal: " + json.dumps(receipt["goal"]))
        print("Declared premises: " + json.dumps(receipt["declared_premises"]))
        print("Used premise indices: " + json.dumps(receipt["used_premise_indices"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
