"""Build pinned native backends. Requires Linux, Lean 4.34.1, Rust and Git.

Builds are trusted development steps, separate from certificate verification.
No submitted proof controls sources, executable selection or compiler options.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from lean_common import ROOT, assert_lake_pins, copy_project, git_pin, require_lean, run, sha256
from lemqo.lean import BACKEND_SOURCES


def build(work):
    work = work.resolve()
    lean_version = require_lean()
    rust_version = subprocess.check_output(["rustc", "--version"], text=True).strip()
    if not rust_version.startswith("rustc 1.94.0 "):
        raise RuntimeError("Rust 1.94.0 is required for the documented build")
    bridge = work / "bridge"
    source = ROOT / "bridge/lean"
    files = [p.relative_to(source).as_posix() for p in source.rglob("*")
             if p.is_file() and ".lake" not in p.parts and "__pycache__" not in p.parts]
    copy_project(source, bridge, files)
    run(["lake", "build", "lemqo_compare"], bridge)
    assert_lake_pins(bridge, {"Comparator": BACKEND_SOURCES["comparator"], "lean4export": BACKEND_SOURCES["lean4export"]})
    nanoda = work / "nanoda"
    git_pin("https://github.com/ammkrn/nanoda_lib.git", BACKEND_SOURCES["nanoda"], nanoda)
    run(["cargo", "build", "--release", "--locked", "--bin", "nanoda_bin"], nanoda)
    binder = bridge / ".lake/build/bin/lemqo_compare"
    checker = nanoda / "target/release/nanoda_bin"
    config = {"format": "lemqo-lean-backends-v1", "sources": BACKEND_SOURCES,
              "binding": {"path": str(binder), "sha256": sha256(binder)},
              "nanoda": {"path": str(checker), "sha256": sha256(checker)}}
    target = work / "backends.json"
    target.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    provenance = {"lean": lean_version, "rust": rust_version, "sources": BACKEND_SOURCES,
                  "binding_source_sha256": sha256(source / "Main.lean"),
                  "binding_sha256": config["binding"]["sha256"], "nanoda_sha256": config["nanoda"]["sha256"]}
    (work / "build-information.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print("Native backends built: " + str(target))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True, help="dedicated build directory, reused if pinned and clean")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("the native backend build is currently validated on Linux; use WSL on Windows")
    try:
        build(args.work)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print("Backend build failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
