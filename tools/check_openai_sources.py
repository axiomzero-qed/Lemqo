#!/usr/bin/env python3
"""Verify the integrity and path inventory of the pinned OpenAI math snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


class CatalogError(Exception):
    """Raised when the local source catalog or its vendored files are invalid."""


CANONICAL_NAME = re.compile(r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*")
EXTERNAL_ROOTS = frozenset(("Init", "Lean", "Std", "Lake", "Mathlib", "Aesop", "Batteries",
                            "Cli", "ImportGraph", "LeanSearchClient", "Plausible", "Qq", "ProofWidgets"))


def theorem_names(item, label="candidate"):
    """Normalize the v1 singular spelling or the v0.3 array without ambiguity."""
    names = item.get("theorem_names")
    if names is None and "theorem_names" not in item:
        names = [item.get("theorem")]
    if (type(names) is not list or not 1 <= len(names) <= 32
            or any(type(n) is not str or len(n) > 256 or CANONICAL_NAME.fullmatch(n) is None for n in names)
            or len(set(names)) != len(names)):
        raise CatalogError(f"{label}.theorem_names must contain 1–32 unique canonical names")
    if "theorem" in item and names != [item["theorem"]]:
        raise CatalogError(f"{label}: theorem and theorem_names disagree")
    return names.copy()


def lean_imports(text):
    # Lean has nested block comments. Preserve line boundaries while stripping
    # them, so an import in a comment cannot hide a missing local dependency.
    cleaned, index, depth = [], 0, 0
    while index < len(text):
        pair = text[index:index + 2]
        if pair == "/-":
            cleaned.append(" ")
            depth += 1
            index += 2
        elif depth and pair == "-/":
            cleaned.append(" ")
            depth -= 1
            index += 2
        elif not depth and pair == "--":
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
        else:
            cleaned.append(text[index] if not depth or text[index] == "\n" else " ")
            index += 1
    for line in "".join(cleaned).splitlines():
        match = re.match(r"\s*(?:(?:public|private)\s+)?import\s+(.*)", line)
        if match is not None:
            for name in match[1].split():
                if name == "all":
                    continue
                if CANONICAL_NAME.fullmatch(name) is None:
                    raise CatalogError(f"unsupported import syntax: {name}")
                yield name


def import_roots(work, modules):
    """Resolve every local root, rejecting unknown imports before Lake runs."""
    seen, mathlib = set(), set()
    pending = list(modules)
    while pending:
        module = pending.pop()
        if module in seen:
            continue
        seen.add(module)
        if CANONICAL_NAME.fullmatch(module) is None:
            raise CatalogError(f"invalid module name: {module}")
        source = work / (module.replace(".", "/") + ".lean")
        if source.is_file():
            pending.extend(lean_imports(source.read_text(encoding="utf-8")))
        elif module.split(".")[0] not in EXTERNAL_ROOTS:
            raise CatalogError(f"unresolved local import: {module} (expected {source})")
        elif module == "Mathlib" or module.startswith("Mathlib."):
            mathlib.add(module)
    return sorted(mathlib)


@dataclass(frozen=True)
class Summary:
    candidates: int
    source_files: int
    source_bytes: int


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CatalogError(f"{label} must be an object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise CatalogError(f"{label} must be an array")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise CatalogError(f"{label} must be a nonempty string")
    return value


def _relative_parts(raw: Any, label: str) -> tuple[str, ...]:
    value = _text(raw, label)
    if "\\" in value or ":" in value or value.startswith("/"):
        raise CatalogError(f"{label} must be a relative POSIX path")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise CatalogError(f"{label} must not contain empty, '.' or '..' components")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise CatalogError(f"{label} must be relative")
    return tuple(parts)


def _safe_file(corpus: Path, raw: Any, label: str) -> tuple[Path, str]:
    parts = _relative_parts(raw, label)
    candidate = corpus.joinpath(*parts)
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise CatalogError(f"{label}: file is missing or unreadable: {raw}") from exc
    try:
        resolved.relative_to(corpus)
    except ValueError as exc:
        raise CatalogError(f"{label}: path escapes corpus/openai: {raw}") from exc
    current = corpus
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise CatalogError(f"{label}: symbolic links are not allowed: {raw}")
    if not resolved.is_file():
        raise CatalogError(f"{label}: not a regular file: {raw}")
    return resolved, "/".join(parts)


def _record(record: Any, label: str) -> tuple[str, int, str]:
    item = _mapping(record, label)
    path = _text(item.get("path"), f"{label}.path")
    size = item.get("bytes")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise CatalogError(f"{label}.bytes must be a nonnegative integer")
    digest = _text(item.get("sha256"), f"{label}.sha256")
    if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise CatalogError(f"{label}.sha256 must be a lowercase SHA256 digest")
    return path, size, digest


def _unique_path(path: str, seen: set[str], label: str) -> None:
    folded = path.casefold()
    if folded in seen:
        raise CatalogError(f"duplicate path in {label}: {path}")
    seen.add(folded)


def _load_json(path: Path, label: str) -> Any:
    def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise CatalogError(f"duplicate JSON key in {label}: {key}")
            result[key] = value
        return result

    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
    except CatalogError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogError(f"{label} is missing, unreadable, or invalid JSON") from exc


def _check_file(corpus: Path, raw_path: str, size: int, expected_hash: str,
                label: str) -> None:
    path, _ = _safe_file(corpus, raw_path, label)
    digest = hashlib.sha256()
    total = 0
    try:
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                total += len(chunk)
                digest.update(chunk)
    except OSError as exc:
        raise CatalogError(f"{label}: cannot read {raw_path}") from exc
    if total != size:
        raise CatalogError(f"{label}: byte count mismatch for {raw_path}: expected {size}, got {total}")
    actual_hash = digest.hexdigest()
    if actual_hash != expected_hash:
        raise CatalogError(f"{label}: SHA256 mismatch for {raw_path}")


def _check_lean_inventory(corpus: Path, expected: set[str]) -> None:
    actual: set[str] = set()
    def walk_error(exc: OSError) -> None:
        raise CatalogError(f"cannot inspect corpus/openai inventory: {exc}") from exc

    for current, dirs, names in os.walk(corpus, followlinks=False, onerror=walk_error):
        current_path = Path(current)
        for name in tuple(dirs):
            entry = current_path / name
            if entry.is_symlink():
                raise CatalogError(f"symbolic-link directory is not allowed in corpus/openai: {entry.relative_to(corpus)}")
        for name in names:
            entry = current_path / name
            rel = entry.relative_to(corpus).as_posix()
            if entry.is_symlink():
                raise CatalogError(f"symbolic-link file is not allowed in corpus/openai: {rel}")
            if entry.suffix == ".lean":
                actual.add(rel)
    extra = sorted(actual - expected)
    missing = sorted(expected - actual)
    if extra:
        raise CatalogError(f"unlisted .lean source file(s): {', '.join(extra)}")
    if missing:
        raise CatalogError(f"catalogued .lean source file(s) missing: {', '.join(missing)}")


def check_catalog(repository_root: Path) -> Summary:
    """Validate catalog/openai bytes, hashes, and complete Lean-file inventory."""
    repository_root = Path(repository_root).resolve()
    lexical_corpus = repository_root / "corpus" / "openai"
    try:
        corpus = lexical_corpus.resolve(strict=True)
        corpus.relative_to(repository_root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise CatalogError("corpus/openai is missing or resolves outside the repository") from exc
    if lexical_corpus.is_symlink() or not corpus.is_dir():
        raise CatalogError("corpus/openai must be a regular directory")

    catalog_path = corpus / "catalog.json"
    if catalog_path.is_symlink():
        raise CatalogError("catalog.json must not be a symbolic link")
    catalog = _load_json(catalog_path, "catalog.json")
    catalog = _mapping(catalog, "catalog")
    schema_version = catalog.get("schema_version")
    if isinstance(schema_version, bool) or schema_version != 1:
        raise CatalogError("unsupported catalog schema_version")
    if catalog.get("lean_sources_root") != "lean/":
        raise CatalogError("lean_sources_root must be 'lean/'")

    source_records = _list(catalog.get("source_files"), "source_files")
    project_records = _list(catalog.get("project_files"), "project_files")
    candidates = _list(catalog.get("candidates"), "candidates")
    if not candidates:
        raise CatalogError("candidates must not be empty")

    source_paths: set[str] = set()
    expected_lean: set[str] = set()
    source_bytes = 0
    for index, item in enumerate(source_records):
        rel, size, digest = _record(item, f"source_files[{index}]")
        parts = _relative_parts(rel, f"source_files[{index}].path")
        if not rel.endswith(".lean"):
            raise CatalogError(f"source_files[{index}].path must name a .lean source")
        _unique_path(rel, source_paths, "source_files")
        _check_file(corpus, "lean/" + rel, size, digest, f"source_files[{index}]")
        expected_lean.add("lean/" + "/".join(parts))
        source_bytes += size
    source_file_count = catalog.get("source_file_count")
    if (isinstance(source_file_count, bool) or not isinstance(source_file_count, int)
            or source_file_count != len(source_records)):
        raise CatalogError("source_file_count does not match source_files")
    declared_source_bytes = catalog.get("source_bytes")
    if (isinstance(declared_source_bytes, bool) or not isinstance(declared_source_bytes, int)
            or declared_source_bytes != source_bytes):
        raise CatalogError("source_bytes does not match source_files")

    project_paths: set[str] = set()
    project_relpaths: set[str] = set()
    for index, item in enumerate(project_records):
        rel, size, digest = _record(item, f"project_files[{index}]")
        parts = _relative_parts(rel, f"project_files[{index}].path")
        _unique_path(rel, project_paths, "project_files")
        if rel.casefold() in source_paths:
            raise CatalogError(f"path appears in both source_files and project_files: {rel}")
        _check_file(corpus, "lean/" + rel, size, digest, f"project_files[{index}]")
        project_relpaths.add(rel)
        if rel.endswith(".lean"):
            expected_lean.add("lean/" + "/".join(parts))

    upstream_catalogue = _text(catalog.get("upstream_catalogue"), "upstream_catalogue")
    _relative_parts(upstream_catalogue, "upstream_catalogue")
    if not upstream_catalogue.startswith("lean/") or upstream_catalogue.removeprefix("lean/") not in project_relpaths:
        raise CatalogError("upstream_catalogue must refer to a catalogued project_file")

    upstream = _mapping(catalog.get("upstream"), "upstream")
    license_path = _text(upstream.get("license"), "upstream.license")
    license_hash = _text(upstream.get("license_sha256"), "upstream.license_sha256")
    if re.fullmatch(r"[0-9a-f]{64}", license_hash) is None:
        raise CatalogError("upstream.license_sha256 must be a lowercase SHA256 digest")
    _, license_rel = _safe_file(corpus, license_path, "upstream license")
    if license_rel.casefold() in {"catalog.json"}:
        raise CatalogError("upstream license path duplicates catalog.json")
    license_file, _ = _safe_file(corpus, license_rel, "upstream license")
    try:
        license_size = license_file.stat().st_size
    except OSError as exc:
        raise CatalogError("upstream license: cannot read file size") from exc
    _check_file(corpus, license_path, license_size, license_hash, "upstream license")

    ids: set[str] = set()
    config_paths: set[str] = set()
    manifest_paths = {"lean/" + path for path in source_paths | project_paths}
    for index, candidate in enumerate(candidates):
        label = f"candidates[{index}]"
        item = _mapping(candidate, label)
        ident = _text(item.get("id"), f"{label}.id")
        if re.fullmatch(r"[a-z][a-z0-9_]{0,63}", ident) is None:
            raise CatalogError(f"{label}.id must be a lowercase safe identifier (up to 64 characters)")
        if ident.casefold() in ids:
            raise CatalogError(f"duplicate candidate id: {ident}")
        ids.add(ident.casefold())
        for field in ("challenge_module", "solution_module"):
            if CANONICAL_NAME.fullmatch(_text(item.get(field), f"{label}.{field}")) is None:
                raise CatalogError(f"{label}.{field} must be a canonical module name")
        targets = theorem_names(item, label)
        definition_names = item.get("definition_names")
        if not isinstance(definition_names, list) or any(not isinstance(x, str) for x in definition_names):
            raise CatalogError(f"{label}.definition_names must be an array of strings")

        spec_raw = _text(item.get("challenge_spec"), f"{label}.challenge_spec")
        _, spec_rel = _safe_file(corpus, spec_raw, f"{label}.challenge_spec")
        if not spec_rel.startswith("lean/") or not spec_rel.endswith(".lean"):
            raise CatalogError(f"{label}.challenge_spec must be under lean/ and end in .lean")
        source_rel = spec_rel.removeprefix("lean/")
        if source_rel.casefold() not in source_paths:
            raise CatalogError(f"{label}.challenge_spec is not listed in source_files")

        config_raw = _text(item.get("challenge_config"), f"{label}.challenge_config")
        config_path, config_rel = _safe_file(corpus, config_raw, f"{label}.challenge_config")
        if not config_rel.startswith("lean/ComparatorChallenges/") or not config_rel.endswith(".json"):
            raise CatalogError(f"{label}.challenge_config must be a ComparatorChallenges JSON file")
        _unique_path(config_rel, config_paths, "candidate challenge_config")
        if config_rel.casefold() in manifest_paths:
            raise CatalogError(f"challenge_config path duplicates another catalogued file: {config_rel}")
        size = item.get("challenge_config_bytes")
        digest = _text(item.get("challenge_config_sha256"), f"{label}.challenge_config_sha256")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise CatalogError(f"{label}.challenge_config_bytes must be a nonnegative integer")
        if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise CatalogError(f"{label}.challenge_config_sha256 must be a lowercase SHA256 digest")
        _check_file(corpus, config_rel, size, digest, f"{label}.challenge_config")
        config = _load_json(config_path, f"{label}.challenge_config")
        config = _mapping(config, f"{label}.challenge_config")
        if config.get("challenge_module") != item["challenge_module"]:
            raise CatalogError(f"{label}: challenge module does not match config")
        if config.get("solution_module") != item["solution_module"]:
            raise CatalogError(f"{label}: solution module does not match config")
        if config.get("theorem_names") != targets:
            raise CatalogError(f"{label}: theorem target does not match config")
        if config.get("definition_names") != definition_names:
            raise CatalogError(f"{label}: definition targets do not match config")
        if config.get("permitted_axioms") != item.get("permitted_axioms"):
            raise CatalogError(f"{label}: permitted axioms do not match config")
        if config.get("enable_nanoda") != item.get("enable_nanoda"):
            raise CatalogError(f"{label}: enable_nanoda does not match config")
        import_roots(corpus / "lean", [item["challenge_module"], item["solution_module"]])

    unique_file_count = catalog.get("unique_upstream_file_count")
    if (isinstance(unique_file_count, bool) or not isinstance(unique_file_count, int)
            or unique_file_count != len(manifest_paths | config_paths)):
        raise CatalogError("unique_upstream_file_count does not match the catalogued file inventory")
    if license_rel.casefold() in manifest_paths | config_paths:
        raise CatalogError("upstream license path duplicates another catalogued file")
    _check_lean_inventory(corpus, expected_lean)
    return Summary(len(candidates), len(source_records), source_bytes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check local OpenAI math source snapshot hashes and inventory.")
    parser.add_argument("--root", type=Path,
                        help="repository root (defaults to the parent of this tools directory)")
    args = parser.parse_args(argv)
    repository_root = args.root if args.root is not None else Path(__file__).resolve().parents[1]
    try:
        summary = check_catalog(repository_root)
    except (CatalogError, OSError) as exc:
        print(f"OpenAI source snapshot rejected: {exc}", file=sys.stderr)
        return 1
    print(f"OpenAI source integrity OK: {summary.source_files} Lean files, "
          f"{summary.candidates} candidates, {summary.source_bytes} bytes; no Lean execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
