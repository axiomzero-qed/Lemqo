"""Offline Lean certificate verification using binding plus independent Nanoda.

Claims and backend configurations are caller-selected trusted inputs. Proof
data cannot specify executable paths, options, references, or allowed axioms.
"""

import hashlib
import json
import os
import re
import stat
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .errors import Rejection
from .lean_export import (AXIOMS, EXPORT_VERSION, LEAN_GITHASH, LEAN_VERSION,
                          MAX_EXPORT_BYTES, deadline_check, fields,
                          inspect_export, load_json, names, uint)
from .native import run_backend
from .progress import Heartbeat

BACKEND_SOURCES = {
    "comparator": "d03acab154d269c06e60e4de7e4cc85deebff94b",
    "lean4export": "076e8e57707e813375e8f9da8bf989799ace9680",
    "nanoda": "0f88b5f382f0f3f08aed4af0dd6c0e48c3fd7a44",
}
DIGEST = re.compile(r"[0-9a-f]{64}")


def _digest(value):
    if type(value) is not str or not DIGEST.fullmatch(value):
        raise Rejection("lean-claim", "expected a lowercase SHA256 digest")


def _read_small(path):
    with Path(path).open("rb") as stream:
        data = stream.read(1024 * 1024 + 1)
    if len(data) > 1024 * 1024:
        raise Rejection("lean-limit", "configuration exceeds 1 MiB")
    return data


def read_claim(data):
    claim = load_json(data)
    fields(claim, "format name theorem_names permitted_axioms reference lean_version lean_githash export_format")
    if claim["format"] != "lemqo-lean-claim-v1":
        raise Rejection("lean-claim", "unknown Lean claim format")
    if type(claim["name"]) is not str or not 1 <= len(claim["name"]) <= 128:
        raise Rejection("lean-claim", "invalid claim name")
    names(claim["theorem_names"])
    names(claim["permitted_axioms"], empty=True)
    if any(n not in AXIOMS for n in claim["permitted_axioms"]):
        raise Rejection("lean-axiom", "claim permits an unsupported axiom")
    if any(n in AXIOMS for n in claim["theorem_names"]):
        raise Rejection("lean-target", "an axiom cannot be a theorem target")
    if (claim["lean_version"], claim["lean_githash"], claim["export_format"]) != (
            LEAN_VERSION, LEAN_GITHASH, EXPORT_VERSION):
        raise Rejection("lean-version", "unsupported claim toolchain or format")
    fields(claim["reference"], "sha256 bytes")
    _digest(claim["reference"]["sha256"])
    uint(claim["reference"]["bytes"], MAX_EXPORT_BYTES)
    if claim["reference"]["bytes"] == 0:
        raise Rejection("lean-claim", "empty reference")
    return claim


def _backends(data, directory):
    config = load_json(data)
    fields(config, "format binding nanoda sources")
    if config["format"] != "lemqo-lean-backends-v1" or config["sources"] != BACKEND_SOURCES:
        raise Rejection("lean-backend", "unsupported backend configuration or source pins")
    paths = {}
    for key in ("binding", "nanoda"):
        entry = config[key]
        fields(entry, "path sha256")
        _digest(entry["sha256"])
        if type(entry["path"]) is not str or not entry["path"]:
            raise Rejection("lean-backend", "invalid backend executable path")
        path = (directory / entry["path"]).resolve(strict=True)
        if not path.is_file():
            raise Rejection("lean-backend", "backend must be a regular executable file")
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != entry["sha256"]:
            raise Rejection("lean-backend", "backend executable checksum mismatch")
        paths[key] = path
    return config, paths


def _snapshot(source, destination, deadline):
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(source, flags)
    with os.fdopen(fd, "rb") as stream, destination.open("xb") as output:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise Rejection("lean-input", "certificate inputs must be regular files")
        size = 0
        while chunk := stream.read(1024 * 1024):
            deadline_check(deadline)
            size += len(chunk)
            if size > MAX_EXPORT_BYTES:
                raise Rejection("lean-limit", "export exceeds the byte limit")
            output.write(chunk)
    destination.chmod(0o400)


def _config(path, data):
    path.write_text(json.dumps(data, ensure_ascii=True, separators=(",", ":")), encoding="utf-8")
    path.chmod(0o400)


