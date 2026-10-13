<a id="research-and-design-notes"></a>

# Research and design notes / 研究与设计说明

*Sources checked 2026-10-12. This note records design context, not a claim that Lemqo has been integrated with any system below.*

*来源核查日期：2026-10-12。本说明记录设计背景，并不表示 Lemqo 已与下列任何系统集成。*

<a id="scope-and-meaning-of-acceptance"></a>

## Scope and meaning of acceptance / 范围与接受的含义

Lemqo v0.1 checks derivations in one fixed intuitionistic propositional natural-deduction calculus. Its rule set is the assumption rule; implication introduction and elimination; conjunction introduction and its two eliminations; disjunction's two introductions and elimination; and falsehood elimination. Together these are ten rules. The supported language has no axioms, definitions, quantifiers, equality, or translation layer. Acceptance means only that the submitted derivation follows these rules from its listed assumptions. It does not establish that a formula captures an intended informal claim, or that assumptions are true.

Lemqo v0.1 检查一种固定的直觉主义命题自然演绎演算中的推导。规则集包括假设规则；蕴涵引入和消去；合取引入及两种消去；析取的两种引入和消去；以及假消去，共十条规则。该语言不包含公理、定义、量词、等号或翻译层。接受仅表示提交的推导遵循这些规则，并由所列假设推出。这并不能证明某个公式准确表达了预期的非形式化待核验陈述，也不能证明假设为真。

This narrow scope makes the calculus and checking behavior inspectable. It deliberately has much less expressive power than general-purpose systems such as Lean, Metamath, or HOL. We make no quantitative claim that Lemqo's total trusted computing base is smaller than theirs: Lemqo still depends on the correctness of its Python runtime and interpreter, as well as its own parser, representation, and checker. A successful check is evidence relative to that implementation and runtime, not a machine-checked proof of the checker's correctness.

这一狭窄范围使演算和检查行为都便于审查。与 Lean、Metamath 或 HOL 等通用系统相比，它的表达能力刻意弱得多。我们不定量声称 Lemqo 的整体可信计算基础比这些系统更小：Lemqo 仍依赖 Python 运行时和解释器的正确性，也依赖自身解析器、表示方式及检查器。检查成功只能在该实现及其运行时的前提下提供证据，并非对检查器正确性的机器检查证明。

<a id="comparison"></a>

## Comparison / 对比

| System / 系统 | What acceptance establishes / 接受结果所确立的内容 | Design strengths / 设计优势 | Important limits / 重要限制 |
| --- | --- | --- | --- |
| **Lemqo** | A derivation follows the fixed intuitionistic propositional rules from its assumptions. / 推导遵循固定的直觉主义命题规则，并由其假设推出。 | Small, explicit scope; no user-added axioms or translation claims in v0.1. / 范围小且明确；v0.1 不允许用户添加公理，也不声称完成翻译。 | Cannot express general mathematics, quantifiers, equality, or definitions. Trust includes Python and Lemqo's parser/checker implementation. / 无法表达一般数学、量词、等号或定义。可信基础包括 Python 以及 Lemqo 的解析器/检查器实现。 |
| **Lean 4** | The kernel accepts a proof term in Lean's dependent type theory, relative to the imported environment and axioms. Tactics generate terms checked by the kernel. / 相对于导入环境和公理，内核接受 Lean 依赖类型论中的证明项。策略生成的项由内核检查。 | Highly expressive, extensible automation and a substantial formalization ecosystem; independent kernel implementations are possible. / 表达能力强、自动化可扩展，且拥有庞大的形式化生态；也可以实现独立内核。 | Axiom and dependency choices matter. Kernel checking does not establish that a formal statement matches the author's intended meaning. Some native-computation mechanisms may add compiler-related trust; consult version-specific documentation. / 公理和依赖项的选择会影响结果。内核检查不能证明形式陈述符合作者本意。某些原生计算机制可能引入对编译器的信任；应查阅对应版本文档。 |
| **Metamath** | Explicit proof steps follow the selected database's axioms and substitution rules. / 显式证明步骤遵循所选数据库的公理和代换规则。 | Simple proof language and multiple independent verifier implementations; adaptable to different formal systems. / 证明语言简单，存在多个独立验证器实现；可适配不同形式系统。 | The selected database determines the logic and assumptions. Verifier acceptance alone does not settle whether those axioms are appropriate or the formalization is faithful. Formula-string and grammar choices require care. / 所选数据库决定逻辑和假设。仅凭验证器接受，无法确定公理是否恰当或形式化是否忠实。公式字符串和语法的选择需要谨慎。 |
| **Metamath Zero (MM0)** | A proof artifact checks against a separate specification containing axioms, definitions, and theorem statements. / 证明工件根据另一份包含公理、定义和定理陈述的规范进行检查。 | Separates an auditable specification from proof data; designed for efficient checking and has more than one verifier implementation. / 将可审计规范与证明数据分开；为高效检查而设计，且有多个验证器实现。 | Its specification warns about stability and labels a paper proof/formalization of its semantic assurance claim as forthcoming; this is distinct from proving a particular implementation correct. Project commentary is not independent evidence about other systems. / 规范对稳定性作出警示，并将语义保证待核验陈述的论文证明/形式化标为即将推出；这与证明具体实现正确不同。项目说明不是有关其他系统的独立证据。 |
| **HOL Light / OpenTheory** | HOL Light's trusted theorem-producing functions construct theorems in higher-order logic; OpenTheory records inference steps for exportable proof packages. / HOL Light 的可信定理生成函数在高阶逻辑中构造定理；OpenTheory 记录推理步骤，以形成可导出的证明包。 | A narrow theorem-producing path supports automation and extensive libraries; proof logging enables package replay. / 范围狭窄的定理生成路径支持自动化和丰富的库；证明日志可用于重放证明包。 | The logic, axioms, definitions, host implementation, and library dependencies remain part of the assurance picture. Statements still require human scrutiny for intended meaning. / 逻辑、公理、定义、宿主实现和库依赖仍属于保证评估范围。陈述是否符合预期含义仍需人工审查。 |

