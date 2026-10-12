# Roadmap

v0.1 establishes one complete verification path: specified logic, explicit
certificate, caller-selected claim, checked derivation, and reproducible
delivery. Its supported mathematics is propositional reasoning only.

Next work should increase assurance before increasing expressive power:

1. Community audit of the calculus, parser, resource policy and implementation;
   preserve minimized regression cases for every discovered defect.
2. A second checker in a different language and differential tests against the
   same versioned certificate corpus. Do not share logical implementation code.
3. A machine-checked specification and refinement/soundness proof covering
   formula representation, parsing, checking, and claim binding.
4. Evaluate whether adopting MM0, OpenTheory, or another existing format/kernel
   is better than extending this propositional kernel.
5. Only then design quantified mathematics, definitions and translation
   contracts, with explicit freshness, axiom, model and statement-fidelity review.

A Lean or other-system exporter will require a stated supported fragment,
preserved theorem statement and assumptions, reproducible translation, and
independent target checking. v0.1 provides no such exporter. Broad interchange
is a research objective, not an existing compatibility or completeness claim.
