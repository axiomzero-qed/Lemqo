# Lemqo

**A small language and independent checker for explicit mathematical proof certificates.**

**用于显式数学证明证书的小型语言和独立验证器。**

Lemqo explores how much proof verification can be made transparent and easy to
audit. A producer supplies a certificate; the checker replays every inference
against a separately selected claim. Proof generation and verification are
separate jobs. Our long-term aim is to check certificates produced by humans,
AI, and other proof systems through documented translations.

Lemqo 探索如何让证明核验过程透明且易于审计。证明生成方提供证明证书；检查器针对单独选定的待核验陈述 claim 重放每一步推理。证明生成和核验是分开的工作。我们的长期目标是通过有文档说明的转换，核验由人类、AI 和其他证明系统生成的证书。

**v0.2 preserves the v0.1 intuitionistic propositional logic checker and adds
an optional, experimental independent Lean-certificate check.**
The IPL path has ten fixed natural-deduction rules for implication, conjunction,
disjunction, and falsehood. The original `check` command and certificate
semantics are unchanged. The separate `check-lean` workflow is limited to the
repository's pinned, vendored OpenAI corpus; it is not general Lean support.
Three selected OpenAI theorem targets have passed actual statement binding
and independent Nanoda checking: Seymour's second-neighborhood theorem,
Erdős–Gallai cycle decomposition, and Borsuk's projector main theorem.

v0.2 保留 v0.1 的直觉主义命题逻辑检查器，并增加可选的实验性 Lean 证书独立核验。IPL 路径包含十条固定的自然演绎规则，涵盖蕴含、合取、析取和假。原有 `check` 命令和证书语义保持不变。独立的 `check-lean` 工作流仅限于仓库中固定版本并随仓库提供的 OpenAI 语料；它不代表通用 Lean 支持。三个选定的 OpenAI 定理目标已通过实际陈述绑定和 Nanoda 独立核验：Seymour 第二邻域定理、Erdős–Gallai 圈分解定理，以及 Borsuk 投影算子主定理。

<a id="try-a-valid-and-an-invalid-proof"></a>

## Try a valid and an invalid proof / 试运行一个有效证明和一个无效证明

Clone the repository, then run the checker. Python 3.11+ is the only runtime
requirement; after obtaining the source, no package installation or network is
needed. On Windows, use `py -3` if `python` is not available.

克隆仓库并运行检查器。唯一的运行时要求是 Python 3.11+；获取源代码后无需安装软件包或联网。Windows 用户若无法使用 `python`，请使用 `py -3`。

```sh
git clone https://github.com/axiomzero-qed/Lemqo.git
cd Lemqo
python -m lemqo check examples/identity.proof.json --claim examples/identity.claim.json
```

This checks `P → P` and prints `VALID identity (closed; 2 checked steps)`.
It also shows the exact goal and premise dependencies. Now try:

此命令核验 `P → P`，并输出 `VALID identity (closed; 2 checked steps)`。它还会显示准确的目标和前提依赖关系。现在再试：

```sh
python -m lemqo check examples/identity.invalid.proof.json --claim examples/identity.claim.json
```

The forged inference prints `REJECTED [inference]` and exits with status 1.
Rejection means the submitted certificate failed, not that its claim is false:
both examples target the same true statement.

伪造的推理会输出 `REJECTED [inference]`，并以状态码 1 退出。拒绝表示提交的证书未通过核验，不表示其待核验陈述为假：两个示例针对的是同一个真命题。

For a larger proof and a machine-readable receipt:

如需核验更大的证明并生成机器可读回执，请运行：

```sh
python -m lemqo check examples/distributivity.proof.json --claim examples/distributivity.claim.json --json
```

<a id="what-a-successful-ipl-check-means"></a>

## What a successful IPL check means / IPL 核验成功意味着什么

Acceptance establishes derivability of the **supplied formula from the reported
premises under the fixed rules**, subject to correctness of this implementation
and its runtime. A certificate cannot change the caller's claim. Open
assumptions must be explicitly permitted; `False ⊢ P` is a conditional result,
while an unproved `⊢ False` is rejected.

接受结果表示：**在固定规则下，所提供的公式可由已报告的前提推导出来**，但这一结论以本实现及其运行时正确为条件。证书不能更改调用方指定的待核验陈述。开放假设必须得到明确允许；`False ⊢ P` 是条件性结果，而未经证明的 `⊢ False` 会被拒绝。

Atoms such as `P` are uninterpreted propositions. Naming an atom `RiemannHypothesis`
does not formalize or prove that mathematical conjecture. Review the formal
statement and its premises as well as the certificate. There is no claim of
absolute safety, implementation correctness, or a measured total trusted base
smaller than Lean's. The Python interpreter is part of the trust boundary.

像 `P` 这样的原子是未解释命题。将一个原子命名为 `RiemannHypothesis` 并不会形式化或证明该数学猜想。除了证书本身，也请审查形式化陈述及其前提。我们不声称绝对安全、不声称实现必然正确，也不声称已测得的整体可信计算基础 TCB 小于 Lean 的 TCB。Python 解释器属于信任边界。

<a id="optional-lean-certificate-path"></a>

## Optional Lean certificate path / 可选的 Lean 证书路径

The Lean path binds a caller-selected reference by hash, performs strict
NDJSON preflight and offline Comparator checks for declarations, statements,
primitives, and axiom types, then asks an independent Rust Nanoda checker to
check every declaration. Both stages must pass before a result can be `VALID`.
Its trusted computing base is larger than the IPL checker's. This path does not
establish absolute correctness or support for all Lean. See the
[Lean checking guide](docs/lean.md) and
[selected OpenAI results and status](docs/openai.md).

