# v0.2 validation record

Recorded on 2026-10-13. The earlier [v0.1 record](validation.md) describes the
unchanged IPL calculus; its code-size figures are historical, not counts for
the larger optional Lean path.

- All 78 standard-library test methods passed on Windows/Python 3.12.10;
  the one POSIX FIFO case is skipped there. Linux/Python 3.12.3 runs that case.
- The native regression driver passed 30 actual backend/public-API cases,
  including 585-declaration acceptance, corrupted-proof rejection with an
  unchanged matched statement, definition and primitive replacement, axiom-type
  spoofing, unsupported metadata and missing declarations.
- The public offline API passed the three named OpenAI targets with 22,252,
  41,966 and 70,651 independently checked declarations. Exact scopes, claims,
  source pins and byte identities are in [openai.md](openai.md).
- Lean 4.34.1's official ZIP SHA256 was verified. The repository's safe extractor
  unpacked the actual release under Linux and the extracted executable reported
  the expected version and full commit.
- Source integrity checks cover all 349 vendored Lean files, comparator configs,
  project metadata and retained Apache license. Native sources are locked to
  exact Git revisions; Nanoda is built with its committed Cargo lock file.
- Source/Python archives are compared byte for byte and executed outside the
  checkout. Documentation links, versions and runtime imports are checked.

Native binary reproducibility across hosts, full Lean compatibility, a human
audit and an end-to-end formal implementation proof are not established by
these checks. AI-assisted implementation/review and bounded tests provide
evidence for inspection. The native workflow tests the small fixture; the three
large paper checks above were performed locally and are independently reproducible.
Remote CI is tied to the repository's actual commit and recorded in
[GitHub Actions](https://github.com/axiomzero-qed/Lemqo/actions).
