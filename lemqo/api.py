"""Public bytes-only verification API, with a receipt bound to exact input bytes."""

import hashlib

from . import __version__
from .input import decode
from .kernel import check


def verify_bytes(claim_bytes: bytes, proof_bytes: bytes) -> dict:
    """Return a receipt on acceptance; raise Rejection on rejected input.

    This proves only the claim's formal sequent, subject to the implementation
    trust assumptions in docs/trust.md. Hashes identify inputs, not logical truth.
    """
    claim = decode(claim_bytes)
    proof = decode(proof_bytes)
    used = check(claim, proof)
    return {
        "status": "valid",
        "verifier": "lemqo",
        "version": __version__,
        "logic": "ipl",
        "claim": claim["name"],
        "kind": "conditional" if used else "closed",
        "goal": claim["goal"],
        "declared_premises": claim["premises"],
        "used_premise_indices": used,
        "formula_rows": len(proof["formulas"]),
        "checked_steps": len(proof["steps"]),
        "root": proof["root"],
        "claim_sha256": hashlib.sha256(claim_bytes).hexdigest(),
        "proof_sha256": hashlib.sha256(proof_bytes).hexdigest(),
    }
