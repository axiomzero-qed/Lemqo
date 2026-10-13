<a id="trust-and-assurance"></a>

# Trust and assurance / 信任与保证

<a id="three-different-questions"></a>

## Three different questions / 三个不同问题

1. **Derivation validity:** do the explicit steps derive the selected formula
   from the retained premises in the specified calculus?
2. **Formalization fidelity:** do that formula and its premises express the
   mathematics the author intended?
3. **Implementation correctness:** does this executable implement the calculus
   and bind the result to the actual input files without defects?

1. **推导有效性：**显式步骤是否在指定演算中，从保留的前提推导出选定公式？
2. **形式化忠实度：**该公式及其前提是否表达作者原本想描述的数学内容？
3. **实现正确性：**可执行程序是否无缺陷地实现演算，并将结果绑定到实际输入文件？

These questions require different evidence. Lemqo checks the first through
an implementation that must itself be scrutinized for the third. It cannot
settle the second. A trivially true implication with an impossible antecedent
can be a valid proof of an unhelpful statement. A proposition named after a
conjecture is still only an uninterpreted atom in the IPL path.

这三个问题需要不同证据。Lemqo 通过程序检查第一个问题，但程序本身必须接受第三个问题的审查；它不能解决第二个问题。前件不可能成立的蕴含式可以平凡地为真，对应的证明有效，却可能没有预期意义。在 IPL 路径中，以猜想命名的命题仍只是没有解释的原子。

Explicit claim premises are mathematical assumptions, separate from software
trust. They need not be consistent. Acceptance of `False ⊢ P` establishes
conditional entailment, not `P` without assumptions and not truth of `False`.

陈述中显式列出的前提是数学假设，与对软件的信任不同，也不要求彼此一致。接受 `False ⊢ P` 只确立条件性蕴涵，不确立无假设的 `P`，也不说明 `False` 为真。

<a id="trusted-boundary"></a>

## Trusted boundary / 可信边界

To trust the end-to-end CLI result, inspect:

要信任命令行从输入到结果的完整流程，需要检查：

- [input.py](../lemqo/input.py): strict JSON decoding, duplicate-key detection,
  byte/depth/value/string bounds, and number handling.
- [kernel.py](../lemqo/kernel.py): exact schemas, formula identity, graph
  validation, the ten inference rules, immutable contexts, and goal/premise binding.
- [limits.py](../lemqo/limits.py) and [errors.py](../lemqo/errors.py): acceptance
  bounds and failure behavior.
- [api.py](../lemqo/api.py): both inputs reach the checker before a receipt exists.
- [__main__.py](../lemqo/__main__.py) and [__init__.py](../lemqo/__init__.py): file
  reading, command-line wiring, version, output, and exit status.

- [input.py](../lemqo/input.py)：严格 JSON 解码、重复键检测、字节/深度/值数/字符串限制及数字处理。
- [kernel.py](../lemqo/kernel.py)：精确模式、公式身份、图验证、十条推理规则、不可变上下文以及目标和前提绑定。
- [limits.py](../lemqo/limits.py) 和 [errors.py](../lemqo/errors.py)：验收限制与失败行为。
- [api.py](../lemqo/api.py)：在生成回执前，将两份输入都交给验证器。
- [__main__.py](../lemqo/__main__.py) 和 [__init__.py](../lemqo/__init__.py)：文件读取、命令行连接、版本、输出和退出状态。

The Python interpreter and the relevant standard library, including JSON,
string, integer, dictionary, and immutable-set operations, are trusted too.
The OS, hardware, installed program integrity, and delivery chain remain
assumptions. SHA-256 identifies inputs; mathematical formula equality uses
full structural keys, never hashes alone. Failure of receipt hashing may
affect input identification even though it is not an inference rule.

Python 解释器及相关标准库也在信任范围内，包括 JSON、字符串、整数、字典和不可变集合操作。操作系统、硬件、已安装程序的完整性以及交付链仍是必要假设。SHA-256 标识输入；数学公式相等依赖完整结构键，绝不只依赖哈希。回执哈希计算失败可能影响输入标识，虽然哈希不是推理规则。

Proof producers, editors, AI models, translators, build helpers, test oracles,
and documentation renderers do not produce trusted mathematical judgments.
Build tools still matter for delivering the intended executable. The IPL path
contains one verifier implementation. The independent semantic test oracle
and review by a separate AI reviewer are additional evidence, not a second IPL
verifier or a completed human audit.

证明生成器、编辑器、AI 模型、翻译器、构建辅助工具、测试语义参照程序和文档渲染器不产生需要信任的数学判断。不过，构建工具仍影响交付的是否是预期程序。IPL 路径只有一个验证器实现。独立语义测试参照和另一位 AI 审查者的检查只是补充证据，既不等于第二个 IPL 验证器，也不等于已完成的人类审计。

The IPL project-owned checking path is small enough to read directly. We do
not claim a measured total trusted computing base smaller than Lean's, nor
that Python is formally verified. There is no machine-checked refinement proof
from this specification to the Python executable.

