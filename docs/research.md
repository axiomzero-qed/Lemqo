# Research and design notes

*Sources checked 2026-10-12. This note records design context, not a claim that Lemqo has been integrated with any system below.*

## Scope and meaning of acceptance

Lemqo v0.1 checks derivations in one fixed intuitionistic propositional natural-deduction calculus. Its rule set is the assumption rule; implication introduction and elimination; conjunction introduction and its two eliminations; disjunction's two introductions and elimination; and falsehood elimination. Together these are ten rules. The supported language has no axioms, definitions, quantifiers, equality, or translation layer. Acceptance means only that the submitted derivation follows these rules from its listed assumptions. It does not establish that a formula captures an intended informal claim, or that assumptions are true.

This narrow scope makes the calculus and checking behavior inspectable. It deliberately has much less expressive power than general-purpose systems such as Lean, Metamath, or HOL. We make no quantitative claim that Lemqo's total trusted computing base is smaller than theirs: Lemqo still depends on the correctness of its Python runtime and interpreter, as well as its own parser, representation, and checker. A successful check is evidence relative to that implementation and runtime, not a machine-checked proof of the checker's correctness.

## Comparison

| System | What acceptance establishes | Design strengths | Important limits |
| --- | --- | --- | --- |
| **Lemqo** | A derivation follows the fixed intuitionistic propositional rules from its assumptions. | Small, explicit scope; no user-added axioms or translation claims in v0.1. | Cannot express general mathematics, quantifiers, equality, or definitions. Trust includes Python and Lemqo's parser/checker implementation. |
| **Lean 4** | The kernel accepts a proof term in Lean's dependent type theory, relative to the imported environment and axioms. Tactics generate terms checked by the kernel. | Highly expressive, extensible automation and a substantial formalization ecosystem; independent kernel implementations are possible. | Axiom and dependency choices matter. Kernel checking does not establish that a formal statement matches the author's intended meaning. Some native-computation mechanisms may add compiler-related trust; consult version-specific documentation. |
| **Metamath** | Explicit proof steps follow the selected database's axioms and substitution rules. | Simple proof language and multiple independent verifier implementations; adaptable to different formal systems. | The selected database determines the logic and assumptions. Verifier acceptance alone does not settle whether those axioms are appropriate or the formalization is faithful. Formula-string and grammar choices require care. |
| **Metamath Zero (MM0)** | A proof artifact checks against a separate specification containing axioms, definitions, and theorem statements. | Separates an auditable specification from proof data; designed for efficient checking and has more than one verifier implementation. | Its specification warns about stability and labels a paper proof/formalization of its semantic assurance claim as forthcoming; this is distinct from proving a particular implementation correct. Project commentary is not independent evidence about other systems. |
| **HOL Light / OpenTheory** | HOL Light's trusted theorem-producing functions construct theorems in higher-order logic; OpenTheory records inference steps for exportable proof packages. | A narrow theorem-producing path supports automation and extensive libraries; proof logging enables package replay. | The logic, axioms, definitions, host implementation, and library dependencies remain part of the assurance picture. Statements still require human scrutiny for intended meaning. |

Across systems, proof checking and interpretation are separate questions: the checker establishes derivability inside a formal system; people must also assess the formal statement, definitions, dependencies, and assumptions against the intended claim. A system's logical kernel is only part of its trusted base. Host runtime, parser or artifact handling, compiler-assisted computation, and imported axioms or libraries can affect what a successful check means.

## Primary sources

- Lean Language Reference, including kernel and tactic architecture: <https://lean-lang.org/doc/reference/latest/>. The version shown when consulted was 4.35.0-rc4; details can change between releases.
- Lean reference on axioms: <https://lean-lang.org/doc/reference/latest/Axioms/>.
- Lean proof validation guidance, including dependency and native-computation caveats: <https://github.com/leanprover/downstream-lean4/blob/master/reference-manual/Manual/ValidatingProofs.lean>.
- Metamath home page, including the independently implemented verifiers used to check the Proof Explorer: <https://us.metamath.org/>.
- Metamath book, language and proof-verification account: <https://us.metamath.org/downloads/metamath.pdf>.
- Metamath Proof Explorer, including its explanation of axioms and schemes: <https://us.metamath.org/mpeuni/mmset.html>.
- Metamath Zero specification and its current stability and conformance-status notes: <https://github.com/digama0/mm0/blob/master/mm0.md>.
- Metamath Zero project repository, design overview and verifier implementations: <https://github.com/digama0/mm0>.
- Metamath Zero paper, describing the proof format and its performance goals: <https://arxiv.org/abs/1910.10703>.
- HOL Light official site: <https://hol-light.github.io/>.
- HOL Light's core theorem-producing implementation: <https://github.com/jrh13/hol-light/blob/master/fusion.ml>.
- OpenTheory project, portable theorem packages and proof articles: <https://www.gilith.com/opentheory/>.
- HOL4 Developers' Manual on its OpenTheory proof-logging kernel: <https://hol-theorem-prover.org/docs/trindemossen-2/Developers/>.
