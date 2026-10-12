# Contributing

Thanks for helping improve Lemqo. Keep changes focused and explain the behavior or documentation they affect.

## Development

Lemqo uses Python 3.11 or newer and the Python standard library for runtime and tests. Run the test suite and release checks from the repository root:

```text
python -m unittest discover -s tests -v
python tools/check_release.py
python tools/build_release.py --out dist
```

To run from source, use:

```text
python -m lemqo --help
```

## Changes to the proof rules

The v0.1 calculus is fixed. Any proposed rule-set change must update the formal specification, add adversarial tests that exercise invalid as well as valid derivations, and receive maintainer review. Please explain the logical effect of each proposed rule and any change to what acceptance guarantees.

## Reporting issues

Use [GitHub Issues](https://github.com/zhtjoe/Lemqo/issues) for bugs and design questions, or Discussions if enabled. For vulnerability reports, follow [SECURITY.md](SECURITY.md).