项目自有的 IPL 检查代码足够小，可以直接通读。我们不声称已测得的整体可信计算基础小于 Lean，也不声称 Python 已得到形式化验证。目前没有从本规范到 Python 可执行程序的机器检查精化证明。

<a id="optional-lean-path"></a>

## Optional Lean path / 可选 Lean 路径

The optional Lean path has a larger trusted computing base than IPL. It binds
the caller-selected reference by hash, strictly preflights certificate
NDJSON, checks declarations, statements, primitives, and axiom types against
the offline Comparator, then checks every declaration with an independent Rust
Nanoda checker. Both phases must pass for `VALID`. The comparator, bridge,
Nanoda implementation, build process, runtime, and input/reference selection
therefore join the trusted boundary. Hash binding identifies bytes; it does not
prove that the selected reference captures the intended mathematics.

可选 Lean 路径的可信计算基础大于 IPL。它通过哈希绑定调用方选择的参考导出，严格预检证书 NDJSON，借助离线 Comparator 检查声明、陈述、原语和公理类型，再由独立 Rust 验证器 Nanoda 检查每一条声明。两个阶段均通过后才能输出 `VALID`。因此，Comparator、桥接程序、Nanoda 实现、构建过程、运行环境及输入/参考选择都进入可信边界。哈希绑定只能标识字节，不能证明参考导出表达了预期数学内容。

The current workflow is restricted to the repository-vendored OpenAI corpus.
Three selected main targets passed, with 22,252, 41,966, and 70,651 declarations.
A 585-declaration smoke check and 30 native/public-API regression cases also
passed on Linux. These results do not establish general Lean support,
correctness for every input, or completion of the 722 manuscripts. See
[docs/lean.md](lean.md) and [docs/openai.md](openai.md).

当前流程仅针对仓库固定保存的 OpenAI 语料快照。三个选定主目标已通过验证，分别包含 22,252、41,966 和 70,651 条声明。585 条声明的冒烟检查以及 30 个原生工具/公开 API 回归案例也已在 Linux 上通过。这些结果不确立通用 Lean 支持、所有输入上的正确性，也不代表完成了全部 722 篇稿件的验证。参见 [docs/lean.md](lean.md) 和 [docs/openai.md](openai.md)。

<a id="soundness-argument-for-the-calculus"></a>

## Soundness argument for the calculus / 演算的健全性论证

Maintain the invariant: every checked judgment `(C, Γ)` has an intuitionistic
natural-deduction derivation of `Γ ⊢ C`. Backward parent references give an
induction order. Exact canonical formula identity represents tree equality.

维护如下不变量：每个已检查判断 `(C, Γ)` 都有一个直觉主义自然演绎推导 `Γ ⊢ C`。父步骤只允许向后引用，因此提供归纳顺序。精确的公式规范化身份代表树结构相等。

Assumptions yield `{A} ⊢ A`. The introduction and projection rules for
conjunction, introductions for disjunction, modus ponens, and falsehood
elimination preserve the invariant by their ordinary natural-deduction
rules. Context unions use admissible weakening. Repeated identical formulas
are harmless because contraction is admissible.

假设规则产生 `{A} ⊢ A`。合取引入和投影、析取引入、肯定前件式以及假消去，都按通常的自然演绎规则保持不变量。上下文并集使用可容许的弱化。相同公式的重复不影响结论，因为收缩是可容许的。

For implication introduction, a parent `Γ ⊢ B` yields
`Γ \ {A} ⊢ A → B`: add `A` to the context if needed, then discharge it.
Vacuous discharge is valid. In Kripke semantics, at every future world forcing
`A`, the remaining persistent assumptions and `A` establish all parent
assumptions, so the parent yields `B` there.

蕴含引入从父判断 `Γ ⊢ B` 得到 `Γ \ {A} ⊢ A → B`：必要时先向上下文加入 `A`，再解除它。未实际使用该假设的解除同样有效。在 Kripke 语义中，对每个强制 `A` 的后继世界，其余具有持久性的假设与 `A` 一起保证全部父假设成立，因而父推导在那里给出 `B`。

For disjunction elimination, set
`U = Γ ∪ (Δ \ {A}) ∪ (Θ \ {B})`. The disjunction follows from `Γ` under `U`.
If `A` holds, every assumption needed by the left branch `Δ` is available;
if `B` holds, every assumption in `Θ` is available. Each branch concludes the
same `C`, so `U ⊢ C`. The context of the disjunction-producing proof is never
discharged by this rule.

析取消去令 `U = Γ ∪ (Δ \ {A}) ∪ (Θ \ {B})`。在上下文 `U` 下，可由 `Γ` 推出析取式。若 `A` 成立，左分支所需的 `Δ` 中所有假设均可使用；若 `B` 成立，右分支的 `Θ` 中所有假设均可使用。两个分支都得出同一个 `C`，因此 `U ⊢ C`。本规则绝不解除产生析取式的证明所依赖的上下文。