def verify_lean_files(claim_path, reference_path, proof_path, backends_path, *, timeout=1800,
                      progress=None, progress_interval=10):
    """Return a receipt only after both native checks complete.

    Binaries must be trusted independently of the submitted certificate.
    Source pins in their configuration are build provenance, not attestations.
    """
    if type(timeout) is not int or not 1 <= timeout <= 7200:
        raise ValueError("timeout must be an integer from 1 to 7200 seconds")
    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    with Heartbeat(progress, progress_interval) as heartbeat:
        receipt = _verify_lean_files(claim_path, reference_path, proof_path, backends_path,
                                     started + timeout, heartbeat)
    receipt.update(started_at=started_at, duration_seconds=round(time.monotonic() - started, 3))
    return receipt


def _verify_lean_files(claim_path, reference_path, proof_path, backends_path, deadline, heartbeat):
    claim_bytes = _read_small(claim_path)
    claim = read_claim(claim_bytes)
    backend_bytes = _read_small(backends_path)
    backend, paths = _backends(backend_bytes, Path(backends_path).resolve().parent)
    with tempfile.TemporaryDirectory(prefix="lemqo-lean-") as temp:
        work = Path(temp)
        reference, solution = work / "reference.ndjson", work / "solution.ndjson"
        heartbeat.update("snapshotting certificate inputs")
        _snapshot(reference_path, reference, deadline)
        _snapshot(proof_path, solution, deadline)
        options = dict(targets=claim["theorem_names"], permitted_axioms=claim["permitted_axioms"], deadline=deadline)
        heartbeat.update("preflight reference")
        ref_info = inspect_export(reference, reference=True, **options)
        if any(ref_info[key] != claim["reference"][key] for key in ("sha256", "bytes")):
            raise Rejection("lean-reference", "reference does not match the caller-selected claim")
        heartbeat.update("preflight solution")
        proof_info = inspect_export(solution, **options)
        binding_config = work / "binding.json"
        _config(binding_config, {"reference_file": str(reference), "solution_file": str(solution),
                                 "theorem_names": claim["theorem_names"], "permitted_axioms": claim["permitted_axioms"]})
        heartbeat.update("binding selected statements with Comparator")
        matched = load_json(run_backend(paths["binding"], binding_config, work, deadline))
        if matched != {"status": "matched", "theorem_names": claim["theorem_names"]}:
            raise Rejection("lean-binding", "binding did not confirm the exact selected targets")
        checker_config = work / "nanoda.json"
        _config(checker_config, {"export_file_path": str(solution),
                                 "permitted_axioms": claim["permitted_axioms"],
                                 "unpermitted_axiom_hard_error": True, "unsafe_permit_all_axioms": False,
                                 "nat_extension": True, "string_extension": True,
                                 "num_threads": 1, "print_success_message": True,
                                 "print_axioms": False})
        heartbeat.update(f"Nanoda running on {proof_info['declarations']} declarations (total; completed count unavailable)")
        checked = run_backend(paths["nanoda"], checker_config, work, deadline)
        expected = f"Checked {proof_info['declarations']} declarations with no errors\n".encode("ascii")
        if checked != expected:
            raise Rejection("lean-kernel", "independent checker did not confirm every declaration")
        deadline_check(deadline)
    return {"status": "valid", "verifier": "lemqo", "version": __version__,
            "logic": "lean4", "claim": claim["name"], "theorem_names": claim["theorem_names"],
            "permitted_axioms": claim["permitted_axioms"], "statement_binding": "matched",
            "independent_kernel": "nanoda", "checked_declarations": proof_info["declarations"],
            "claim_sha256": hashlib.sha256(claim_bytes).hexdigest(),
            "reference_sha256": ref_info["sha256"], "proof_sha256": proof_info["sha256"],
            "reference_bytes": ref_info["bytes"], "reference_records": ref_info["records"],
            "reference_declarations": ref_info["declarations"],
            "proof_bytes": proof_info["bytes"], "proof_records": proof_info["records"],
            "backend_config_sha256": hashlib.sha256(backend_bytes).hexdigest(),
            "binding_sha256": backend["binding"]["sha256"], "nanoda_sha256": backend["nanoda"]["sha256"],
            "backend_sources": BACKEND_SOURCES.copy()}
