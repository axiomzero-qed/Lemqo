<a id="changelog"></a>

# Changelog / 更新日志

## Unreleased / 尚未发布

No pending release changes. / 暂无待发布变更。

## 0.3.0 — recoverable verification workflows, 2026-10-16 / 可恢复核验流程

- Supports 1–32 theorem names in a catalog candidate, preserving the singular
  spelling for existing single-target entries and requiring exact config binding.
  语料候选支持 1–32 个定理名称，兼容单目标旧写法，并严格匹配配置。
- Splits build/export/check, continues after per-target failures, writes atomic
  checkpoints and batch summaries, and adds `--reuse-exports` / `--resume`.
  拆分构建/导出/检查，单目标失败后继续，原子写入检查点与汇总，并增加导出复用及续跑。
- Selects IDs from the catalog, rejects unresolved local imports at admission,
  and documents corpus extension and heavy-target timeouts.
  从目录选择 ID，入库时拒绝未解析本地导入，并补充语料扩展和重目标时限文档。
- Adds truthful elapsed-time heartbeats, distinct exit/signal/CPU-limit errors,
  UTC start time, duration and reference counts in Lean receipts.
  增加如实报告耗时的心跳，区分退出/信号/CPU 限额错误，Lean 回执增加 UTC 起始时间、耗时及参考计数。
- Adds `audit-receipt` for file/receipt consistency, explicitly separate from a
  fresh proof check; supports older v0.2 receipts.
  增加回执与文件一致性审计，明确区分于新的证明检查，兼容旧 v0.2 回执。
- Adds a dependency-free MCP stdio reference server for the existing IPL/Lean
  APIs, with operator-fixed trust inputs and bounded proof submissions.
  增加调用现有 IPL/Lean API 的零依赖 MCP stdio 参考服务，可信输入由操作者固定，证明提交有界。
- Publishes the existing bilingual website source and updates its release
  overview, workflow, audit and agent-integration links for v0.3.
  将现有双语网站源码纳入仓库，并更新 v0.3 功能、工作流、审计及智能体接入链接。

Logical acceptance, backend source pins and the three archived v0.2 theorem
records are preserved. This release does not claim a recheck of all OpenAI
targets or a formal proof of implementation correctness.

逻辑验收条件、后端源码固定版本及三份 v0.2 定理归档记录保持不变。本次不声称重跑了全部 OpenAI 目标，也不声称实现具有形式化正确性证明。

- Pairs project documentation in English and Simplified Chinese, adds a
  developer index and terminology guide, and checks links in the bridge and
  corpus guides. Protocol identifiers and certificate examples are unchanged.
  项目文档增加英文与简体中文对照，新增开发者索引和术语指南，并检查桥接程序与语料指南的链接。协议标识和证书示例保持不变。

<a id="020--experimental-independent-lean-checking"></a>

## 0.2.0 — experimental independent Lean checking / 实验性 Lean 独立核验

- Preserves the v0.1 IPL `check` behavior, certificate format, and test
  semantics.
  保留 v0.1 IPL `check` 行为、证书格式和测试语义。
- Adds an optional `check-lean` workflow with reference-hash binding, strict
  NDJSON preflight, offline Comparator checks, and independent Rust Nanoda
  checking of every declaration.
  增加可选 `check-lean` 工作流，支持参考导出哈希绑定、严格 NDJSON 预检、离线 Comparator 检查，以及使用独立 Rust Nanoda 核验每条声明。
- Limits the current corpus workflow to three selected, vendored OpenAI
  results. The selected main targets passed independent checking: Seymour
  (22,252 declarations), Erdős–Gallai (41,966), and the Borsuk projector main
  theorem (70,651). Supporting lemmas are not counted as additional results.
  当前语料工作流限于三个选定的、随仓库提供并固定版本的 OpenAI 结果。选定的主目标已通过独立核验：Seymour（22,252 条声明）、Erdős–Gallai（41,966 条）和 Borsuk 投影算子主定理（70,651 条）。辅助引理不计为额外结果。
- Records Linux-only validation for this path: a 585-declaration smoke check
  and 30 native/public-API regression cases passed. This is not a claim of general Lean
  support or verification of all 722 manuscripts.
  该路径仅记录了 Linux 验证：585 条声明的冒烟检查和 30 个原生/公共 API 回归用例通过。这不表示支持通用 Lean，也不表示已核验全部 722 份手稿。

The Lean path adds trusted components beyond the IPL checker. Release tags and
commit-specific CI evidence are recorded separately; see the
[v0.2 validation record](docs/validation-v0.2.md).

Lean 路径在 IPL 检查器之外增加了可信组件。发布标签与具体提交的 CI 证据另行记录；参见 [v0.2 验证记录](docs/validation-v0.2.md)。

<a id="010--initial-release-candidate-2026-10-12"></a>

## 0.1.0 — initial release candidate, 2026-10-12 / 初始候选版本，2026-10-12

- A fixed intuitionistic propositional natural-deduction calculus with ten rules.
  固定的直觉主义命题自然演绎演算，包含十条规则。
- Explicit formula/proof DAG certificates and separately selected claim files.
  明确的公式/证明 DAG 证书和单独选定的待核验陈述文件。
- Structural formula identity, immutable assumption tracking and exact goal binding.
  结构化公式同一性、不可变假设跟踪和精确目标绑定。
- Bounded strict UTF-8 JSON ingestion and fail-closed CLI/API behavior.
  有界且严格的 UTF-8 JSON 读取，以及失败即拒绝的 CLI/API 行为。
- Seven accepted example derivations and two deliberately rejected certificates.
  七个接受的示例推导和两个刻意设计为被拒绝的证书。
- Unit, adversarial, semantic-oracle, CLI and reproducible-archive tests.
  单元、对抗性、语义参照程序、CLI 和可复现归档测试。
- English specification, trust analysis, research, contributor and release documents.
  英文规范、信任分析、研究、贡献和发布文档。
- MIT license, pinned GitHub Actions, and dependency-free offline ZIP releases.
- MIT 许可证、固定版本的 GitHub Actions，以及无需依赖的离线 ZIP 发布包。

The v0.1 candidate contains one Python IPL checker and no quantified
mathematics, arithmetic, custom axioms, definitions, tactics or external-system
importers. There is no machine-checked proof of implementation correctness.
Publication and remote CI results must be recorded separately when the
repository is live.

v0.1 候选版本包含一个 Python IPL 检查器，不包含含量词的数学、算术、自定义公理、定义、策略或外部系统导入器。实现正确性没有机器核验的证明。仓库上线后，发布和远程 CI 结果必须分别记录。
