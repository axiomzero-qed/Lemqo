<a id="architecture-and-audit-map"></a>

# Architecture and audit map / 架构与审计路线图

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

`lemqo/` 中的所有模块都属于端到端检查路径。内核不执行输入/输出，也不依赖 CLI。`verify_bytes` 是公开边界：先解析两个输入，再进行内核检查，最后创建回执。每次调用都会构建全新的本地状态；定理缓存、导入环境或先前已接受的数据库都不会影响结果。

<a id="optional-lean-path"></a>

## Optional Lean path / 可选 Lean 路径

The optional `check-lean` command is separate from the IPL checker:

可选的 `check-lean` 命令与 IPL 检查器彼此独立：

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

参考文件由调用方独立选定。当前工作流只使用固定版本 OpenAI 仓库中 vendored 的源文件；它并非通用 Lean 导入器。其可信路径包括预检、Comparator、桥接层、Rust 检查器以及它们的构建/运行时组件。参见 [docs/lean.md](lean.md)。

The certificate uses two topologically ordered DAGs. Formula rows permit
sharing without ambiguous parsing or exponential subtree expansion. Proof
rows permit reuse without mutating earlier judgments. Conclusion formula IDs
are explicit, while assumption dependencies are always computed internally.

证书使用两个按拓扑顺序排列的有向无环图（DAG）。公式行允许共享子结构，同时避免解析歧义或子树规模指数膨胀。证明行允许复用，而不会改变先前的判断。结论公式 ID 显式给出；假设依赖则始终由系统内部计算。

Claims use readable prefix trees. A shared exact interner maps claim and proof
formulas into canonical IDs; wire IDs have no logical meaning. Hash-consing
keys are shallow tuples of connective and canonical child IDs. Python's
dictionary compares full keys, so hash collisions cannot identify unequal
formulas. Immutable context sets contain these canonical formula IDs.

待核验陈述使用可读的前缀树表示。共享的精确驻留表将待核验陈述与证明中的公式映射为规范 ID；传输格式中的 ID 不具有逻辑含义。哈希驻留键是由联结词和规范子节点 ID 构成的浅层元组。Python 字典会比较完整键，因此哈希冲突不会把不相等的公式识别为同一公式。不可变上下文集合包含这些规范公式 ID。

For an audit, start with the rule table in [specification.md](specification.md),
then read [kernel.py](../lemqo/kernel.py) with [trust.md](trust.md). Follow
`verify_bytes` and `main` to confirm that every acceptance path reaches all
checks and that receipt data comes from the selected claim. Review the parser
and resource limits as part of the trusted path, not as disposable front-end code.

审计时，先阅读 [specification.md](specification.md) 中的规则表，再结合 [trust.md](trust.md) 阅读 [kernel.py](../lemqo/kernel.py)。沿着 `verify_bytes` 和 `main` 的调用路径，确认每条接受路径都会经过所有检查，且回执数据来自选定的待核验陈述。解析器和资源限制也属于可信路径的一部分，应纳入审查，不能视为可随意替换的前端代码。

Tests and release tools live outside the verifier package. The finite-model
oracle imports only the public API and interprets claim trees independently
of the kernel. Release tooling packages an explicit file allowlist and creates
deterministic archives; it cannot add inference rules at runtime.

测试和发布工具位于验证器包之外。有限模型语义参照程序只导入公开 API，并独立于内核解释待核验陈述树。发布工具按照明确的文件许可列表打包并创建确定性归档；它无法在运行时添加推理规则。

<a id="design-decisions"></a>

## Design decisions / 设计决策

- **Fixed propositional logic:** standard natural deduction gives a clear
  meaning and a short soundness argument. Avoiding binders and computation
  removes variable capture, substitution and reduction machinery in v0.1.
  **固定命题逻辑：** 标准自然演绎含义清晰，且健全性论证简短。v0.1 不处理绑定变量和计算，因此无需变量捕获、代换和归约机制。
- **Python standard library:** readers can run and inspect the source without
  installing dependencies. The interpreter remains a substantial trusted
  component; a future second implementation should reduce shared failure modes.
  **Python 标准库：** 读者无需安装依赖即可运行并检查源代码。解释器仍是可信计算基础的重要组成部分；未来增加第二种实现应能减少共同失效模式。
- **JSON with exact schemas:** familiar tooling and explicit references;
  strict duplicate/type/limit checks address JSON interpretation hazards.
  **采用精确模式的 JSON：** 工具普及且引用关系明确；严格检查重复项、类型和限制，以应对 JSON 解释风险。
- **Separate claim and certificate:** the target is selected by the caller and
  compared structurally after replay. No digest or certificate assertion can
  override the expected theorem.
  **待核验陈述与证书分离：** 目标由调用方选定，并在重放后进行结构比较。任何摘要或证书声明都不能覆盖预期定理。
- **Formula-set contexts:** contraction and weakening are valid in this logic.
  This decision must be revisited for linear logic or binder-dependent rules.
  **公式集合上下文：** 在本逻辑中，收缩和弱化规则有效。若扩展到线性逻辑或依赖绑定变量的规则，就必须重新审视此设计。

This architecture borrows the independent replay idea from established proof
systems, especially Metamath/MM0. It is not a reimplementation of their full
languages or a compatible interchange format. See [research.md](research.md).

这一架构借鉴了成熟证明系统（尤其是 Metamath/MM0）中的独立重放思想，但并未重新实现它们的完整语言，也不兼容其交换格式。参见 [research.md](research.md)。
