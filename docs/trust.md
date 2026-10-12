# Trust and assurance

## Three different questions

1. **Derivation validity:** do the explicit steps derive the selected formula
   from the retained premises in the specified calculus?
2. **Formalization fidelity:** do that formula and its premises express the
   mathematics the author intended?
3. **Implementation correctness:** does this executable implement the calculus
   and bind the result to the actual input files without defects?

These questions require different evidence. Lemqo checks the first through
an implementation that must itself be scrutinized for the third. It cannot
settle the second. A trivially true implication with an impossible antecedent
can be a valid proof of an unhelpful statement. A proposition named after a
conjecture is still only an uninterpreted atom in v0.1.

Explicit claim premises are mathematical assumptions, separate from software
trust. They need not be consistent. Acceptance of `False ⊢ P` establishes
conditional entailment, not `P` without assumptions and not truth of `False`.

## Trusted boundary

To trust the end-to-end CLI result, inspect:

- [input.py](../lemqo/input.py): strict JSON decoding, duplicate-key detection,
  byte/depth/value/string bounds, and number handling.
- [kernel.py](../lemqo/kernel.py): exact schemas, formula identity, graph
  validation, the ten inference rules, immutable contexts, and goal/premise binding.
- [limits.py](../lemqo/limits.py) and [errors.py](../lemqo/errors.py): acceptance
  bounds and failure behavior.
- [api.py](../lemqo/api.py): both inputs reach the checker before a receipt exists.
- [__main__.py](../lemqo/__main__.py) and [__init__.py](../lemqo/__init__.py): file
  reading, command-line wiring, version, output, and exit status.

The Python interpreter and the relevant standard library, including JSON,
string, integer, dictionary, and immutable-set operations, are trusted too.
The OS, hardware, installed program integrity, and delivery chain remain
assumptions. SHA-256 identifies inputs; mathematical formula equality uses
full structural keys, never hashes alone. Failure of receipt hashing may
affect input identification even though it is not an inference rule.

Proof producers, editors, AI models, translators, build helpers, test oracles,
and documentation renderers do not produce trusted mathematical judgments.
Build tools still matter for delivering the intended executable. This project
contains one verifier implementation. The independent semantic test oracle
and review by a separate AI reviewer are additional evidence, not a second verifier
or a completed human audit.

The IPL project-owned checking path is small enough to read directly. We do
not claim a measured total trusted computing base smaller than Lean's, nor
that Python is formally verified. There is no machine-checked refinement proof
from this specification to the Python executable.

## Optional Lean path

The optional Lean path has a larger trusted computing base than IPL. It binds
the caller-selected reference by hash, strictly preflights certificate
NDJSON, checks declarations, statements, primitives, and axiom types against
the offline Comparator, then checks every declaration with an independent Rust
Nanoda checker. Both phases must pass for `VALID`. The comparator, bridge,
Nanoda implementation, build process, runtime, and input/reference selection
therefore join the trusted boundary. Hash binding identifies bytes; it does not
prove that the selected reference captures the intended mathematics.

The current workflow is restricted to the repository-vendored OpenAI corpus.
Three main-theorem checks remain pending. A 585-declaration smoke check and 25
native attack regressions passed on Linux; these results do not establish
general Lean support, correctness for every input, or completion of the 722
manuscripts. See [docs/lean.md](lean.md) and [docs/openai.md](openai.md).

## Soundness argument for the calculus

Maintain the invariant: every checked judgment `(C, Γ)` has an intuitionistic
natural-deduction derivation of `Γ ⊢ C`. Backward parent references give an
induction order. Exact canonical formula identity represents tree equality.

Assumptions yield `{A} ⊢ A`. The introduction and projection rules for
conjunction, introductions for disjunction, modus ponens, and falsehood
elimination preserve the invariant by their ordinary natural-deduction
rules. Context unions use admissible weakening. Repeated identical formulas
are harmless because contraction is admissible.

For implication introduction, a parent `Γ ⊢ B` yields
`Γ \ {A} ⊢ A → B`: add `A` to the context if needed, then discharge it.
Vacuous discharge is valid. In Kripke semantics, at every future world forcing
`A`, the remaining persistent assumptions and `A` establish all parent
assumptions, so the parent yields `B` there.

For disjunction elimination, set
`U = Γ ∪ (Δ \ {A}) ∪ (Θ \ {B})`. The disjunction follows from `Γ` under `U`.
If `A` holds, every assumption needed by the left branch `Δ` is available;
if `B` holds, every assumption in `Θ` is available. Each branch concludes the
same `C`, so `U ⊢ C`. The context of the disjunction-producing proof is never
discharged by this rule.

Finally, the root must have the selected goal and a context contained in the
declared claim premises. Weakening gives the advertised sequent. Empty
retained context yields a closed theorem. Since no Kripke world forces
falsehood, these rules cannot derive closed falsehood: a one-world model
already rules that out. This is a mathematical argument about the specified
calculus, not a proof that every line of the implementation is correct.

## Adversarial input and failure behavior

Treat both files as untrusted data for parsing. Treat the caller-selected
claim as the intended target only after reviewing it. A producer who controls
both the proof and the claimed target could supply a trivial theorem instead
of the theorem a reader expected.

The checker rejects unknown fields, rules and versions; invalid references;
bad rule shapes; goal replacement; undeclared open assumptions; duplicate
JSON keys; float/Boolean index aliases; malformed encoding; and policy-limit
violations. There is no code execution, file inclusion, network access, pickle
loading, or plugin mechanism driven by certificate content. All supplied
nodes validate, including unused nodes. Immutable dependency sets prevent
one branch from erasing assumptions from a reused proof.

Byte limits are applied before JSON decoding. Nesting is scanned before the
recursive decoder. Formula DAGs are interned by bounded shallow keys and never
expanded for comparison or output. Context cardinality and cumulative retained
memberships bound union/set work. The limits are fixed in the specification.

These checks do not guarantee that a process cannot exhaust resources or be
delayed by an OS, unusual file source, hostile host environment, or many
simultaneous requests. A network service should add its own process timeout,
memory/concurrency limits, and finite regular-file or bytes ingestion policy.
The caller must regard exceptions, interrupted execution, missing/partial
output, and any nonzero exit as failure. Arbitrary Python callers able to
modify module globals or execute code in the verifier process are outside
the certificate-input threat model.

## Evidence and limits

The tests exercise all rules, accepted/rejected examples, discharge and alias
regressions, strict input handling, resource bounds, and fail-closed CLI paths.
An independent prefix-tree Kripke oracle checks retained-premise entailment for
6,000 deterministic generated candidates on 145 finite world/valuation
observations. Its excluded-middle countermodel confirms that it uses
intuitionistic implication, rather than ordinary Boolean implication.

Finite tests cannot establish general soundness or eliminate all bugs. Review
the [specification](specification.md), replay the tests, compare the rules to
the code, and consider implementing a second checker in a different language.
Any extension involving binders, equality, computation, axioms, definitions,
or external proof formats needs a new soundness and trust analysis.
