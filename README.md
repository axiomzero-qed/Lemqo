# Lemqo

**A small language and independent checker for explicit mathematical proof certificates.**

Lemqo explores how much proof verification can be made transparent and easy to
audit. A producer supplies a certificate; the checker replays every inference
against a separately selected claim. Proof generation and verification are
separate jobs. Our long-term aim is to check certificates produced by humans,
AI, and other proof systems through documented translations.

**v0.1 is a working, experimental intuitionistic propositional logic checker.**
It has ten fixed natural-deduction rules for implication, conjunction,
disjunction, and falsehood. It can check genuine logical proofs such as
composition and distributivity. It has no arithmetic, quantifiers, definitions,
custom axioms, tactics, or Lean/Metamath importers. Those are future work.

## Try a valid and an invalid proof

Clone the repository, then run the checker. Python 3.11+ is the only runtime
requirement; after obtaining the source, no package installation or network is
needed. On Windows, use `py -3` if `python` is not available.

```sh
git clone https://github.com/axiomzero-qed/Lemqo.git
cd Lemqo
python -m lemqo check examples/identity.proof.json --claim examples/identity.claim.json
```

This checks `P → P` and prints `VALID identity (closed; 2 checked steps)`.
It also shows the exact goal and premise dependencies. Now try:

```sh
python -m lemqo check examples/identity.invalid.proof.json --claim examples/identity.claim.json
```

The forged inference prints `REJECTED [inference]` and exits with status 1.
Rejection means the submitted certificate failed, not that its claim is false:
both examples target the same true statement.

For a larger proof and a machine-readable receipt:

```sh
python -m lemqo check examples/distributivity.proof.json --claim examples/distributivity.claim.json --json
```

## What a successful check means

Acceptance establishes derivability of the **supplied formula from the reported
premises under the fixed rules**, subject to correctness of this implementation
and its runtime. A certificate cannot change the caller's claim. Open
assumptions must be explicitly permitted; `False ⊢ P` is a conditional result,
while an unproved `⊢ False` is rejected.

Atoms such as `P` are uninterpreted propositions. Naming an atom `RiemannHypothesis`
does not formalize or prove that mathematical conjecture. Review the formal
statement and its premises as well as the certificate. There is no claim of
absolute safety, implementation correctness, or a measured total trusted base
smaller than Lean's. The Python interpreter is part of the trust boundary.

## Tests, documentation, and releases

```sh
python tools/check_release.py
python tools/build_release.py --out dist
python dist/lemqo-0.1.0.pyz check examples/identity.proof.json --claim examples/identity.claim.json
```

Tests cover valid proofs, invalid inferences, assumption discharge, adversarial
JSON, resource limits, CLI failures, and an independent finite Kripke-model
oracle. The build creates a reproducible runnable archive, a source archive,
and SHA-256 checksums using only the standard library.

- [Certificate format, rules, and mathematical semantics](docs/specification.md)
- [Trusted boundary, threat model, and soundness argument](docs/trust.md)
- [Architecture and audit entry points](docs/architecture.md)
- [Research: Lean, Metamath, MM0, and HOL/OpenTheory](docs/research.md)
- [Examples and how their proofs work](examples/README.md)
- [Release instructions and reproducibility](docs/release.md)
- [Recorded local validation and review](docs/validation.md)
- [Roadmap](docs/roadmap.md), [contributing](CONTRIBUTING.md), [security](SECURITY.md)

Project domain: [lemqo.com](https://lemqo.com). The repository's English Markdown
documentation is the source for a future documentation site; v0.1 does not
deploy or depend on a website. Public repository:
[axiomzero-qed/Lemqo](https://github.com/axiomzero-qed/Lemqo).

Lemqo is licensed under the [MIT License](LICENSE). The implementation is
original; the research documents acknowledge the systems that informed it.
