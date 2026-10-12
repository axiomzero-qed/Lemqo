# Changelog

## 0.2.0 — experimental independent Lean checking

- Preserves the v0.1 IPL `check` behavior, certificate format, and test
  semantics.
- Adds an optional `check-lean` workflow with reference-hash binding, strict
  NDJSON preflight, offline Comparator checks, and independent Rust Nanoda
  checking of every declaration.
- Limits the current corpus workflow to three selected, vendored OpenAI
  results. The selected main targets passed independent checking: Seymour
  (22,252 declarations), Erdős–Gallai (41,966), and the Borsuk projector main
  theorem (70,651). Supporting lemmas are not counted as additional results.
- Records Linux-only validation for this path: a 585-declaration smoke check
  and 30 native/public-API regression cases passed. This is not a claim of general Lean
  support or verification of all 722 manuscripts.

The Lean path adds trusted components beyond the IPL checker. No v0.2 release
tag or GitHub CI run is asserted here.

## 0.1.0 — initial release candidate, 2026-10-12

- A fixed intuitionistic propositional natural-deduction calculus with ten rules.
- Explicit formula/proof DAG certificates and separately selected claim files.
- Structural formula identity, immutable assumption tracking and exact goal binding.
- Bounded strict UTF-8 JSON ingestion and fail-closed CLI/API behavior.
- Seven accepted example derivations and two deliberately rejected certificates.
- Unit, adversarial, semantic-oracle, CLI and reproducible-archive tests.
- English specification, trust analysis, research, contributor and release documents.
- MIT license, pinned GitHub Actions, and dependency-free offline ZIP releases.

The v0.1 candidate contains one Python IPL checker and no quantified
mathematics, arithmetic, custom axioms, definitions, tactics or external-system
importers. There is no machine-checked proof of implementation correctness.
Publication and remote CI results must be recorded separately when the
repository is live.