Finally, the root must have the selected goal and a context contained in the
declared claim premises. Weakening gives the advertised sequent. Empty
retained context yields a closed theorem. Since no Kripke world forces
falsehood, these rules cannot derive closed falsehood: a one-world model
already rules that out. This is a mathematical argument about the specified
calculus, not a proof that every line of the implementation is correct.

最后，根步骤必须具有选定目标，且上下文包含于声明的陈述前提。弱化给出对外声明的相继式。保留上下文为空时得到闭合定理。由于任何 Kripke 世界都不强制假，这些规则不可能导出闭合的假；单世界模型已足以排除这种情况。这是对指定演算的数学论证，不是对实现每一行都正确的证明。

<a id="adversarial-input-and-failure-behavior"></a>

## Adversarial input and failure behavior / 恶意输入与失败行为

Treat both files as untrusted data for parsing. Treat the caller-selected
claim as the intended target only after reviewing it. A producer who controls
both the proof and the claimed target could supply a trivial theorem instead
of the theorem a reader expected.

解析时，两份文件都作为不可信数据处理。调用方选择的陈述只有经审查后才应视为预期目标。若生成者同时控制证明和声称要证明的目标，就可以提交一个平凡定理，而非读者所期待的定理。

The checker rejects unknown fields, rules and versions; invalid references;
bad rule shapes; goal replacement; undeclared open assumptions; duplicate
JSON keys; float/Boolean index aliases; malformed encoding; and policy-limit
violations. There is no code execution, file inclusion, network access, pickle
loading, or plugin mechanism driven by certificate content. All supplied
nodes validate, including unused nodes. Immutable dependency sets prevent
one branch from erasing assumptions from a reused proof.

验证器拒绝未知字段、规则或版本，无效引用，规则形状错误，目标替换，未声明的开放假设，重复 JSON 键，浮点/布尔索引别名，非法编码及超出策略限制的输入。证书内容不能驱动代码执行、文件包含、网络访问、pickle 加载或插件机制。所有输入节点都须通过验证，包括未使用的节点。不可变依赖集合防止某一分支擦除被复用证明的假设。

Byte limits are applied before JSON decoding. Nesting is scanned before the
recursive decoder. Formula DAGs are interned by bounded shallow keys and never
expanded for comparison or output. Context cardinality and cumulative retained
memberships bound union/set work. The limits are fixed in the specification.

JSON 解码前先限制字节数，递归解码前先扫描嵌套深度。公式 DAG 通过有界浅层键进行驻留，不会因比较或输出而展开。上下文大小及累计保留成员数限制并集和集合操作的工作量。这些限制固定写在规范中。

These checks do not guarantee that a process cannot exhaust resources or be
delayed by an OS, unusual file source, hostile host environment, or many
simultaneous requests. A network service should add its own process timeout,
memory/concurrency limits, and finite regular-file or bytes ingestion policy.
The caller must regard exceptions, interrupted execution, missing/partial
output, and any nonzero exit as failure. Arbitrary Python callers able to
modify module globals or execute code in the verifier process are outside
the certificate-input threat model.

这些检查不能保证进程不会耗尽资源，也不能保证它不会因操作系统、特殊文件来源、恶意宿主环境或大量并发请求而延迟。网络服务应另设进程超时、内存/并发限制，以及有限普通文件或字节数据的输入策略。调用方必须将异常、中断、缺失或不完整输出以及任何非零退出码视为失败。能够修改模块全局变量或在验证器进程中执行代码的任意 Python 调用方，不在证书输入威胁模型之内。

<a id="evidence-and-limits"></a>

## Evidence and limits / 证据与局限

The tests exercise all rules, accepted/rejected examples, discharge and alias
regressions, strict input handling, resource bounds, and fail-closed CLI paths.
An independent prefix-tree Kripke oracle checks retained-premise entailment for
6,000 deterministic generated candidates on 145 finite world/valuation
observations. Its excluded-middle countermodel confirms that it uses
intuitionistic implication, rather than ordinary Boolean implication.

测试覆盖全部规则、接受/拒绝示例、假设解除和别名回归、严格输入处理、资源限制以及命令行失败时拒绝的行为。独立的前缀树 Kripke 语义参照在 145 个有限世界/赋值观测上，检查 6,000 个确定性生成候选的保留前提蕴涵关系。其排中律反模型确认使用的是直觉主义蕴含，而非普通布尔蕴含。

Finite tests cannot establish general soundness or eliminate all bugs. Review
the [specification](specification.md), replay the tests, compare the rules to
the code, and consider implementing a second checker in a different language.
Any extension involving binders, equality, computation, axioms, definitions,
or external proof formats needs a new soundness and trust analysis.

有限测试不能确立一般健全性，也不能排除全部缺陷。请阅读[规范](specification.md)、重跑测试、对照规则与代码，并考虑用另一种语言实现第二个验证器。任何涉及绑定变量、相等、计算、公理、定义或外部证明格式的扩展，都需要新的健全性和信任分析。
