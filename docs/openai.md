<a id="openai-math-formalizations-in-lemqo"></a>

# OpenAI math formalizations in Lemqo / Lemqo 中的 OpenAI 数学形式化

Three selected main theorem targets from the pinned OpenAI math corpus passed Lemqo's offline statement binding and independent Rust Nanoda checks. The source snapshot, exact target scope, and verification evidence are retained for reproduction and review.

固定版本的 OpenAI 数学语料库中，三个选定的主要定理目标通过了 Lemqo 的离线陈述绑定检查和独立 Rust Nanoda 检查。源代码快照、精确目标范围和验证证据均已保留，以供复现和审查。

<a id="upstream-snapshot"></a>

## Upstream snapshot / 上游快照

The snapshot is pinned to [openai/math](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb), commit fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb. Upstream source is under [corpus/openai/lean/](../corpus/openai/lean/); its Apache-2.0 license is retained at [corpus/openai/LICENSE](../corpus/openai/LICENSE). [catalog.json](../corpus/openai/catalog.json) lists theorem declarations, comparator challenge and solution modules, paper and scope links, pinned project metadata, and deduplicated Lean source paths with byte sizes and SHA256 hashes.

该快照固定到 [openai/math](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb) 的提交 fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb。上游源文件位于 [corpus/openai/lean/](../corpus/openai/lean/)；其 Apache-2.0 许可证保存在 [corpus/openai/LICENSE](../corpus/openai/LICENSE) 中。[catalog.json](../corpus/openai/catalog.json) 列出了定理声明、比较器挑战模块和解答模块、论文及范围链接、固定项目元数据，以及去重后的 Lean 源文件路径、字节大小和 SHA256 哈希。

