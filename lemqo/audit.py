"""Check receipt/file consistency without executing a proof-checking backend.

A consistent receipt can be forged. This is evidence bookkeeping, not a new
proof check or authentication of the receipt's author or native binaries.
"""

import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

from .errors import Rejection
from .input import _not_integer, _object
from .lean import BACKEND_SOURCES, _read_small, read_claim
from .lean_export import inspect_export


def read_receipt(path):
    try:
        receipt = json.loads(_read_small(path).decode("utf-8", errors="strict"),
                             object_pairs_hook=_object, parse_constant=_not_integer)
    except (UnicodeError, ValueError, RecursionError):
        raise Rejection("receipt-format", "receipt must be strict UTF-8 JSON") from None
    if type(receipt) is not dict:
        raise Rejection("receipt-format", "receipt must be an object")
    return receipt


def audit_receipt(receipt_path, reference_path, solution_path, claim_path):
    """Return 'consistent', never 'valid'; supports v0.2 receipts without timing."""
    receipt = read_receipt(receipt_path)
    claim_bytes = _read_small(claim_path)
    claim = read_claim(claim_bytes)

    def equal(key, value):
        actual = receipt.get(key)
        if type(actual) is not type(value) or actual != value:
            raise Rejection("receipt-mismatch", f"receipt field {key} does not match the supplied evidence")

    for key, expected in {"status": "valid", "verifier": "lemqo", "logic": "lean4",
                          "statement_binding": "matched", "independent_kernel": "nanoda",
                          "claim": claim["name"], "theorem_names": claim["theorem_names"],
                          "permitted_axioms": claim["permitted_axioms"],
                          "claim_sha256": hashlib.sha256(claim_bytes).hexdigest(),
                          "backend_sources": BACKEND_SOURCES}.items():
        equal(key, expected)
    if type(receipt.get("version")) is not str or not receipt["version"]:
        raise Rejection("receipt-format", "missing verifier version")
    for key in ("backend_config_sha256", "binding_sha256", "nanoda_sha256"):
        value = receipt.get(key)
        if type(value) is not str or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise Rejection("receipt-format", f"invalid {key}")
    if "started_at" in receipt or "duration_seconds" in receipt:
        try:
            timestamp = receipt["started_at"]
            duration = receipt["duration_seconds"]
            if type(timestamp) is not str or datetime.fromisoformat(timestamp.replace("Z", "+00:00")).utcoffset() is None:
                raise ValueError()
            if type(duration) not in (int, float) or not math.isfinite(duration) or duration < 0:
                raise ValueError()
        except (KeyError, TypeError, ValueError, OverflowError):
            raise Rejection("receipt-format", "invalid receipt timing metadata") from None
    options = {"targets": claim["theorem_names"], "permitted_axioms": claim["permitted_axioms"]}
    reference = inspect_export(Path(reference_path), reference=True, **options)
    solution = inspect_export(Path(solution_path), **options)
    if any(reference[key] != claim["reference"][key] for key in ("sha256", "bytes")):
        raise Rejection("receipt-mismatch", "reference does not match the caller-selected claim")
    for key, expected in {"reference_sha256": reference["sha256"], "proof_sha256": solution["sha256"],
                          "proof_bytes": solution["bytes"], "proof_records": solution["records"],
                          "checked_declarations": solution["declarations"]}.items():
        equal(key, expected)
    for suffix in ("bytes", "records", "declarations"):
        key = "reference_" + suffix
        if key in receipt:
            equal(key, reference[suffix])
    return {"status": "consistent", "audit": "receipt-file-consistency", "proof_verified": False,
            "claim": claim["name"], "theorem_names": claim["theorem_names"],
            "checked_declarations": solution["declarations"],
            "claim_sha256": receipt["claim_sha256"], "reference_sha256": reference["sha256"],
            "proof_sha256": solution["sha256"],
            "notice": "Hashes and counts match; no Comparator or Nanoda check was run. This does not authenticate the receipt."}
