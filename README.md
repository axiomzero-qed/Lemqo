# Lemqo

**A small language and independent checker for explicit mathematical proof certificates.**

Lemqo explores how much proof verification can be made transparent and easy to
audit. A producer supplies a certificate; the checker replays every inference
against a separately selected claim. Proof generation and verification are
separate jobs. Our long-term aim is to check certificates produced by humans,
AI, and other proof systems through documented translations.

**v0.2 preserves the v0.1 intuitionistic propositional logic checker and adds
an optional, experimental independent Lean-certificate check.**
The IPL path has ten fixed natural-deduction rules for implication, conjunction,
disjunction, and falsehood. The original `check` command and certificate
semantics are unchanged. The separate `check-lean` workflow is limited to the
repository's pinned, vendored OpenAI corpus; it is not general Lean support.
Three selected OpenAI theorem targets have passed actual statement binding
and independent Nanoda checking: Seymour's second-neighborhood theorem,
Erdős–Gallai cycle decomposition, and Borsuk's projector main theorem.

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

## What a successful IPL check means

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

## Optional Lean certificate path

The Lean path binds a caller-selected reference by hash, performs strict
NDJSON preflight and offline Comparator checks for declarations, statements,
primitives, and axiom types, then asks an independent Rust Nanoda checker to
check every declaration. Both stages must pass before a result can be `VALID`.
Its trusted computing base is larger than the IPL checker's. This path does not
establish absolute correctness or support for all Lean. See the
[Lean checking guide](docs/lean.md) and
[selected OpenAI results and status](docs/openai.md).

Build the backends and prepare the vendored certificate (omit `--only` to
select all three results):

```sh
python tools/build_lean_backends.py --work /tmp/lemqo-backends
python tools/openai_certificates.py --work /tmp/lemqo-openai --out /tmp/lemqo-certificates --backends /tmp/lemqo-backends/backends.json --only seymour_second_neighborhood
```

This workflow has only been exercised on Linux. Preparing a certificate does
not mean its theorem has passed independent checking; the producer reports
`VALID` and writes a receipt only after the separate offline check succeeds.
The [verification records](corpus/openai/verification/summary.json) identify the
three checked main targets and complete certificate hashes. Full exports are
generated locally rather than committed as hundreds of megabytes of JSON.

## Tests, documentation, and releases

```sh
python tools/check_release.py
python tools/build_release.py --out dist
python dist/lemqo-0.2.0.pyz check examples/identity.proof.json --claim examples/identity.claim.json
```

The original 49 IPL tests retain their v0.1 semantics and cover valid proofs,
invalid inferences, assumption discharge, adversarial
JSON, resource limits, CLI failures, and an independent finite Kripke-model
oracle. The build creates a reproducible runnable archive, a source archive,
and SHA-256 checksums using only the standard library.

- [Certificate format, rules, and mathematical semantics](docs/specification.md)
- [Lean certificate checking guide](docs/lean.md)
- [Selected OpenAI results and verification status](docs/openai.md)
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