The [October 2026 release announcement](https://openai.com/index/sharing-ai-progress-in-mathematics/) described 722 manuscripts. By this pinned repository snapshot, the collection had been revised to 719; only a subset has Lean formalizations. The upstream [revision history](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/history.md) records those changes. This snapshot includes three catalogue-listed main results. Supporting lemmas are not counted as additional results here.

[2026 年 10 月的发布公告](https://openai.com/index/sharing-ai-progress-in-mathematics/)介绍了 722 篇手稿。到这个固定仓库快照时，集合已修订为 719 篇；其中只有一部分拥有 Lean 形式化。上游[修订历史](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/history.md)记录了这些变化。此快照包含目录列出的三个主要结果。这里不把辅助引理计作额外结果。

<a id="main-results-included"></a>

## Main results included / 收录的主要结果

- **Erdős–Gallai cycle decomposition:** There is a universal constant $C > 0$ such that every finite simple graph on $n$ vertices has an edge-disjoint decomposition into cycles and single edges using at most $Cn$ pieces. The formalized statement includes edgeless and small graphs; it does not determine the optimal constant. [Paper](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/A-linear-cycle-and-edge-decomposition-of-every-graph-September-24-2026/main.pdf) · [scope note](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/181.md).
  **Erdős–Gallai 环分解：** 存在一个通用常数 $C > 0$，使得每个具有 $n$ 个顶点的有限简单图都能分解为两两边不相交的环和单边，且所用部分不超过 $Cn$ 个。形式化陈述涵盖无边图和小图；它没有确定最优常数。[论文](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/A-linear-cycle-and-edge-decomposition-of-every-graph-September-24-2026/main.pdf) · [范围说明](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/181.md)。
- **Seymour’s second-neighborhood conjecture:** Every nonempty finite oriented graph has a vertex whose number of out-neighbors at directed distance exactly two is at least its outdegree. The second neighborhood excludes the starting vertex and first out-neighbors; sinks are included. [Paper](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/A-proof-of-Seymours-second-neighborhood-conjecture-September-23-2026/paper.pdf) · [scope note](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/173.md).
  **Seymour 第二邻域猜想：** 每个非空有限定向图都存在一个顶点，其有向距离恰为 2 的出邻点数量至少等于该顶点的出度。第二邻域不包括起始顶点和第一层出邻点；汇点也包含在适用范围内。[论文](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/A-proof-of-Seymours-second-neighborhood-conjecture-September-23-2026/paper.pdf) · [范围说明](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/173.md)。
- **A nine-dimensional counterexample to Borsuk’s assertion:** The comparator target proves that the compact set of rank-one orthogonal projectors onto lines in $\mathbb{R}^4$ lies in the trace-one symmetric matrix space, has diameter $\sqrt{2}$, and cannot be covered by ten arbitrary subsets of strictly smaller diameter. The solution module derives an isometric image in $\mathbb{R}^9$ giving the nine-dimensional Euclidean counterexample; that corollary is not among this comparator’s named theorem targets. [Paper](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/A-nine-dimensional-counterexample-to-Borsuks-covering-assertion-September-23-2026/paper.pdf) · [scope note](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/156.md).
  **Borsuk 断言的九维反例：** 比较器目标证明，由 $\mathbb{R}^4$ 中直线上的秩一正交投影构成的紧集位于迹为 1 的对称矩阵空间中，直径为 $\sqrt{2}$，且不能被十个直径严格更小的任意子集覆盖。解答模块进一步导出该集合在 $\mathbb{R}^9$ 中的等距像，从而得到九维欧氏反例；这一推论不在本比较器具名的定理目标之列。[论文](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/A-nine-dimensional-counterexample-to-Borsuks-covering-assertion-September-23-2026/paper.pdf) · [范围说明](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/156.md)。

<a id="verification-status"></a>

## Verification status / 验证状态

Recorded on 2026-10-13 using Ubuntu 24.04 under WSL, Python 3.12.3, Lean 4.34.1, Rust 1.94.0 and the pinned Nanoda 0.4.19 source. All source modules built without modifying the vendored proofs. The solution exports contain complete transitive proof dependencies; no missing declarations were replaced by axioms or omitted from checking.

记录时间为 2026-10-13，环境为 WSL 下的 Ubuntu 24.04、Python 3.12.3、Lean 4.34.1、Rust 1.94.0，以及固定版本的 Nanoda 0.4.19 源码。所有源模块均成功构建，且未修改 vendored 证明。解答导出包含完整的传递证明依赖；没有用公理替代缺失声明，也没有将其从检查中省略。

| Selected target / 选定目标 | Nanoda declarations / Nanoda 声明数 | Reference bytes / 参考文件字节数 | Solution bytes / 解答文件字节数 | Result / 结果 |
| --- | ---: | ---: | ---: | --- |
| Seymour second neighborhood / Seymour 第二邻域 | 22,252 | 6,425,597 | 120,954,904 | Matched; independently checked / 匹配；已独立检查 |
| Erdős–Gallai cycle decomposition / Erdős–Gallai 环分解 | 41,966 | 21,712,669 | 268,967,194 | Matched; independently checked / 匹配；已独立检查 |
| Borsuk projector main theorem / Borsuk 投影矩阵主定理 | 70,651 | 77,807,309 | 523,141,577 | Matched; independently checked / 匹配；已独立检查 |

The [machine-readable summary](../corpus/openai/verification/summary.json) links these counts to full SHA256 identities. Per-result folders in [verification/](../corpus/openai/verification/) retain the claim, exact receipt and production provenance. The [build information](../corpus/openai/verification/build-information.json) identifies compilers and actual native binaries. The [archived catalog input](../corpus/openai/verification/catalog-input.json) preserves the exact UTF-8 catalog used during production, before its status fields were updated; hash its `utf8_text` encoded as UTF-8 to reproduce the provenance digest. Current source and check status are in [catalog.json](../corpus/openai/catalog.json).

[机器可读摘要](../corpus/openai/verification/summary.json)将这些计数与完整 SHA256 标识关联起来。[verification/](../corpus/openai/verification/) 中按结果划分的目录保留了待核验陈述、精确回执和生成溯源信息。[构建信息](../corpus/openai/verification/build-information.json)标明编译器和实际使用的原生二进制文件。[归档的目录输入](../corpus/openai/verification/catalog-input.json)保留了生成时使用的精确 UTF-8 目录内容（状态字段更新之前）；对其 `utf8_text` 的 UTF-8 编码计算哈希即可复现溯源摘要。当前源文件和检查状态见 [catalog.json](../corpus/openai/catalog.json)。

These are successful checks of the explicitly selected formal statements under `propext`, `Classical.choice` and `Quot.sound`, subject to the implementation assumptions in [lean.md](lean.md). They are not an independent human audit of the prose-to-formalization correspondence or a claim that the whole corpus has been checked. The Borsuk target is the projector statement described above; its separate Euclidean corollary is outside the named target list.

这些结果表示，在 [lean.md](lean.md) 所述实现假设下，显式选定的形式陈述在 `propext`、`Classical.choice` 和 `Quot.sound` 下通过了检查。它们并非对自然语言与形式化之间对应关系的独立人工审计，也不表示整个语料库都已检查。Borsuk 目标是上文所述的投影矩阵陈述；其单独的欧氏空间推论不在具名目标列表内。

<a id="reproduce"></a>

## Reproduce / 复现

v0.3 supports independent build/export/check phases, per-target failure
records and exact-hash recovery. See the [batch guide](batch.md) and
[target-admission schema](corpus-targets.md). The archived results below are
historical v0.2 checks; workflow improvements do not imply additional checked targets.

v0.3 支持独立构建/导出/检查阶段、逐目标失败记录及精确哈希恢复，参见[批量指南](batch.md)及[目标入库模式](corpus-targets.md)。归档成果是历史 v0.2 检查记录；工作流改进不表示新增已核验目标。

Follow [the native backend build](lean.md), then run:

按照 [原生后端构建说明](lean.md)操作，然后运行：

```sh
python tools/openai_certificates.py --work /tmp/lemqo-openai --out /tmp/lemqo-certificates --backends /tmp/lemqo-backends/backends.json
```

Omit `--only` to check all three, or select one of `seymour_second_neighborhood`, `cycle_decomposition`, `borsuk_nine`. The build instantiates a minimal pinned Mathlib project instead of the full upstream project's unrelated research dependencies. The initial Mathlib cache download is substantial; `--no-cache` in a fresh workspace builds from source. No untrusted `.lean` source service or sandbox is provided.

省略 `--only` 可检查全部三个目标；也可以从 `seymour_second_neighborhood`、`cycle_decomposition`、`borsuk_nine` 中选择一个。构建过程会实例化一个固定版本的最小 Mathlib 项目，而不是上游完整项目中与此无关的研究依赖。首次下载 Mathlib 缓存的数据量较大；在全新工作区中使用 `--no-cache` 会从源码构建。项目没有提供用于不可信 `.lean` 源码的服务或沙箱。

The output for each result includes `reference.ndjson`, `solution.ndjson`, `claim.json`, `provenance.json`, and a receipt only on acceptance. Full data exports are kept outside Git because their combined size approaches one gigabyte. Verification of existing exports needs only the prepared native programs and Python, without Lake, Mathlib cache access or network:

每个结果的输出包含 `reference.ndjson`、`solution.ndjson`、`claim.json` 和 `provenance.json`；只有接受后才会生成回执。完整数据导出文件总体积接近 1 GB，因此保存在 Git 之外。验证已有导出只需要准备好的原生程序和 Python，无需 Lake、Mathlib 缓存访问或网络：

```sh
python -m lemqo check-lean /tmp/lemqo-certificates/seymour_second_neighborhood/solution.ndjson --claim /tmp/lemqo-certificates/seymour_second_neighborhood/claim.json --reference /tmp/lemqo-certificates/seymour_second_neighborhood/reference.ndjson --backends /tmp/lemqo-backends/backends.json --json
```
