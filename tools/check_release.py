"""Run tests and check example outcomes, documentation links, and metadata."""

import ast
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lemqo import Rejection, __version__, verify_bytes  # noqa: E402
from check_openai_sources import check_catalog  # noqa: E402


def check_documents():
    required = ("README.md", "LICENSE", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
                "SECURITY.md", "CHANGELOG.md", "docs/specification.md", "docs/trust.md",
                "docs/architecture.md", "docs/research.md", "docs/release.md",
                ".github/workflows/ci.yml", ".github/workflows/release-artifacts.yml",
                "docs/lean.md", "docs/openai.md", "corpus/openai/catalog.json",
                "corpus/openai/LICENSE", "bridge/lean/Main.lean", "bridge/lean/lake-manifest.json",
                "bridge/openai/lake-manifest.json")
    for name in required:
        if not (ROOT / name).is_file():
            raise RuntimeError(f"missing release file: {name}")
    for path in [*ROOT.glob("*.md"), *ROOT.glob("docs/*.md"), *ROOT.glob("examples/*.md")]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = target.strip("<>").split("#", 1)[0]
            if not target or ":" in target:
                continue
            if not (path.parent / target).exists():
                raise RuntimeError(f"broken local link in {path.name}: {target}")
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    if metadata["project"]["version"] != __version__:
        raise RuntimeError("package version differs from verifier version")
    if metadata["project"]["dependencies"]:
        raise RuntimeError("runtime must remain dependency-free")


def check_imports():
    for path in (ROOT / "lemqo").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [(node.module or "").split(".")[0]]
            if any(name not in sys.stdlib_module_names for name in names):
                raise RuntimeError(f"non-standard-library runtime import in {path.name}")


def check_examples():
    checked = 0
    for path in sorted((ROOT / "examples").glob("*.proof.json")):
        invalid = ".invalid." in path.name
        name = path.name.replace(".invalid", "").removesuffix(".proof.json")
        claim = (ROOT / "examples" / f"{name}.claim.json").read_bytes()
        try:
            verify_bytes(claim, path.read_bytes())
        except Rejection:
            if not invalid:
                raise RuntimeError(f"valid example rejected: {path.name}") from None
        else:
            if invalid:
                raise RuntimeError(f"invalid example accepted: {path.name}")
        checked += 1
    if checked != 9:
        raise RuntimeError("expected seven valid and two invalid documented examples")
    return checked


def main():
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT)
    if result.returncode:
        return result.returncode
    check_documents()
    check_imports()
    check_catalog(ROOT)
    count = check_examples()
    print(f"Release checks passed: lemqo {__version__}; {count} expected example outcomes; documentation and metadata checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
