# Releasing Lemqo v0.2

## Local verification

Run from the repository root with Python 3.11+:

```sh
python tools/check_release.py
python tools/build_release.py --out dist
python dist/lemqo-0.2.0.pyz check examples/identity.proof.json --claim examples/identity.claim.json
```

The release check runs the complete test suite and checks documented example
outcomes, local documentation links, version consistency, required files, and
standard-library runtime imports. The IPL command remains cross-platform. The
optional Lean path has only been validated on Linux; this does not assert that
v0.2 CI or a release tag has been verified.

The build writes three files:

- `lemqo-0.2.0.pyz`: source ZIP application, launched with `python`; Python is
  still required. It includes the checker and its MIT license.
- `lemqo-0.2.0-source.zip`: allowlisted source, docs, tests, examples, and CI
  configuration under the `lemqo-0.2.0/` directory.
- `SHA256SUMS`: exact-byte SHA-256 values for those two archives.

Extracting the source archive and running its quickstart requires no network.
The tests build twice, compare every byte, and launch the runnable archive
from outside the checkout with Python isolated mode.

## Reproducibility contract

Given identical allowlisted source contents after CRLF-to-LF normalization,
the archive builder produces identical bytes. It sorts paths, uses stored
uncompressed ZIP entries, fixes timestamps to 1980-01-01, and normalizes file
modes. It excludes git history, caches, build outputs, virtual environments,
and unlisted workspace files. No compiler, zlib version, local timezone, wall
clock, or package index affects these archive bytes.

To independently compare builds:

```sh
python tools/build_release.py --out dist/first
python tools/build_release.py --out dist/second
```

Compare both archives and checksum files byte for byte. Checksums identify
artifacts; they are not authentication. Independently verify the source and
obtain release checksums through a trusted channel. The builder itself does
not run tests; use the release check before building.

## Optional package installation

For a conventional local installation:

```sh
python -m pip install .
lemqo check examples/identity.proof.json --claim examples/identity.claim.json
```

The runtime has no package dependencies. This optional installation uses a
PEP 517 setuptools build backend pinned in `pyproject.toml`; fetching it may
require network access. The archive reproducibility claim above applies to
the standard-library ZIP builder, not arbitrary wheel or installer output.
No package has been uploaded to PyPI and no package-name reservation is claimed.

## GitHub publication

The public repository is [axiomzero-qed/Lemqo](https://github.com/axiomzero-qed/Lemqo).
Before publishing a release tag, review repository metadata and security-reporting
contact options and record the reviewed release commit. The homepage is
`https://lemqo.com`; no live deployment or current domain-content claim is part
of this release.

Push the reviewed source, wait for CI, then create a reviewed release tag and
release described by [CHANGELOG.md](../CHANGELOG.md). The manual
`Build release artifacts` workflow tests and uploads the archives as a workflow
artifact; it never publishes a GitHub release automatically. Attach the three
reviewed files to the release and preserve the commit, CI evidence, Python
version and checksums with the release record.

The English Markdown in `docs/` is the canonical documentation. A future
lemqo.com site can publish these same versioned files and link each release
to its source, specification, examples, and checksums. Avoid a second,
independently edited technical specification on the website.
