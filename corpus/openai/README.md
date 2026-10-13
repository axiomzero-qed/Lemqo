# Pinned OpenAI corpus / 固定的 OpenAI 语料

This directory contains the upstream source snapshot and local provenance for
Lemqo's three selected OpenAI targets. Use the bilingual [result guide](../../docs/openai.md)
for their exact statements, scope and verification status, and the
[Lean guide](../../docs/lean.md) for the acceptance contract and toolchain.

本目录保存 Lemqo 三个选定 OpenAI 目标的上游源码快照及本地来源记录。精确陈述、适用范围和验证状态见双语[结果指南](../../docs/openai.md)；验收契约和工具链见 [Lean 指南](../../docs/lean.md)。

## Directory map / 目录说明

- [catalog.json](catalog.json) pins upstream commits, project files and all
  349 vendored Lean files by hash; it also identifies each selected main target
  and supporting results.
  [catalog.json](catalog.json) 按哈希固定上游提交、项目文件和全部 349 个随仓库保存的 Lean 文件，并标识各选定主目标及辅助结果。
- [lean/](lean/) preserves the upstream source tree. Its
  [Comparator README](lean/ComparatorChallenges/README.md) remains an original
  upstream document; follow Lemqo's guides for this project's workflow.
  [lean/](lean/) 保留上游源码树。其中 [Comparator README](lean/ComparatorChallenges/README.md) 是未改动的上游文档；运行本项目流程时，请遵循 Lemqo 指南。
- [verification/summary.json](verification/summary.json) records the completed
  checks, full declaration counts and identities of generated certificates.
  [verification/summary.json](verification/summary.json) 记录已完成的检查、完整声明数及生成证书的身份标识。
- [LICENSE](LICENSE) is the retained original Apache-2.0 license; attribution
  is explained in [THIRD_PARTY.md](../../THIRD_PARTY.md).
  [LICENSE](LICENSE) 保留 Apache-2.0 许可证原文；署名说明见 [THIRD_PARTY.md](../../THIRD_PARTY.md)。

## Check and reproduce / 检查与复现

Run source-integrity checks from the repository root before producing exports:

生成导出前，请在仓库根目录运行源码完整性检查：

```sh
python tools/check_openai_sources.py
```

Then follow [docs/openai.md](../../docs/openai.md) to prepare the certificates
and run the independent checker. Export production is a trusted preparation
stage. Offline verification checks selected, authenticated reference bytes
against untrusted solution bytes and requires both Comparator binding and
Nanoda proof checking. Upstream challenge settings do not replace Lemqo's
mandatory independent proof-checking stage.

随后按照 [docs/openai.md](../../docs/openai.md) 准备证书并运行独立验证器。导出生成属于可信准备阶段。离线验证将选定且已确认身份的参考字节与不可信解答字节进行核对，同时要求 Comparator 绑定和 Nanoda 证明检查通过。上游挑战配置不能替代 Lemqo 必需的独立证明检查阶段。

Do not edit vendored files to translate them or to make a check pass. A deliberate
source update must update its provenance and catalog hashes and repeat the
relevant validation. Do not treat a supporting lemma as verification of a main
target, or three selected targets as completion of all 722 manuscripts.

不要为翻译或通过检查而修改上游快照。主动更新源码时，必须更新来源记录和目录哈希，并重新执行相关验证。不要把辅助引理通过当作主目标通过，也不要把三个选定目标当作全部 722 篇稿件已完成验证。
