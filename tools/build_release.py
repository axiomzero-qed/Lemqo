"""Build byte-reproducible, dependency-free source and runnable ZIP archives.

Only the explicit source allowlist is packaged. No git history, local virtual
environment, build output, or arbitrary workspace files are included.
"""

import argparse
import hashlib
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lemqo import __version__  # noqa: E402

ROOT_FILES = (
    "README.md", "LICENSE", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
    "SECURITY.md", "CHANGELOG.md", "THIRD_PARTY.md", "pyproject.toml", "MANIFEST.in",
    ".gitignore", ".gitattributes",
)
SOURCE_DIRS = ("lemqo", "docs", "examples", "tests", "tools", ".github", "bridge", "corpus")
EXTENSIONS = {".py", ".md", ".json", ".yml", ".yaml", ".toml", ".ndjson", ".lean"}
EXTENSIONLESS_FILES = {"LICENSE", "lean-toolchain", ".gitignore"}
EXCLUDED_DIRS = {
    ".git", ".lake", "__pycache__", ".cache", "cache", "caches",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", ".venv",
    "venv", "node_modules", "build", "dist",
}


def source_files():
    files = [ROOT / name for name in ROOT_FILES]
    for directory in SOURCE_DIRS:
        for current, dirs, names in os.walk(ROOT / directory):
            dirs[:] = [name for name in dirs
                       if name.casefold() not in EXCLUDED_DIRS
                       and not name.casefold().endswith(".egg-info")]
            for name in names:
                path = Path(current) / name
                if name in EXTENSIONLESS_FILES or path.suffix.lower() in EXTENSIONS:
                    if path.is_file():
                        files.append(path)
    for path in files:
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"required source is missing or a symlink: {path.name}")
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def archive(path, contents):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as output:
        for name, data in sorted(contents):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            output.writestr(entry, data)


def build(output):
    output.mkdir(parents=True, exist_ok=True)
    files = source_files()
    # Source is UTF-8 text; normalize checkout line endings on every platform.
    contents = [(p.relative_to(ROOT).as_posix(), p.read_bytes().replace(b"\r\n", b"\n")) for p in files]
    prefix = f"lemqo-{__version__}"
    source = output / f"{prefix}-source.zip"
    runnable = output / f"{prefix}.pyz"
    archive(source, [(f"{prefix}/{name}", data) for name, data in contents])
    modules = [(name, data) for name, data in contents
               if (name.startswith("lemqo/") and name.endswith(".py")) or name == "LICENSE"]
    modules.append(("__main__.py", b"from lemqo.__main__ import main\nraise SystemExit(main())\n"))
    archive(runnable, modules)
    hashes = "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n"
                     for p in sorted((source, runnable), key=lambda p: p.name))
    (output / "SHA256SUMS").write_bytes(hashes.encode("ascii"))
    return hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    print(build(args.out), end="")


if __name__ == "__main__":
    main()
