# Contributing

Thanks for helping improve Lemqo. Keep changes focused and explain the behavior or documentation they affect.

## Development

The IPL checker uses Python 3.11 or newer and only the standard library at
runtime. Its v0.1 rules, format, and test semantics remain unchanged. The
optional Lean path has separate native prerequisites and currently has only
Linux validation; see [docs/lean.md](docs/lean.md) before changing it. Run the
Python suite and release checks from the repository root:

```text
python -m unittest discover -s tests -v
python tools/check_release.py
python tools/build_release.py --out dist
```

The optional OpenAI corpus workflow uses repository-vendored sources:

```text
python tools/build_lean_backends.py --work /tmp/lemqo-backends
python tools/openai_certificates.py --work /tmp/lemqo-openai --out /tmp/lemqo-certificates --backends /tmp/lemqo-backends/backends.json
```

It does not accept arbitrary Lean source. Keep main-theorem status distinct
from supporting lemmas, and report a result as checked only after both the
Comparator and independent Nanoda stages pass.

To run from source, use:

```text
python -m lemqo --help
```

## Changes to the proof rules

The v0.1 calculus is fixed. Any proposed rule-set change must update the formal specification, add adversarial tests that exercise invalid as well as valid derivations, and receive maintainer review. Please explain the logical effect of each proposed rule and any change to what acceptance guarantees.

## Reporting issues

Use [GitHub Issues](https://github.com/axiomzero-qed/Lemqo/issues) for bugs and design questions, or Discussions if enabled. For vulnerability reports, follow [SECURITY.md](SECURITY.md).
