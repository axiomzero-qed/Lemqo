# Roadmap

v0.1 established the IPL verification path, which remains unchanged in v0.2.
v0.2 adds an optional, experimental Lean certificate path for a small,
repository-vendored corpus. Three selected OpenAI theorem targets passed
independent checking. The two paths have different trusted bases and scopes.

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

Further Lean work requires a stated supported fragment, preserved theorem
statement and assumptions, reproducible translation, and independent target
checking. The current path is not general Lean support and does not claim that
all 722 manuscripts are formalized or checked. Broad interchange remains a
research objective, not a compatibility or completeness claim.
