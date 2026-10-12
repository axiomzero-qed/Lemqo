# Lemqo v1 certificate specification

This is the normative v0.1 format and calculus. The implementation version is
0.1.0; the wire formats are `lemqo-claim-v1` and `lemqo-proof-v1`, with fixed
logic identifier `ipl`. Any incompatible logical or format change needs a new
identifier. Resource-policy changes must be documented separately.

## Formulas and semantics

Abstract formulas are finite trees:

```text
F ::= Atom(name) | False | Imp(F,F) | And(F,F) | Or(F,F)
name ::= [A-Za-z][A-Za-z0-9_]{0,63}
```

Names are case-sensitive uninterpreted propositional variables. There are no
definitions or reserved mathematical meanings attached to names. `Atom("false")`
and `False` are different formulas. Formula equality is exact tree equality;
there is no implicit associativity, commutativity, reduction, or equivalence.
Negation can be written `Imp(A,False)`; truth can be written `Imp(False,False)`.
These are explanations, not additional syntax or primitive rules.

A Kripke model consists of a nonempty partially ordered set of worlds `(W, ≤)`
and an upward-closed set of worlds for each atom. Forcing is defined by:

- `w ⊩ P` exactly when `w` belongs to the atom's set.
- No world forces `False`.
- `w ⊩ And(A,B)` exactly when `w ⊩ A` and `w ⊩ B`.
- `w ⊩ Or(A,B)` exactly when `w ⊩ A` or `w ⊩ B`.
- `w ⊩ Imp(A,B)` exactly when every `v ≥ w` that forces `A` also forces `B`.

These clauses are persistent upwards. A sequent `Γ ⊢ C` is semantically valid
when, in every model and world, forcing every formula in the finite set `Γ`
implies forcing `C`. The rules below are sound for this semantics. Acceptance
checks a derivation, rather than running a truth-table or finite-model test.
Excluded middle and double-negation elimination are not built-in principles.

## Byte-level format

Each document is one strict UTF-8 JSON object. A BOM, duplicate object keys,
comments, trailing data, malformed UTF-8, and lone surrogate escapes are
rejected. String escapes are decoded before identifiers are compared; `"P"`
and `"\u0050"` denote the same atom. Whitespace and object-key ordering do not
affect derivability. Input hashes refer to original bytes, so these changes do
affect receipt hashes.

Only integer JSON numbers with at most nine digits, excluding the minus sign,
are supported. Decimal/exponent notation, NaN, Infinity, and negative zero are
rejected. Every index must have exact integer type, be nonnegative, and satisfy
its range check; booleans are never indices. JSON booleans and null have no
valid location in either document's schema.

All listed keys are mandatory; additional keys are rejected. There are no
includes, external references, executable strings, or extensible rules.

## Claim document

```json
{
  "format": "lemqo-claim-v1",
  "logic": "ipl",
  "name": "identity",
  "premises": [],
  "goal": ["imp", "P", "P"]
}
```

`name` matches `[A-Za-z][A-Za-z0-9_.-]{0,63}` and labels the report only. Claim
formulas use prefix trees: an atom is a string, falsehood is `["false"]`, and
each binary connective is `["imp"|"and"|"or", left, right]` (the vertical bars
here describe alternatives; they are not JSON syntax). `premises` is a list
of distinct structural formulas. Its order determines receipt premise indices.

The caller selects this file independently of the proof. Declared premises
are permissions to leave those formulas open; Lemqo never verifies their
truth, consistency, or intended informal interpretation.

## Proof document

```json
{
  "format": "lemqo-proof-v1",
  "logic": "ipl",
  "formulas": [["atom", "P"], ["imp", 0, 0]],
  "steps": [["assume", 0], ["imp_intro", 1, 0]],
  "root": 1
}
```

Formula and step IDs are zero-based row positions, in separate namespaces.
The formula table consists of exactly these row shapes:

| Row | Meaning |
| --- | --- |
| `["atom", name]` | Atom with the given identifier |
| `["false"]` | Falsehood |
| `["imp", a, b]` | Implication of formula rows `a` and `b` |
| `["and", a, b]` | Conjunction of formula rows `a` and `b` |
| `["or", a, b]` | Disjunction of formula rows `a` and `b` |

At formula row `i`, child IDs must be strictly less than `i`. Duplicate
structural formulas are permitted and canonicalized using full structural
equality, so different IDs cannot create different meanings for the same
formula. Claim trees and proof DAGs share this identity relation. Intermediate
atoms not present in the claim are allowed and remain uninterpreted.

Each proof row names a rule, an explicit conclusion formula row `f`, and zero
or more parent step IDs. At step `i`, every parent ID must be less than `i`.
Conclusion formula IDs may reference any row of the already validated formula
table. `root` selects any existing step, not necessarily the last one. All
formulas and all steps must validate, including nodes after or unrelated to
the root. Forward references, cycles, and empty tables are rejected.

## Ten inference rules

