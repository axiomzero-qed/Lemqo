# Architecture and audit map

```text
caller-selected claim bytes     untrusted proof certificate bytes
            |                                |
            +------ strict bounded JSON -----+
                             |
                   exact format validation
                             |
               shared structural formula interner
                             |
                all ten-rule proof DAG checks
                             |
               exact goal and premise comparison
                             |
           receipt, byte hashes, and CLI success status
```

All modules in `lemqo/` belong to the end-to-end checking path. The kernel
performs no I/O and has no dependency on the CLI. `verify_bytes` is the public
boundary: parsing both inputs precedes kernel checking, which precedes receipt
creation. Each invocation builds fresh local state; no theorem cache, import
environment, or previously accepted database can affect the result.

## Optional Lean path

The optional `check-lean` command is separate from the IPL checker:

```text
caller-selected reference + certificate
        | hash binding and strict NDJSON preflight
        | offline Comparator checks of declarations, statements,
        | primitives, and axiom types
        | independent Rust Nanoda checks of every declaration
        + both stages pass -> VALID
```

The reference is selected independently by the caller. The current workflow
uses only vendored sources from the pinned OpenAI repository; it is not a
general Lean importer. Its trusted path includes preflight, Comparator, bridge,
Rust checker, and their build/runtime components. See [docs/lean.md](lean.md).

The certificate uses two topologically ordered DAGs. Formula rows permit
sharing without ambiguous parsing or exponential subtree expansion. Proof
rows permit reuse without mutating earlier judgments. Conclusion formula IDs
are explicit, while assumption dependencies are always computed internally.

Claims use readable prefix trees. A shared exact interner maps claim and proof
formulas into canonical IDs; wire IDs have no logical meaning. Hash-consing
keys are shallow tuples of connective and canonical child IDs. Python's
dictionary compares full keys, so hash collisions cannot identify unequal
formulas. Immutable context sets contain these canonical formula IDs.

For an audit, start with the rule table in [specification.md](specification.md),
then read [kernel.py](../lemqo/kernel.py) with [trust.md](trust.md). Follow
`verify_bytes` and `main` to confirm that every acceptance path reaches all
checks and that receipt data comes from the selected claim. Review the parser
and resource limits as part of the trusted path, not as disposable front-end code.

Tests and release tools live outside the verifier package. The finite-model
oracle imports only the public API and interprets claim trees independently
of the kernel. Release tooling packages an explicit file allowlist and creates
deterministic archives; it cannot add inference rules at runtime.

## Design decisions

- **Fixed propositional logic:** standard natural deduction gives a clear
  meaning and a short soundness argument. Avoiding binders and computation
  removes variable capture, substitution and reduction machinery in v0.1.
- **Python standard library:** readers can run and inspect the source without
  installing dependencies. The interpreter remains a substantial trusted
  component; a future second implementation should reduce shared failure modes.
- **JSON with exact schemas:** familiar tooling and explicit references;
  strict duplicate/type/limit checks address JSON interpretation hazards.
- **Separate claim and certificate:** the target is selected by the caller and
  compared structurally after replay. No digest or certificate assertion can
  override the expected theorem.
- **Formula-set contexts:** contraction and weakening are valid in this logic.
  This decision must be revisited for linear logic or binder-dependent rules.

This architecture borrows the independent replay idea from established proof
systems, especially Metamath/MM0. It is not a reimplementation of their full
languages or a compatible interchange format. See [research.md](research.md).
