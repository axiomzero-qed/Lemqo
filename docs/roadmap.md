<a id="roadmap"></a>

# Roadmap / 路线图

v0.1 established the IPL verification path, which remains unchanged in v0.2.
v0.2 adds an optional, experimental Lean certificate path for a small,
repository-vendored corpus. Three selected OpenAI theorem targets passed
independent checking. The two paths have different trusted bases and scopes.

v0.1 建立了 IPL 验证路径，该路径在 v0.2 中保持不变。v0.2 为小型仓库内 vendored 语料增加了可选的实验性 Lean 证明证书路径。三个选定的 OpenAI 定理目标通过了独立检查。两条路径具有不同的可信计算基础（TCB）和适用范围。

Next work should increase assurance before increasing expressive power:

下一步应先提升保证程度，再扩大表达能力：

1. Community audit of the calculus, parser, resource policy and implementation;
   preserve minimized regression cases for every discovered defect.
   社区审计演算、解析器、资源策略和实现；对发现的每个缺陷保留最小化回归用例。
2. A second checker in a different language and differential tests against the
   same versioned certificate corpus. Do not share logical implementation code.
   使用另一种语言实现第二个检查器，并针对相同的版本化证明证书语料开展差分测试。不要共享逻辑实现代码。
3. A machine-checked specification and refinement/soundness proof covering
   formula representation, parsing, checking, and claim binding.
   建立机器检查的规范及精化/健全性证明，覆盖公式表示、解析、检查和 claim 绑定。
4. Evaluate whether adopting MM0, OpenTheory, or another existing format/kernel
   is better than extending this propositional kernel.
   评估采用 MM0、OpenTheory 或其他现有格式/内核，是否优于扩展此命题内核。
5. Only then design quantified mathematics, definitions and translation
   contracts, with explicit freshness, axiom, model and statement-fidelity review.
   只有之后才设计含量词的数学、定义和翻译约定，并明确审查新鲜性、公理、模型与陈述忠实度。

Further Lean work requires a stated supported fragment, preserved theorem
statement and assumptions, reproducible translation, and independent target
checking. The current path is not general Lean support and does not claim that
all 722 manuscripts are formalized or checked. Broad interchange remains a
research objective, not a compatibility or completeness claim.

后续 Lean 工作需要明确说明支持片段、保留定理陈述和假设、提供可复现的翻译，并独立检查目标。当前路径不提供通用 Lean 支持，也不声称全部 722 篇手稿均已形式化或检查。广泛互操作仍是研究目标，不构成兼容性或完备性声明。