Each checked step is a judgment `(C, Γ)` with conclusion `C` and a finite,
immutable set of open assumption formulas `Γ`. The certificate supplies `C`
but never supplies `Γ`. The checker computes it. In the table, `j:(C,Γ)` means
that parent step `j` has the indicated already checked judgment.

| Row | Required shapes | Computed judgment |
| --- | --- | --- |
| `["assume", f]` | `f = A` | `(A, {A})` |
| `["imp_intro", f, j]` | `f = A → B`; `j:(B,Γ)` | `(A → B, Γ \ {A})` |
| `["imp_elim", f, j, k]` | `f = B`; `j:(A → B,Γ)`; `k:(A,Δ)` | `(B, Γ ∪ Δ)` |
| `["and_intro", f, j, k]` | `f = A ∧ B`; `j:(A,Γ)`; `k:(B,Δ)` | `(A ∧ B, Γ ∪ Δ)` |
| `["and_left", f, j]` | `f = A`; `j:(A ∧ B,Γ)` | `(A,Γ)` |
| `["and_right", f, j]` | `f = B`; `j:(A ∧ B,Γ)` | `(B,Γ)` |
| `["or_left", f, j]` | `f = A ∨ B`; `j:(A,Γ)` | `(A ∨ B,Γ)` |
| `["or_right", f, j]` | `f = A ∨ B`; `j:(B,Γ)` | `(A ∨ B,Γ)` |
| `["or_elim", f, j, k, l]` | `f = C`; `j:(A ∨ B,Γ)`; `k:(C,Δ)`; `l:(C,Θ)` | `(C, Γ ∪ (Δ \ {A}) ∪ (Θ \ {B}))` |
| `["false_elim", f, j]` | `f = C`; `j:(False,Γ)` | `(C,Γ)` |

Contexts contain formulas, not named assumption occurrences. Weakening and
contraction are admissible structural principles. Vacuous discharge and
discharging all occurrences of an identical formula are valid. Discharge
creates a new context; it cannot remove assumptions from a shared parent.
`or_elim` removes only the left disjunct from the left branch and the right
disjunct from the right branch, retaining the disjunction-producing context.
Branches need not actually use their respective branch assumption.

At the root, conclusion tree equality with the supplied claim's goal is
required, and its computed context must be a subset of the declared premises.
An empty computed context certifies a closed derivation. Extra declared
premises may be unused. Dependencies are not promised to be mathematically
minimal. No rule can introduce a closed proof of falsehood in this calculus.

## Fixed resource policy

These limits apply before acceptance and can reject valid large proofs:

| Resource | Limit |
| --- | --- |
| Bytes per input file | 2,097,152 |
| JSON container nesting per file | 96 |
| JSON values per file, counting object keys too | 200,000 |
| Decoded characters per JSON string | 128 |
| Digits per JSON integer | 9 |
| Certificate formula rows | 10,000 |
| Formula depth, atom/false depth = 1 | 64 |
| Formula occurrences across all claim trees | 10,000 |
| Proof steps | 20,000 |
| Declared distinct premises | 256 |
| Open formulas in any step's context | 256 |
| Sum of context cardinalities over all proof steps | 200,000 |

The shared interner can contain up to the sum of claim occurrences and proof
formula rows (20,000), not just the certificate row limit. DAG comparison
never unfolds shared subtrees. The CLI displays the bounded claim tree.
This is a bounded input/work policy, not an OS-level memory or time guarantee.

## CLI and receipt

```text
python -m lemqo check PROOF --claim CLAIM [--json]
python -m lemqo --version
```

| Exit code | Meaning |
| --- | --- |
| 0 | Completed verification and accepted the supplied claim/certificate pair |
| 1 | Input, inference, claim-binding, or resource-policy rejection |
| 2 | Command-line usage or input-file I/O error |
| 3 | Internal or environmental exception; verification did not complete |

On rejection, stdout is empty and stderr explains the error. With `--json`,
verification rejections emit a JSON error on stderr; usage, I/O, and internal
errors remain plain diagnostic text. Unexpected process termination and
output errors must also be treated as failure. A consumer should require
exit 0 and a complete receipt, not search logs for the word `VALID`.

A successful JSON receipt contains `status`, `verifier`, `version`, `logic`,
`claim`, `kind`, `goal`, `declared_premises`, `used_premise_indices`,
`formula_rows`, `checked_steps`, `root`, `claim_sha256`, and `proof_sha256`.
`kind` is `closed` if the retained context is empty, otherwise `conditional`.
Hashes identify exact input bytes; they are neither signatures nor proofs of
truth. All success output is constructed after checking the complete input.

The public Python API is `lemqo.verify_bytes(claim_bytes, proof_bytes)`. It
returns the same receipt or raises `lemqo.Rejection`, whose `code` identifies
the rejection category. It accepts bytes only. Other unexpected exceptions
must be treated as verification failure. Kernel-internal helpers are not a
supported interface for skipping byte-level validation.
