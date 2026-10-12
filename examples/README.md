# Examples

Every proof is checked against its matching `NAME.claim.json`. All files use
the fixed format described in the [specification](../docs/specification.md).
Run commands from the repository root:

```sh
python -m lemqo check examples/identity.proof.json --claim examples/identity.claim.json
```

| Name | Formal result | Outcome |
| --- | --- | --- |
| identity | `P → P` | Closed proof |
| composition | `(P → Q) → ((Q → R) → (P → R))` | Closed proof |
| conjunction | `(P ∧ Q) → (Q ∧ P)` | Closed proof |
| disjunction | `(P ∨ Q) → (Q ∨ P)` | Closed proof |
| distributivity | `(P ∧ (Q ∨ R)) → ((P ∧ Q) ∨ (P ∧ R))` | Closed proof |
| modus_ponens | `P → Q, P ⊢ Q` | Conditional on both premises |
| ex_falso | `⊥ → P` | Closed proof; it does not prove `⊥` |
| identity.invalid | A forged implication elimination targeting `P → P` | Rejected inference |
| false.invalid | An open assumption submitted as a closed proof of `⊥` | Rejected undeclared assumption |

In the identity certificate, formula row 0 denotes `P`, and row 1 denotes
`P → P`. Step 0 assumes `P`. Step 1 applies implication introduction and
discharges that assumption. The final open context is empty.

The disjunction example first assumes `P ∨ Q`. In its left branch, an assumed
`P` gives `Q ∨ P`; in its right branch, an assumed `Q` gives the same result.
`or_elim` removes the respective branch assumptions but retains `P ∨ Q`.
Implication introduction then discharges the remaining assumption.

The `modus_ponens` receipt lists used premise indices `[0, 1]`. This reports
dependencies of this derivation and does not establish either premise's truth.
