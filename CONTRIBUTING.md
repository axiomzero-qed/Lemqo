<a id="contributing"></a>

# Contributing / 贡献指南

Thanks for helping improve Lemqo. Keep changes focused and explain the behavior or documentation they affect.

感谢你帮助改进 Lemqo。请保持改动聚焦，并说明它们影响的行为或文档。

The [documentation index](docs/README.md) provides reading paths and the shared
English/Chinese terminology. Keep both languages in sync when editing prose;
preserve command examples, protocol fields and mathematical expressions.

[文档索引](docs/README.md)提供阅读路线和统一英中术语。修改说明文字时，请同步维护两种语言，保留命令示例、协议字段和数学表达式。

<a id="development"></a>

## Development / 开发

The IPL checker uses Python 3.11 or newer and only the standard library at
runtime. Its v0.1 rules, format, and test semantics remain unchanged. The
optional Lean path has separate native prerequisites and currently has only
Linux validation; see [docs/lean.md](docs/lean.md) before changing it. Run the
Python suite and release checks from the repository root:

IPL 检查器运行时需要 Python 3.11 或更新版本，且只依赖标准库。v0.1 的规则、格式和测试语义保持不变。可选 Lean 路径有独立的原生依赖，目前仅在 Linux 上验证；修改前请阅读 [docs/lean.md](docs/lean.md)。请在仓库根目录运行以下 Python 测试套件和发布检查：

```text
python -m unittest discover -s tests -v
python tools/check_release.py
python tools/build_release.py --out dist
```

The optional OpenAI corpus workflow uses repository-vendored sources:

可选 OpenAI 语料工作流使用仓库随附并固定版本的源文件：

```text
python tools/build_lean_backends.py --work /tmp/lemqo-backends
python tools/openai_certificates.py --work /tmp/lemqo-openai --out /tmp/lemqo-certificates --backends /tmp/lemqo-backends/backends.json
```

It does not accept arbitrary Lean source. Keep main-theorem status distinct
from supporting lemmas, and report a result as checked only after both the
Comparator and independent Nanoda stages pass.

此工作流不接受任意 Lean 源码。请将主定理状态与辅助引理区分开；只有 Comparator 和独立 Nanoda 两个阶段都通过后，才能报告结果已核验。

To run from source, use:

从源码运行时，请使用：

```text
python -m lemqo --help
```

<a id="changes-to-the-proof-rules"></a>

## Changes to the proof rules / 修改证明规则

The v0.1 calculus is fixed. Any proposed rule-set change must update the formal specification, add adversarial tests that exercise invalid as well as valid derivations, and receive maintainer review. Please explain the logical effect of each proposed rule and any change to what acceptance guarantees.

v0.1 演算规则固定。任何规则集变更提案都必须更新形式化规范、添加同时覆盖有效和无效推导的对抗性测试，并经维护者审查。请说明每条拟议规则的逻辑效果，以及它会如何改变接受结果所保证的内容。

<a id="reporting-issues"></a>

## Reporting issues / 报告问题

Use [GitHub Issues](https://github.com/axiomzero-qed/Lemqo/issues) for bugs and design questions, or Discussions if enabled. For vulnerability reports, follow [SECURITY.md](SECURITY.md).

请通过 [GitHub Issues](https://github.com/axiomzero-qed/Lemqo/issues) 报告错误或设计问题；若已启用，也可使用 Discussions。报告漏洞请遵循 [SECURITY.md](SECURITY.md)。
