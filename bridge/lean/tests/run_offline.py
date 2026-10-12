"""Actual-tool regression tests; run under Linux/WSL with pinned tools built.

This is trusted fixture production, never a verifier for supplied Lean source.
All generated exports/configurations stay in the ignored .lake directory.
"""

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


AXIOMS = ["propext", "Classical.choice", "Quot.sound"]
PRIMITIVES = [
    "Nat.add", "Nat.sub", "Nat.mul", "Nat.pow", "Nat.gcd", "Nat.div",
    "Nat.mod", "Nat.beq", "Nat.ble", "Nat.land", "Nat.lor", "Nat.xor",
    "Nat.shiftLeft", "Nat.shiftRight", "String.ofList", "Char.ofNat",
    "List", "eagerReduce", "Nat", "String", "String.mk", "Char",
    "optParam", "autoParam", "semiOutParam", "outParam",
]
TARGET = "LemqoSmoke.target"


def main():
    if not __debug__:
        raise SystemExit("Regression tests require assertions; do not run Python with -O or -OO.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--nanoda", type=Path, required=True)
    parser.add_argument("--lemqo-root", type=Path,
                        help="checkout root containing lemqo/; required for copies outside the checkout")
    args = parser.parse_args()
    bridge = args.bridge_dir.resolve()
    if args.lemqo_root is not None:
        lemqo_root = args.lemqo_root.resolve()
    else:
        candidates = [*Path(__file__).resolve().parents, *bridge.parents]
        lemqo_root = next((path for path in candidates if (path / "lemqo/lean.py").is_file()), None)
    if lemqo_root is None or not (lemqo_root / "lemqo/lean.py").is_file():
        parser.error("cannot locate the Lemqo checkout; provide --lemqo-root")
    sys.path.insert(0, str(lemqo_root))
    import lemqo
    from lemqo.errors import Rejection
    from lemqo.lean import BACKEND_SOURCES, verify_lean_files
    if Path(lemqo.__file__).resolve().parent != (lemqo_root / "lemqo").resolve():
        raise RuntimeError("imported Lemqo from a different checkout")
    nanoda = args.nanoda.resolve(strict=True)
    binder = (bridge / ".lake/build/bin/lemqo_compare").resolve(strict=True)
    exporter = (bridge / ".lake/packages/lean4export/.lake/build/bin/lean4export").resolve(strict=True)
    work = bridge / ".lake/bridge-regressions"
    work.mkdir(exist_ok=True)
    shutil.copyfile(bridge / "tests/Fixture.lean", work / "Fixture.lean")
    env = os.environ.copy()
    leanpath = subprocess.check_output(
        ["lake", "env", "printenv", "LEAN_PATH"], cwd=bridge, text=True, env=env
    ).strip()
    env["LEAN_PATH"] = str(work) + os.pathsep + leanpath
    subprocess.run(
        ["lean", "-o", "Fixture.olean", "Fixture.lean"],
        cwd=work, env=env, check=True, capture_output=True,
    )
    reference = work / "reference.ndjson"
    roots = ["False", TARGET, *AXIOMS, *PRIMITIVES, "Quot", "Quot.mk", "Quot.lift", "Quot.ind"]
    with reference.open("wb") as destination:
        subprocess.run(
            [str(exporter), "Fixture", "--", *roots],
            cwd=work, env=env, check=True, stdout=destination,
        )
    rows = [json.loads(line) for line in reference.read_text().splitlines()]
    names = {0: ""}
    for row in rows:
        if "in" in row:
            value = row.get("str") or row.get("num")
            names[row["in"]] = (
                (names[value["pre"]] + "." if value["pre"] else "")
                + str(value.get("str", value.get("i")))
            )
    false_expr = next(
        row["ie"] for row in rows
        if "const" in row and names[row["const"]["name"]] == "False"
    )
    base_config = {
        "reference_file": str(reference),
        "solution_file": str(reference),
        "theorem_names": [TARGET],
        "permitted_axioms": AXIOMS,
    }
    results = []

    def declaration(data, kind, name):
        return next(row[kind] for row in data if kind in row and names[row[kind]["name"]] == name)

    def write_export(label, data):
        path = work / f"{label}.ndjson"
        path.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in data))
        return path

    def bind(label, data=None, config=None, error=None):
        cfg = copy.deepcopy(base_config if config is None else config)
        if data is not None:
            cfg["solution_file"] = str(write_export(label, data))
        path = work / f"{label}.json"
        path.write_text(json.dumps(cfg))
        process = subprocess.run([str(binder), str(path)], capture_output=True, text=True)
        if error is None:
            assert process.returncode == 0, (label, process.stderr)
            assert json.loads(process.stdout) == {"status": "matched", "theorem_names": [TARGET]}
        else:
            assert process.returncode != 0, (label, "unexpected acceptance")
            assert error in process.stderr, (label, process.stderr)
            assert process.stdout == "", (label, "failure wrote success output")
        results.append({"case": label, "exit_code": process.returncode, "result": "expected"})
        print(f"PASS {label}: exit {process.returncode}")

    bind("good")
    for label, kind, name, field, value, error in [
        ("wrong_type", "thm", TARGET, "type", false_expr, "statement do not match"),
        ("changed_definition", "def", "LemqoSmoke.proposition", "value", false_expr, "Const does not match"),
        ("forged_propext", "axiom", "propext", "type", false_expr, "statement do not match"),
        ("changed_primitive", "def", "Nat.add", "value", "use_type", "Const does not match"),
        ("unsafe_definition", "def", "LemqoSmoke.proposition", "safety", "unsafe", "unsafe or partial"),
        ("partial_definition", "def", "LemqoSmoke.proposition", "safety", "partial", "unsafe or partial"),
    ]:
        data = copy.deepcopy(rows)
        decl = declaration(data, kind, name)
        decl[field] = decl["type"] if value == "use_type" else value
        bind(label, data, error=error)
    for new_kind in ["axiom", "def", "opaque"]:
        data = copy.deepcopy(rows)
        row = next(row for row in data if "thm" in row and names[row["thm"]["name"]] == TARGET)
        old = row.pop("thm")
        new = {key: old[key] for key in ("name", "levelParams", "type")}
        if new_kind != "axiom":
            new.update(value=old["value"], all=old["all"])
        if new_kind == "def":
            new.update(hints="abbrev", safety="safe")
        else:
            new["isUnsafe"] = False
        row[new_kind] = new
        bind(f"{new_kind}_root", data, error="not a theorem")
    for label, kind, name, error in [
        ("missing_root", "thm", TARGET, "not a theorem"),
        ("missing_statement_dependency", "def", "LemqoSmoke.proposition", "Const not found"),
    ]:
        data = [row for row in rows if not (kind in row and names[row[kind]["name"]] == name)]
        bind(label, data, error=error)
    bind("metadata_only", rows[:1], error="no declarations")
    data = copy.deepcopy(rows)
    extra_name = max(names) + 1
    data.append({"in": extra_name, "str": {"pre": 0, "str": "UnexpectedAxiom"}})
    data.append({"axiom": {
        "name": extra_name, "levelParams": [], "type": false_expr, "isUnsafe": False,
    }})
    bind("unused_unapproved_axiom", data, error="unpermitted axiom")
    for label, part, key, value, error in [
        ("unsupported_format", "format", "version", "999.0.0", "unsupported export format"),
        ("unsupported_lean", "lean", "version", "4.35.0", "unsupported Lean toolchain"),
        ("spoof_toolchain_hash", "lean", "githash", "0" * 40, "unsupported Lean toolchain"),
        ("unsupported_exporter", "exporter", "name", "another_exporter", "unsupported exporter"),
    ]:
        data = copy.deepcopy(rows)
        data[0]["meta"][part][key] = value
        bind(label, data, error=error)
    for label, key, value, error in [
        ("empty_targets", "theorem_names", [], "must not be empty"),
        ("duplicate_targets", "theorem_names", [TARGET, TARGET], "duplicate name"),
        ("permit_sorry", "permitted_axioms", [*AXIOMS, "sorryAx"], "not permitted by Lemqo"),
        ("unknown_config_field", "unexpected", 1, "unexpected configuration field"),
    ]:
        config = copy.deepcopy(base_config)
        config[key] = value
        bind(label, config=config, error=error)
    # Well-formed declaration shape, correct statement, invalid proof value.
    broken = copy.deepcopy(rows)
    target = declaration(broken, "thm", TARGET)
    target["value"] = target["type"]
    bind("invalid_proof_same_statement", broken)

    def check_proof(label, export, valid):
        cfg = {
            "export_file_path": str(export), "use_stdin": False,
            "permitted_axioms": AXIOMS, "unpermitted_axiom_hard_error": True,
            "unsafe_permit_all_axioms": False, "nat_extension": True,
            "string_extension": True, "num_threads": 2,
            "print_success_message": True, "print_axioms": False,
        }
        config = work / f"{label}.nanoda.json"
        config.write_text(json.dumps(cfg))
        process = subprocess.run([str(nanoda), str(config)], capture_output=True, text=True)
        assert (process.returncode == 0) == valid, (label, process.stdout, process.stderr)
        if valid:
            count = sum(
                sum(len(row["inductive"][part]) for part in ("types", "ctors", "recs"))
                if "inductive" in row else 1
                for row in rows
                if set(row) & {"thm", "def", "opaque", "axiom", "quot", "inductive"}
            )
            assert process.stdout == f"Checked {count} declarations with no errors\n"
            assert not process.stderr
        results.append({"case": label, "exit_code": process.returncode, "result": "expected"})
        print(f"PASS {label}: Nanoda exit {process.returncode}")

    check_proof("valid_proof", reference, True)
    check_proof("invalid_proof", work / "invalid_proof_same_statement.ndjson", False)

    # The trusted fixture becomes a separately selected expected claim. Its
    # digest is fixed before any mutated solution is sent to the public API.
    def sha256(path):
        with path.open("rb") as source:
            return hashlib.file_digest(source, "sha256").hexdigest()

    metadata = rows[0]["meta"]
    claim = {
        "format": "lemqo-lean-claim-v1", "name": "smoke-real-independent",
        "theorem_names": [TARGET], "permitted_axioms": AXIOMS,
        "reference": {"sha256": sha256(reference), "bytes": reference.stat().st_size},
        "lean_version": metadata["lean"]["version"],
        "lean_githash": metadata["lean"]["githash"],
        "export_format": metadata["format"]["version"],
    }
    claim_path = work / "claim.json"
    claim_path.write_text(json.dumps(claim, indent=2) + "\n")
    backends = {"format": "lemqo-lean-backends-v1", "sources": BACKEND_SOURCES.copy()}
    for name, binary in (("binding", binder), ("nanoda", nanoda)):
        backends[name] = {"path": str(binary), "sha256": sha256(binary)}
    backends_path = work / "backends.json"
    backends_path.write_text(json.dumps(backends, indent=2) + "\n")
    receipt = verify_lean_files(claim_path, reference, reference, backends_path, timeout=60)
    assert receipt["status"] == "valid" and receipt["checked_declarations"] == 585
    assert receipt["theorem_names"] == [TARGET]
    assert receipt["statement_binding"] == "matched" and receipt["independent_kernel"] == "nanoda"
    assert receipt["reference_sha256"] == claim["reference"]["sha256"]
    assert receipt["proof_sha256"] == claim["reference"]["sha256"]
    (work / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    results.append({"case": "api_good", "result": "expected", "checked_declarations": 585})
    print("PASS api_good: valid, 585 declarations")
    for label in ("invalid_proof_same_statement", "changed_definition", "forged_propext", "wrong_type"):
        try:
            verify_lean_files(claim_path, reference, work / f"{label}.ndjson", backends_path, timeout=60)
        except Rejection as error:
            results.append({"case": "api_" + label, "result": "expected", "rejection": error.code})
            print(f"PASS api_{label}: rejected ({error.code})")
        else:
            raise AssertionError(f"public API accepted {label}")
    (work / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"All {len(results)} cases passed; artifacts: {work}")


if __name__ == "__main__":
    main()
