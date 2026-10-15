"""Build, export, and independently check pinned OpenAI theorem targets.

Each target is recorded independently. A failed batch exits nonzero after all
selected targets have been attempted. The public verifier is check-lean.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.lean_common import ROOT, assert_lake_pins, copy_project, require_lean, run, sha256
from tools.check_openai_sources import CatalogError, check_catalog, import_roots, theorem_names
from lemqo import Rejection
from lemqo.audit import audit_receipt, read_receipt
from lemqo.lean import BACKEND_SOURCES, _backends, _read_small, read_claim, verify_lean_files
from lemqo.lean_export import EXPORT_VERSION, LEAN_GITHASH, LEAN_VERSION

MATHLIB = "d13f23b723b8a846827a245b89c10fc7d3f11612"
CORPUS = ROOT / "corpus/openai"


def write_json(path, value):
    """Replace a complete checkpoint atomically."""
    partial = path.with_name(path.name + ".partial")
    with partial.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    partial.replace(path)


def primitives():
    source = (ROOT / "bridge/lean/Main.lean").read_text(encoding="utf-8")
    match = re.search(r"def primitiveTargets.*?\#\[(.*?)\]", source, re.S)
    if match is None:
        raise RuntimeError("cannot locate the bridge's fixed primitive targets")
    names = re.findall(r"``([A-Za-z_0-9.]+)", match[1])
    if len(names) != 26 or len(set(names)) != len(names):
        raise RuntimeError("unexpected primitive target list")
    return names


def select_candidates(catalog, selected):
    available = [item["id"] for item in catalog["candidates"]]
    unknown = set(selected or ()) - set(available)
    if unknown:
        raise CatalogError("unknown target(s): " + ", ".join(sorted(unknown))
                           + "; available: " + ", ".join(available))
    return [item for item in catalog["candidates"] if selected is None or item["id"] in selected]


def prepare_project(work, catalog):
    require_lean()
    copy_project(ROOT / "bridge/openai", work, ("lakefile.toml", "lean-toolchain", "lake-manifest.json"))
    for entry in catalog["source_files"]:
        source = CORPUS / "lean" / entry["path"]
        target = work / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)


def build_target(work, item, env):
    targets = ["+" + item[key] for key in ("challenge_module", "solution_module")]
    run(["lake", "--no-cache", "build", *targets], work, env=env)


def make_claim(item, reference):
    return {"format": "lemqo-lean-claim-v1", "name": "openai/" + item["id"],
            "theorem_names": theorem_names(item), "permitted_axioms": item["permitted_axioms"],
            "reference": {"sha256": sha256(reference), "bytes": reference.stat().st_size},
            "lean_version": LEAN_VERSION, "lean_githash": LEAN_GITHASH, "export_format": EXPORT_VERSION}


def export_target(work, dest, item, catalog, env, no_cache):
    exporter = work / ".lake/packages/lean4export/.lake/build/bin/lean4export"
    roots = list(dict.fromkeys([*theorem_names(item), *item["permitted_axioms"], *primitives()]))
    if "Quot.sound" in item["permitted_axioms"]:
        roots += ["Quot", "Quot.mk", "Quot.lift", "Quot.ind"]
    # Provenance commits a complete pair. Invalidate it before changing files.
    (dest / "provenance.json").unlink(missing_ok=True)
    for label, module in (("reference", item["challenge_module"]), ("solution", item["solution_module"])):
        path = dest / (label + ".ndjson")
        partial = path.with_suffix(".ndjson.partial")
        with partial.open("wb") as sink:
            run(["lake", "env", exporter, module, "--", *roots], work, env=env, stdout=sink)
            sink.flush()
            os.fsync(sink.fileno())
        partial.replace(path)
    write_json(dest / "claim.json", make_claim(item, dest / "reference.ndjson"))
    write_json(dest / "provenance.json", {
        "format": "lemqo-openai-production-v1", "upstream_repository": catalog["upstream"]["repository"],
        "upstream_commit": catalog["upstream"]["commit"], "theorem_names": theorem_names(item),
        "challenge_module": item["challenge_module"], "solution_module": item["solution_module"],
        "catalog_sha256": sha256(CORPUS / "catalog.json"), "mathlib_commit": MATHLIB,
        "lake_manifest_sha256": sha256(work / "lake-manifest.json"), "claim_sha256": sha256(dest / "claim.json"),
        "solution_sha256": sha256(dest / "solution.ndjson"), "reference_sha256": sha256(dest / "reference.ndjson"),
        "mathlib_cache_requested": not no_cache})


def validate_exports(dest, item, catalog):
    """Reuse only a complete checkpoint bound to this catalog and exact bytes."""
    try:
        provenance = json.loads(_read_small(dest / "provenance.json"))
        claim = read_claim(_read_small(dest / "claim.json"))
        expected = {"format": "lemqo-openai-production-v1", "catalog_sha256": sha256(CORPUS / "catalog.json"),
                    "upstream_repository": catalog["upstream"]["repository"],
                    "upstream_commit": catalog["upstream"]["commit"], "mathlib_commit": MATHLIB,
                    "challenge_module": item["challenge_module"], "solution_module": item["solution_module"],
                    "theorem_names": theorem_names(item), "claim_sha256": sha256(dest / "claim.json"),
                    "solution_sha256": sha256(dest / "solution.ndjson"),
                    "reference_sha256": sha256(dest / "reference.ndjson"),
                    "lake_manifest_sha256": hashlib.sha256((ROOT / "bridge/openai/lake-manifest.json").read_bytes().replace(b"\r\n", b"\n")).hexdigest()}
        if type(provenance) is not dict or any(provenance.get(key) != value for key, value in expected.items()):
            raise ValueError("provenance or file hash mismatch")
        if claim != make_claim(item, dest / "reference.ndjson"):
            raise ValueError("claim does not match the selected target and reference")
    except (OSError, ValueError, Rejection) as error:
        raise Rejection("producer-exports", f"cannot reuse exports for {item['id']}: {error}") from None


def resume_receipt(dest, backends):
    receipt = read_receipt(dest / "receipt.json")
    config_bytes = _read_small(backends)
    config, _ = _backends(config_bytes, backends.parent)
    expected = {"backend_config_sha256": hashlib.sha256(config_bytes).hexdigest(),
                "binding_sha256": config["binding"]["sha256"], "nanoda_sha256": config["nanoda"]["sha256"]}
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise Rejection("producer-resume", "backend configuration differs from the previous receipt")
    audit_receipt(dest / "receipt.json", dest / "reference.ndjson", dest / "solution.ndjson", dest / "claim.json")
    return receipt


def check_target(dest, backends, timeout):
    return verify_lean_files(dest / "claim.json", dest / "reference.ndjson", dest / "solution.ndjson", backends,
                             timeout=timeout, progress=lambda text: print("[lemqo] " + text, file=sys.stderr, flush=True))


def produce(work, output, backends, selected, *, no_cache=False, timeout=1800,
            phase="all", reuse_exports=False, resume=False):
    if phase not in ("all", "build", "export", "check"):
        raise ValueError("unknown production phase")
    if type(timeout) is not int or not 1 <= timeout <= 7200:
        raise ValueError("timeout must be from 1 to 7200 seconds")
    check_catalog(ROOT)
    catalog = json.loads((CORPUS / "catalog.json").read_text(encoding="utf-8"))
    candidates = select_candidates(catalog, selected)
    work, output = work.resolve(), output.resolve()
    if phase in ("all", "check"):
        if backends is None:
            raise ValueError("--backends is required for checking")
        backends = backends.resolve(strict=True)
    output.mkdir(parents=True, exist_ok=True)
    ready = False
    env = dict(os.environ, MATHLIB_NO_CACHE_ON_UPDATE="1")
    rows = []
    for item in candidates:
        started = time.monotonic()
        dest = output / item["id"]
        dest.mkdir(parents=True, exist_ok=True)
        row = {"id": item["id"], "phase": phase, "status": "error", "checked_declarations": None}
        try:
            cached = False
            if phase == "check" or (phase in ("all", "export") and (reuse_exports or resume)):
                try:
                    validate_exports(dest, item, catalog)
                    cached = True
                except Rejection:
                    if phase == "check":
                        raise
            receipt = None
            if cached and resume and phase in ("all", "check"):
                try:
                    receipt = resume_receipt(dest, backends)
                except (OSError, Rejection):
                    pass
            if receipt is not None:
                row.update(status="reused", checked_declarations=receipt["checked_declarations"])
            else:
                (dest / "receipt.json").unlink(missing_ok=True)
                if not cached and phase != "check":
                    if not ready:
                        prepare_project(work, catalog)
                        if phase in ("all", "build"):
                            run(["lake", "--no-cache", "build", "lean4export"], work, env=env)
                        assert_lake_pins(work, {"mathlib": MATHLIB, "lean4export": BACKEND_SOURCES["lean4export"]})
                        ready = True
                    if phase in ("all", "build"):
                        if not no_cache:
                            modules = [item[key] for key in ("challenge_module", "solution_module")]
                            run(["lake", "exe", "cache", "get", *import_roots(work, modules)], work, env=env)
                        build_target(work, item, env)
                    if phase in ("all", "export"):
                        export_target(work, dest, item, catalog, env, no_cache)
                if phase in ("all", "check"):
                    receipt = check_target(dest, backends, timeout)
                    write_json(dest / "receipt.json", receipt)
                    row.update(status="valid", checked_declarations=receipt["checked_declarations"])
                else:
                    row["status"] = "built" if phase == "build" else "exported"
            (dest / "failed.json").unlink(missing_ok=True)
        except Exception as error:
            (dest / "receipt.json").unlink(missing_ok=True)
            code = error.code if isinstance(error, Rejection) else "producer-error"
            row.update(status="rejected" if isinstance(error, Rejection) else "error", code=code, message=str(error))
        row["duration_seconds"] = round(time.monotonic() - started, 3)
        if row["status"] in ("error", "rejected"):
            write_json(dest / "failed.json", row)
        rows.append(row)
        write_json(output / "batch-summary.json", {"format": "lemqo-batch-v1", "phase": phase, "targets": rows})
        print(f"{row['id']}: {row['status']} | declarations={row['checked_declarations']} | {row['duration_seconds']:.1f}s", flush=True)
        if "message" in row:
            print(f"  [{row['code']}] {row['message']}", file=sys.stderr, flush=True)
    print("\nID | RESULT | DECLARATIONS | SECONDS", flush=True)
    for row in rows:
        print(f"{row['id']} | {row['status']} | {row['checked_declarations']} | {row['duration_seconds']:.1f}", flush=True)
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path, help="dedicated Lake workspace (unused by check)")
    parser.add_argument("--out", required=True, type=Path, help="certificate and receipt output directory")
    parser.add_argument("--backends", type=Path, help="trusted backend configuration; required by all/check")
    parser.add_argument("--only", action="append", help="catalog target id; repeat for multiple targets")
    parser.add_argument("--phase", choices=("all", "build", "export", "check"), default="all")
    parser.add_argument("--reuse-exports", action="store_true", help="reuse catalog/claim/hash-matching exports")
    parser.add_argument("--resume", action="store_true", help="reuse matching exports and audited success receipts with the same backends")
    parser.add_argument("--no-cache", action="store_true", help="avoid Mathlib artifact downloads")
    parser.add_argument("--timeout", type=int, default=1800, help="verification deadline per target, 1–7200 seconds; use 7200 for heavy targets")
    args = parser.parse_args(argv)
    if args.phase != "check" and sys.platform != "linux":
        parser.error("build/export are currently validated on Linux; use WSL on Windows")
    if not 1 <= args.timeout <= 7200:
        parser.error("timeout must be from 1 to 7200 seconds")
    if args.phase in ("all", "check") and args.backends is None:
        parser.error("--backends is required for all/check")
    try:
        rows = produce(args.work, args.out, args.backends, args.only, no_cache=args.no_cache,
                       timeout=args.timeout, phase=args.phase, reuse_exports=args.reuse_exports, resume=args.resume)
    except (OSError, RuntimeError, ValueError, CatalogError, Rejection, subprocess.CalledProcessError) as error:
        print("Production/check failed: " + str(error), file=sys.stderr)
        return 1
    return int(any(row["status"] in ("error", "rejected") for row in rows))


if __name__ == "__main__":
    raise SystemExit(main())
