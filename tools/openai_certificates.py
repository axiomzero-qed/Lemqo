"""Build and independently check selected, pinned OpenAI main theorems.

This is a trusted producer for the vendored snapshot, not an arbitrary Lean
source service. The public offline verifier is `lemqo check-lean`.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from lean_common import ROOT, assert_lake_pins, copy_project, require_lean, run, sha256
from check_openai_sources import check_catalog
from lemqo import Rejection
from lemqo.lean import BACKEND_SOURCES, verify_lean_files
from lemqo.lean_export import EXPORT_VERSION, LEAN_GITHASH, LEAN_VERSION

MATHLIB = "d13f23b723b8a846827a245b89c10fc7d3f11612"
CORPUS = ROOT / "corpus/openai"


def primitives():
    source = (ROOT / "bridge/lean/Main.lean").read_text(encoding="utf-8")
    match = re.search(r"def primitiveTargets.*?\#\[(.*?)\]", source, re.S)
    if match is None:
        raise RuntimeError("cannot locate the bridge's fixed primitive targets")
    names = re.findall(r"``([A-Za-z_0-9.]+)", match[1])
    if len(names) != 26 or len(set(names)) != len(names):
        raise RuntimeError("unexpected primitive target list")
    return names


def import_roots(work, modules):
    seen, mathlib = set(), set()

    def visit(module):
        if module in seen:
            return
        seen.add(module)
        if module == "Mathlib" or module.startswith("Mathlib."):
            mathlib.add(module)
        elif module.startswith(("OAI.", "ComparatorChallenges.")):
            source = work / (module.replace(".", "/") + ".lean")
            for line in source.read_text(encoding="utf-8").splitlines():
                if line.startswith("import "):
                    for name in line.removeprefix("import ").split():
                        if name.startswith("--"):
                            break
                        visit(name)

    for module in modules:
        visit(module)
    return sorted(mathlib)


def produce(work, output, backends, selected, *, no_cache=False, timeout=1800):
    require_lean()
    check_catalog(ROOT)
    catalog = json.loads((CORPUS / "catalog.json").read_text(encoding="utf-8"))
    candidates = [x for x in catalog["candidates"] if selected is None or x["id"] in selected]
    work, output, backends = work.resolve(), output.resolve(), backends.resolve(strict=True)
    project = ROOT / "bridge/openai"
    copy_project(project, work, ("lakefile.toml", "lean-toolchain", "lake-manifest.json"))
    for entry in catalog["source_files"]:
        source = CORPUS / "lean" / entry["path"]
        target = work / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)
    env = dict(os.environ, MATHLIB_NO_CACHE_ON_UPDATE="1")
    # Building from the checked-in lock instantiates exact transitive revisions.
    run(["lake", "--no-cache", "build", "lean4export"], work, env=env)
    assert_lake_pins(work, {"mathlib": MATHLIB, "lean4export": BACKEND_SOURCES["lean4export"]})
    if not no_cache:
        modules = [x[k] for x in candidates for k in ("challenge_module", "solution_module")]
        run(["lake", "exe", "cache", "get", *import_roots(work, modules)], work, env=env)
    exporter = work / ".lake/packages/lean4export/.lake/build/bin/lean4export"
    for item in candidates:
        started = time.monotonic()
        dest = output / item["id"]
        dest.mkdir(parents=True, exist_ok=True)
        receipt_path = dest / "receipt.json"
        receipt_path.unlink(missing_ok=True)
        failed_path = dest / "failed.json"
        failed_path.unlink(missing_ok=True)
        targets = ["+" + item[k] for k in ("challenge_module", "solution_module")]
        print("Producing main theorem: " + item["theorem"], flush=True)
        run(["lake", "--no-cache", "build", *targets], work, env=env)
        roots = [item["theorem"], *item["permitted_axioms"], *primitives()]
        if "Quot.sound" in item["permitted_axioms"]:
            roots += ["Quot", "Quot.mk", "Quot.lift", "Quot.ind"]
        for label, module in (("reference", item["challenge_module"]), ("solution", item["solution_module"])):
            path = dest / (label + ".ndjson")
            partial = path.with_suffix(".ndjson.partial")
            with partial.open("wb") as sink:
                run(["lake", "env", exporter, module, "--", *roots], work, env=env, stdout=sink)
            partial.replace(path)
        reference = dest / "reference.ndjson"
        claim = {"format": "lemqo-lean-claim-v1", "name": "openai/" + item["id"],
                 "theorem_names": [item["theorem"]], "permitted_axioms": item["permitted_axioms"],
                 "reference": {"sha256": sha256(reference), "bytes": reference.stat().st_size},
                 "lean_version": LEAN_VERSION, "lean_githash": LEAN_GITHASH, "export_format": EXPORT_VERSION}
        claim_path = dest / "claim.json"
        claim_path.write_text(json.dumps(claim, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        provenance = {"upstream_repository": catalog["upstream"]["repository"],
                      "upstream_commit": catalog["upstream"]["commit"], "theorem": item["theorem"],
                      "challenge_module": item["challenge_module"], "solution_module": item["solution_module"],
                      "catalog_sha256": sha256(CORPUS / "catalog.json"), "mathlib_commit": MATHLIB,
                      "lake_manifest_sha256": sha256(work / "lake-manifest.json"),
                      "solution_sha256": sha256(dest / "solution.ndjson"),
                      "reference_sha256": claim["reference"]["sha256"], "mathlib_cache_requested": not no_cache}
        (dest / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
        try:
            receipt = verify_lean_files(claim_path, reference, dest / "solution.ndjson", backends, timeout=timeout)
        except Rejection as error:
            failed_path.write_text(json.dumps({"status": "rejected", "code": error.code, "message": str(error)}, indent=2) + "\n")
            raise
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"VALID {item['id']}: {receipt['checked_declarations']} declarations, {time.monotonic() - started:.1f}s including production", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path, help="dedicated minimal Lake workspace")
    parser.add_argument("--out", required=True, type=Path, help="certificate and receipt output directory")
    parser.add_argument("--backends", required=True, type=Path, help="separately built trusted backend configuration")
    parser.add_argument("--only", action="append", choices=("seymour_second_neighborhood", "cycle_decomposition", "borsuk_nine"))
    parser.add_argument("--no-cache", action="store_true", help="avoid downloading Mathlib build artifacts; use a fresh work directory for a full source rebuild")
    parser.add_argument("--timeout", type=int, default=1800, help="offline verification deadline per theorem, 1–7200 seconds")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("this producer is currently validated on Linux; use WSL on Windows")
    if not 1 <= args.timeout <= 7200:
        parser.error("timeout must be from 1 to 7200 seconds")
    try:
        produce(args.work, args.out, args.backends, args.only, no_cache=args.no_cache, timeout=args.timeout)
    except (OSError, RuntimeError, Rejection, subprocess.CalledProcessError) as error:
        print("Production/check failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