Lean 路径按哈希绑定调用方选定的参考导出 reference，执行严格的 NDJSON 预检和离线 Comparator 检查，核对声明、陈述、原语及公理类型；随后由独立的 Rust Nanoda 检查器核验每条声明。两个阶段都必须通过，结果才会是 `VALID`。该路径的可信计算基础 TCB 大于 IPL 检查器。此路径不保证绝对正确，也不支持所有 Lean。请参阅 [Lean 核验指南](docs/lean.md) 和[选定的 OpenAI 结果与状态](docs/openai.md)。

Build the backends and prepare a certificate from the vendored sources (omit
`--only` to select all three results):

构建后端，并根据仓库中固定的源码生成证书（省略 `--only` 可选择全部三个结果）：

```sh
python tools/build_lean_backends.py --work /tmp/lemqo-backends
python tools/openai_certificates.py --work /tmp/lemqo-openai --out /tmp/lemqo-certificates --backends /tmp/lemqo-backends/backends.json --only seymour_second_neighborhood
```

This workflow has only been exercised on Linux. Preparing a certificate does
not mean its theorem has passed independent checking; the producer reports
`VALID` and writes a receipt only after the separate offline check succeeds.
The [verification records](corpus/openai/verification/summary.json) identify the
three checked main targets and complete certificate hashes. Full exports are
generated locally rather than committed as hundreds of megabytes of JSON.

此工作流目前仅在 Linux 上运行过。准备好证书不代表定理已通过独立核验；只有单独的离线检查成功后，生成器才会报告 `VALID` 并写入回执。[核验记录](corpus/openai/verification/summary.json)列出三个已核验的主目标及完整证书哈希。完整导出文件会在本地生成，不会作为数百兆字节的 JSON 提交。

<a id="tests-documentation-and-releases"></a>

## Tests, documentation, and releases / 测试、文档与发布

```sh
python tools/check_release.py
python tools/build_release.py --out dist
python dist/lemqo-0.2.0.pyz check examples/identity.proof.json --claim examples/identity.claim.json
```

The original 49 IPL tests retain their v0.1 semantics and cover valid proofs,
invalid inferences, assumption discharge, adversarial
JSON, resource limits, CLI failures, and an independent finite Kripke-model
oracle. The build creates a reproducible runnable archive, a source archive,
and SHA-256 checksums using only the standard library.

原有的 49 项 IPL 测试保留 v0.1 语义，覆盖有效证明、无效推理、假设解除、对抗性 JSON、资源限制、CLI 失败情况，以及独立的有限 Kripke 模型语义参照程序。构建过程仅使用标准库，生成可复现的可运行归档、源代码归档和 SHA-256 校验和。

- [Bilingual documentation index and terminology](docs/README.md) — [双语文档索引与统一术语](docs/README.md)
- [Certificate format, rules, and mathematical semantics](docs/specification.md) — [证书格式、规则与数学语义](docs/specification.md)
- [Lean certificate checking guide](docs/lean.md) — [Lean 证书核验指南](docs/lean.md)
- [Selected OpenAI results and verification status](docs/openai.md) — [选定的 OpenAI 结果与核验状态](docs/openai.md)
- [Trusted boundary, threat model, and soundness argument](docs/trust.md) — [信任边界、威胁模型与健全性 soundness 论证](docs/trust.md)
- [Architecture and audit entry points](docs/architecture.md) — [架构与审计入口](docs/architecture.md)
- [Research: Lean, Metamath, MM0, and HOL/OpenTheory](docs/research.md) — [研究：Lean、Metamath、MM0 与 HOL/OpenTheory](docs/research.md)
- [Examples and how their proofs work](examples/README.md) — [示例及其证明过程](examples/README.md)
- [Release instructions and reproducibility](docs/release.md) — [发布说明与可复现性](docs/release.md)
- [Recorded local validation and review](docs/validation.md) — [本地验证与审查记录](docs/validation.md)
- [Roadmap](docs/roadmap.md) — [路线图](docs/roadmap.md), [contributing](CONTRIBUTING.md) — [贡献指南](CONTRIBUTING.md), [security](SECURITY.md) — [安全](SECURITY.md)

Project domain: [lemqo.com](https://lemqo.com). The repository's bilingual Markdown
documentation is the source for a future documentation site; v0.1 does not
deploy or depend on a website. Public repository:
[axiomzero-qed/Lemqo](https://github.com/axiomzero-qed/Lemqo).

项目域名：[lemqo.com](https://lemqo.com)。仓库中的中英对照 Markdown 文档将作为未来文档网站的源文件；v0.1 不会部署网站，也不依赖网站。公开仓库：[axiomzero-qed/Lemqo](https://github.com/axiomzero-qed/Lemqo)。

The original Python implementation is licensed under the [MIT License](LICENSE).
The bridge and third-party sources are governed by their respective Apache
licenses; see [THIRD_PARTY.md](THIRD_PARTY.md).

原始 Python 实现采用 [MIT 许可证](LICENSE)。桥接代码和第三方来源分别遵循其 Apache 许可证；详见 [THIRD_PARTY.md](THIRD_PARTY.md)。

The [research documents](docs/research.md) acknowledge the systems that informed
Lemqo's design.

[研究文档](docs/research.md)记录并致谢为 Lemqo 设计提供参考的现有系统。