Across systems, proof checking and interpretation are separate questions: the checker establishes derivability inside a formal system; people must also assess the formal statement, definitions, dependencies, and assumptions against the intended claim. A system's logical kernel is only part of its trusted base. Host runtime, parser or artifact handling, compiler-assisted computation, and imported axioms or libraries can affect what a successful check means.

在各类系统中，证明检查与解释是两个不同问题：检查器确立的是形式系统内部的可推导性；人还必须根据预期待核验陈述评估形式陈述、定义、依赖项和假设。系统的逻辑内核只是其可信基础的一部分。宿主运行时、解析器或工件处理、编译器辅助计算，以及导入的公理或库，都会影响检查成功所代表的含义。

<a id="primary-sources"></a>

## Primary sources / 一手来源

- Lean Language Reference, including kernel and tactic architecture: <https://lean-lang.org/doc/reference/latest/>. The version shown when consulted was 4.35.0-rc4; details can change between releases.
  Lean 语言参考（包括内核和策略架构）：<https://lean-lang.org/doc/reference/latest/>。查阅时显示的版本为 4.35.0-rc4；具体内容可能随版本变化。
- Lean reference on axioms: <https://lean-lang.org/doc/reference/latest/Axioms/>.
  Lean 关于公理的参考文档：<https://lean-lang.org/doc/reference/latest/Axioms/>。
- Lean proof validation guidance, including dependency and native-computation caveats: <https://github.com/leanprover/downstream-lean4/blob/master/reference-manual/Manual/ValidatingProofs.lean>.
  Lean 证明验证指南，包含依赖项和原生计算方面的注意事项：<https://github.com/leanprover/downstream-lean4/blob/master/reference-manual/Manual/ValidatingProofs.lean>。
- Metamath home page, including the independently implemented verifiers used to check the Proof Explorer: <https://us.metamath.org/>.
  Metamath 首页，介绍了用于检查 Proof Explorer 的独立验证器实现：<https://us.metamath.org/>。
- Metamath book, language and proof-verification account: <https://us.metamath.org/downloads/metamath.pdf>.
  Metamath 书籍，对语言和证明验证作出说明：<https://us.metamath.org/downloads/metamath.pdf>。
- Metamath Proof Explorer, including its explanation of axioms and schemes: <https://us.metamath.org/mpeuni/mmset.html>.
  Metamath Proof Explorer，包含对公理和公理模式的说明：<https://us.metamath.org/mpeuni/mmset.html>。
- Metamath Zero specification and its current stability and conformance-status notes: <https://github.com/digama0/mm0/blob/master/mm0.md>.
  Metamath Zero 规范及其当前关于稳定性和一致性状态的说明：<https://github.com/digama0/mm0/blob/master/mm0.md>。
- Metamath Zero project repository, design overview and verifier implementations: <https://github.com/digama0/mm0>.
  Metamath Zero 项目仓库，包含设计概述和验证器实现：<https://github.com/digama0/mm0>。
- Metamath Zero paper, describing the proof format and its performance goals: <https://arxiv.org/abs/1910.10703>.
  Metamath Zero 论文，介绍证明格式及其性能目标：<https://arxiv.org/abs/1910.10703>。
- HOL Light official site: <https://hol-light.github.io/>.
  HOL Light 官方网站：<https://hol-light.github.io/>。
- HOL Light's core theorem-producing implementation: <https://github.com/jrh13/hol-light/blob/master/fusion.ml>.
  HOL Light 的核心定理生成实现：<https://github.com/jrh13/hol-light/blob/master/fusion.ml>。
- OpenTheory project, portable theorem packages and proof articles: <https://www.gilith.com/opentheory/>.
  OpenTheory 项目，提供可移植定理包和证明文档：<https://www.gilith.com/opentheory/>。
- HOL4 Developers' Manual on its OpenTheory proof-logging kernel: <https://hol-theorem-prover.org/docs/trindemossen-2/Developers/>.
  HOL4 开发者手册中关于其 OpenTheory 证明日志内核的章节：<https://hol-theorem-prover.org/docs/trindemossen-2/Developers/>。
