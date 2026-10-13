<a id="third-party-sources-and-dependencies"></a>

# Third-party sources and dependencies / 第三方来源与依赖

The root MIT license covers Lemqo's original Python implementation and tools.
It does not replace the licenses of retained upstream code or proof sources.

根目录 MIT 许可证适用于 Lemqo 原创的 Python 实现和工具；它不会取代保留的上游代码或证明源文件所适用的许可证。

- `corpus/openai/` contains unmodified selected sources from
  [openai/math](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb),
  under Apache-2.0. Its full license is retained at
  [corpus/openai/LICENSE](corpus/openai/LICENSE); original source notices remain.

  `corpus/openai/` 包含来自 [openai/math](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb) 的未修改选定源文件，采用 Apache-2.0 许可证。完整许可证保存在 [corpus/openai/LICENSE](corpus/openai/LICENSE)，原始来源声明仍予保留。
- `bridge/lean/Main.lean` adapts Comparator's primitive target list and invocation
  pattern, copyright 2025 Lean FRO, LLC, author Henrik Böving. This bridge is
  Apache-2.0, with attribution in the source and the full license at
  [bridge/lean/LICENSE](bridge/lean/LICENSE).

  `bridge/lean/Main.lean` 改编了 Comparator 的原语目标列表和调用模式，版权所有者为 Lean FRO, LLC（2025），作者 Henrik Böving。此桥接代码采用 Apache-2.0 许可证，源文件中包含署名，完整许可证位于 [bridge/lean/LICENSE](bridge/lean/LICENSE)。
- Comparator, lean4export, Nanoda and Mathlib are pinned Apache-2.0 dependencies
  fetched by build tools, rather than included as native binaries. Their source
  links, revisions and roles are listed in [docs/lean.md](docs/lean.md).

  Comparator、lean4export、Nanoda 和 Mathlib 是构建工具获取的固定版本 Apache-2.0 依赖，并未作为原生二进制文件包含在仓库中。它们的源码链接、版本修订和用途列于 [docs/lean.md](docs/lean.md)。

Generated mathematical certificates contain terms derived from these upstream
proofs. Preserve the applicable source attributions and Apache-2.0 license when
redistributing them. Compiler/runtime licenses also apply to redistributed
native binaries; Lemqo's source archives do not bundle those binaries.

生成的数学证明证书包含从这些上游证明派生的项。重新分发时请保留适用的来源署名和 Apache-2.0 许可证。重新分发原生二进制文件时也须遵守编译器/运行时许可证；Lemqo 源代码归档不包含这些二进制文件。
