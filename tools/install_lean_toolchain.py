"""Install the pinned Lean 4.34.1 Linux release into a dedicated directory."""

import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import tempfile
import urllib.request
import zipfile


LEAN_URL = "https://github.com/leanprover/lean4/releases/download/v4.34.1/lean-4.34.1-linux.zip"
LEAN_SHA256 = "3013aba02bb8bf31b1cf8c9d956d60fb95bb1c10920dfe91abcaa59cb461ddac"
MAX_ARCHIVE_BYTES = 1024**3
MAX_EXPANDED_BYTES = 8 * 1024**3
MAX_MEMBERS = 200_000
CHUNK = 1024 * 1024


def checked_target(raw):
    """Resolve --out and reject roots or paths that could replace the checkout."""
    requested = Path(raw).expanduser()
    if not requested.is_absolute():
        requested = Path.cwd() / requested
    parent = requested.parent.resolve()
    target = parent / requested.name
    if target.name in ("", ".", "..") or target == Path(target.anchor):
        raise ValueError("--out must name a dedicated directory, not a filesystem root")
    protected_roots = {Path.home().resolve(), Path(__file__).resolve().parents[1]}
    for path in protected_roots:
        if target == path or target in path.parents:
            raise ValueError("--out must not replace the user home, repository, or an ancestor")
    if target.exists() or target.is_symlink():
        raise ValueError("--out must not already exist")
    return target


def _member_name(info):
    name = info.filename
    if not name or "\\" in name or name.startswith("/"):
        raise ValueError("unsafe ZIP member path: " + repr(name))
    raw_parts = name.rstrip("/").split("/")
    if not raw_parts or any(part in ("", ".", "..") for part in raw_parts):
        raise ValueError("unsafe ZIP member path: " + repr(name))
    if ":" in raw_parts[0]:
        raise ValueError("drive-like ZIP member path: " + repr(name))
    return PurePosixPath(*raw_parts).as_posix(), info.is_dir()


def _inside_link(name, target):
    if not target or target.startswith("/") or "\\" in target or "\x00" in target:
        raise ValueError("unsafe ZIP symlink target: " + repr(target))
    combined = PurePosixPath(name).parent.joinpath(target)
    parts = []
    for part in combined.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                raise ValueError("ZIP symlink escapes installation directory")
            parts.pop()
        else:
            parts.append(part)
    if not parts:
        raise ValueError("ZIP symlink may not target installation root")
    return PurePosixPath(*parts).as_posix()


def _safe_extract(archive, destination):
    with zipfile.ZipFile(archive) as zf:
        infos = zf.infolist()
        if len(infos) > MAX_MEMBERS:
            raise ValueError("ZIP contains too many members")
        entries = {}
        symlinks = {}
        total = 0
        for info in infos:
            name, is_dir = _member_name(info)
            mode = info.external_attr >> 16
            kind = stat.S_IFMT(mode)
            is_link = kind == stat.S_IFLNK
            if kind not in (0, stat.S_IFREG, stat.S_IFDIR, stat.S_IFLNK):
                raise ValueError("unsupported special ZIP member: " + name)
            if is_link and is_dir:
                raise ValueError("symlink marked as directory: " + name)
            if name in entries:
                raise ValueError("duplicate ZIP member: " + name)
            entries[name] = (info, is_dir, mode, is_link)
            if is_link:
                target = zf.read(info).decode("utf-8", errors="strict")
                resolved = _inside_link(name, target)
                symlinks[name] = resolved
            elif not is_dir:
                total += info.file_size
                if total > MAX_EXPANDED_BYTES:
                    raise ValueError("ZIP expands beyond the configured size bound")

        # Reject any file or link placed below a symlink, independent of archive order.
        for name in entries:
            for parent in PurePosixPath(name).parents:
                p = parent.as_posix()
                if p != "." and p in symlinks:
                    raise ValueError("ZIP member is nested below a symlink: " + name)
        for name, (info, is_dir, mode, is_link) in entries.items():
            if is_link:
                continue
            path = destination.joinpath(*PurePosixPath(name).parts)
            if is_dir:
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as source, path.open("xb") as output:
                    shutil.copyfileobj(source, output, CHUNK)
                path.chmod((mode & 0o777) or 0o644)

        # Apply directory permissions after writing children; archives may store
        # read-only directory modes.
        for name, (info, is_dir, mode, is_link) in entries.items():
            if is_dir:
                destination.joinpath(*PurePosixPath(name).parts).chmod((mode & 0o777) or 0o755)

        for name, resolved in symlinks.items():
            info = entries[name][0]
            target = zf.read(info).decode("utf-8", errors="strict")
            prefix = PurePosixPath()
            for part in PurePosixPath(resolved).parts:
                prefix /= part
                if prefix.as_posix() in symlinks:
                    raise ValueError("ZIP symlink target traverses another symlink: " + name)
            path = destination.joinpath(*PurePosixPath(name).parts)
            # Require the lexical target and every chained link to be represented in
            # the archive so link resolution cannot depend on ambient filesystem state.
            if resolved not in entries:
                raise ValueError("ZIP symlink target is not an archive member: " + name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.symlink_to(target)


def _download(destination):
    digest = hashlib.sha256()
    count = 0
    request = urllib.request.Request(LEAN_URL, headers={"User-Agent": "Lemqo-toolchain-installer"})
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("xb") as output:
        final_url = response.geturl()
        if not final_url.startswith("https://"):
            raise ValueError("Lean release download did not use HTTPS")
        while True:
            block = response.read(CHUNK)
            if not block:
                break
            count += len(block)
            if count > MAX_ARCHIVE_BYTES:
                raise ValueError("Lean archive exceeds the configured download bound")
            digest.update(block)
            output.write(block)
    actual = digest.hexdigest()
    if actual != LEAN_SHA256:
        raise ValueError("Lean archive SHA-256 mismatch: " + actual)


def install(out):
    if sys.platform != "linux":
        raise RuntimeError("the pinned release installer supports Linux and WSL only")
    target = checked_target(out)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lemqo-lean-install-", dir=target.parent) as temporary:
        temporary = Path(temporary)
        archive = temporary / "lean.zip"
        staged = temporary / "installation"
        staged.mkdir()
        print("Downloading pinned Lean 4.34.1 release...", flush=True)
        _download(archive)
        print("SHA-256 verified; safely extracting...", flush=True)
        _safe_extract(archive, staged)
        lean_candidates = list(staged.glob("*/bin/lean"))
        if len(lean_candidates) != 1 or not os.access(lean_candidates[0], os.X_OK):
            raise ValueError("release archive did not contain one executable */bin/lean")
        shutil.move(str(staged), str(target))
    installed = target / lean_candidates[0].relative_to(staged)
    print(installed)
    return installed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="new dedicated directory for the Lean toolchain")
    args = parser.parse_args()
    try:
        install(args.out)
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        print("Lean installation failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
