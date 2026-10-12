"""Producer/build helpers; never used by the offline verifier."""

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def run(argv, cwd, *, env=None, stdout=None):
    print("Running " + " ".join(str(x) for x in argv[:4]), flush=True)
    subprocess.run([str(x) for x in argv], cwd=cwd, env=env, stdout=stdout, check=True)


def sha256(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def require_lean():
    from lemqo.lean_export import LEAN_GITHASH, LEAN_VERSION
    output = subprocess.check_output(["lean", "--version"], text=True)
    if f"version {LEAN_VERSION}," not in output or LEAN_GITHASH not in output:
        raise RuntimeError("Lean 4.34.1 with the pinned release commit is required")
    return output.strip()


def copy_project(source, destination, files):
    destination.mkdir(parents=True, exist_ok=True)
    for name in files:
        origin = source / name
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        # No timestamps/host paths are inputs to generated proof claims.
        data = origin.read_bytes().replace(b"\r\n", b"\n")
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)


def git_pin(repository, revision, destination):
    destination.mkdir(parents=True, exist_ok=True)
    if not (destination / ".git").is_dir():
        run(["git", "init", "-q"], destination)
        run(["git", "remote", "add", "origin", repository], destination)
        run(["git", "fetch", "--depth=1", "origin", revision], destination)
        run(["git", "checkout", "--detach", "FETCH_HEAD"], destination)
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=destination, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=normal"],
                                    cwd=destination, text=True).strip()
    if actual != revision or dirty:
        raise RuntimeError("backend source is not the clean pinned commit: " + str(destination))


def assert_lake_pins(work, required):
    import json
    lock = json.loads((work / "lake-manifest.json").read_text())
    packages = {x["name"]: x for x in lock["packages"]}
    for name, revision in required.items():
        if packages.get(name, {}).get("rev") != revision:
            raise RuntimeError("Lake dependency pin mismatch: " + name)
    for entry in packages.values():
        if entry["type"] != "git":
            raise RuntimeError("unexpected non-git Lake dependency")
        path = work / ".lake/packages" / entry["name"]
        actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip()
        dirty = subprocess.check_output(["git", "diff", "--name-only", "HEAD", "--"], cwd=path, text=True).strip()
        if actual != entry["rev"] or dirty:
            raise RuntimeError("Lake dependency source differs from lock: " + entry["name"])
