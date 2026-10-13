# Developer documentation / 开发者文档

Lemqo's project-owned documentation pairs English with Simplified Chinese in
the same file. Start with the [project README](../README.md) to run one valid
proof and one rejected certificate in a few minutes.

Lemqo 自有文档在同一文件内提供英文和简体中文对照。请先阅读[项目 README](../README.md)，几分钟内即可运行一个有效证明和一个被拒绝的证书。

## Reading paths / 阅读路线

| Goal / 目标 | Documents / 文档 |
| --- | --- |
| Contribute a change / 参与开发 | [Contributing / 贡献指南](../CONTRIBUTING.md), [architecture / 架构](architecture.md), [examples / 示例](../examples/README.md) |
| Audit the IPL rules / 审计 IPL 规则 | [Specification / 规范](specification.md), [trust and soundness / 信任与健全性](trust.md), [research / 技术调研](research.md) |
| Reproduce independent Lean checking / 复现 Lean 独立验证 | [Lean guide / Lean 指南](lean.md), [bridge / 桥接程序](../bridge/lean/README.md), [OpenAI results / OpenAI 结果](openai.md), [corpus guide / 语料指南](../corpus/openai/README.md) |
| Review evidence and prepare releases / 审查证据与准备发布 | [v0.2 validation / v0.2 验证记录](validation-v0.2.md), [historical v0.1 record / v0.1 历史记录](validation.md), [release guide / 发布指南](release.md) |
| Understand future work and project policies / 了解后续工作与项目规则 | [Roadmap / 路线图](roadmap.md), [security / 安全](../SECURITY.md), [conduct / 行为准则](../CODE_OF_CONDUCT.md), [third-party notices / 第三方声明](../THIRD_PARTY.md) |

## Shared terminology / 统一术语

| English | 中文 | Meaning / 含义 |
| --- | --- | --- |
| Proof certificate | 证明证书 | Explicit data checked by inference rules or a proof kernel / 由推理规则或证明内核检查的显式数据 |
| Claim | 待核验陈述 | Caller-selected target and permitted assumptions / 调用方选择的目标及允许的假设 |
| Reference export | 参考导出 | Independently selected formal specification for Lean statement binding / 独立选择、用于 Lean 陈述绑定的形式规范 |
| Verification receipt | 验证回执 | Completed check's result and input identities / 完整检查的结果及输入标识 |
| Open assumption | 未解除的假设 | Formula still retained in a step's context / 步骤上下文中仍保留的公式 |
| Discharge | 解除假设 | Remove a permitted assumption under the specified rule / 按指定规则移除可解除的假设 |
| Soundness | 健全性 | Accepted derivations respect the specified mathematical semantics / 被接受的推导符合指定数学语义 |
| Formalization fidelity | 形式化忠实度 | The statement and definitions express the intended mathematics / 陈述与定义表达预期数学内容 |
| Implementation correctness | 实现正确性 | The program implements its specification without defects / 程序无缺陷地实现规范 |
| Trusted computing base (TCB) | 可信计算基础 | Components whose correctness the result relies on / 结果所依赖其正确性的组件 |
| Permitted axioms | 允许的公理 | The acceptance policy's allowed set, which need not be the minimal set used / 验收策略允许的集合，不一定是实际使用的最小集合 |

A rejected certificate does not establish that its target proposition is false.
A valid derivation does not establish statement fidelity or the absence of
implementation defects. These distinctions apply in both languages.

证书被拒绝不说明目标命题为假。推导有效不确立陈述忠实度，也不排除实现缺陷。两种语言的说明都应保持这些区分。

## Maintaining translations / 维护翻译

Update both languages together. Keep each English paragraph followed by its
Chinese counterpart; pair list items and table cells as well. Share one copy
of commands, JSON and mathematical rule tables. Preserve protocol identifiers,
field names, paths, theorem names, formulas, hashes and version numbers exactly.
Translate explanations without translating these executable or formal values.

请同步更新两种语言。每个英文段落后紧接对应中文，列表条目和表格单元格也应对照。命令、JSON 和数学规则表只保留一份。协议标识、字段名、路径、定理名、公式、哈希和版本号必须原样保留。翻译解释文字，不翻译这些可执行或形式化取值。

The English IPL specification is the normative reference for the versioned
wire format. Chinese text explains the same contract. Report any disagreement
as a documentation defect, resolve it against the specification and code, and
correct both texts. Do not silently change a protocol through translation.

英文 IPL 规范是版本化传输格式的规范性依据，中文说明同一契约。若发现两种文本不一致，请按文档缺陷报告，对照规范和代码解决，并同步修正。不要通过翻译悄然改变协议。

Original legal license texts and hash-pinned third-party source snapshots remain
unchanged. Read the bilingual project guides alongside them. Generated JSON
records remain machine-readable data. These Markdown files can also serve as
the source for future documentation at [lemqo.com](https://lemqo.com).

法律许可证原文及按哈希固定的第三方源码快照保持原样，可配合项目双语指南阅读。生成的 JSON 记录仍是机器可读数据。这些 Markdown 文件也可作为未来 [lemqo.com](https://lemqo.com) 文档网站的源文件。
