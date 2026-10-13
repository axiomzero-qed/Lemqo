<a id="offline-statement-binding"></a>

# Offline statement binding / 离线陈述绑定

`lemqo_compare config.json` reads a trusted reference NDJSON export and an
untrusted solution NDJSON export. It does not execute supplied Lean source,
import supplied `.olean` files, run Lake, or invoke the Lean proof kernel.
Success means statement binding only. Lemqo must additionally obtain success
from its pinned independent Nanoda proof checker before reporting a valid proof.

`lemqo_compare config.json` 读取可信的参考 NDJSON 导出和不可信的解答 NDJSON 导出。它不执行提交的 Lean 源码、不导入提交的 `.olean` 文件、不运行 Lake，也不调用 Lean 证明内核。成功只表示陈述绑定成功；Lemqo 还必须获得固定的独立 Nanoda 证明验证器的成功结果，才能报告证明有效。

Build this directory with Lean 4.34.1 using `lake build lemqo_compare`.
The executable is `.lake/build/bin/lemqo_compare`. Lake dependencies are pinned
in `lakefile.toml`; retain the resulting `lake-manifest.json` for reproducibility.
The selected Comparator and exporter sources target Lean 4.34.0 upstream;
they were successfully compiled with this project's 4.34.1 toolchain on
2026-10-12. The generated manifest records both exact dependency commits.

在本目录使用 Lean 4.34.1 运行 `lake build lemqo_compare` 进行构建，可执行程序位于 `.lake/build/bin/lemqo_compare`。Lake 依赖固定在 `lakefile.toml` 中；请保留生成的 `lake-manifest.json` 以支持复现。所选 Comparator 和 exporter 上游源码面向 Lean 4.34.0，已于 2026-10-12 使用本项目 4.34.1 工具链成功编译。生成的清单记录两个依赖的精确提交。

The generated configuration has exactly these required fields:

生成的配置必须恰好包含这些字段：

```json
{
  "reference_file": "/absolute/path/reference.ndjson",
  "solution_file": "/absolute/path/solution.ndjson",
  "theorem_names": ["OAI.SelectedNamespace.main_theorem"],
  "permitted_axioms": ["propext", "Classical.choice", "Quot.sound"]
}
```

The Python caller supplies this configuration from its separately selected,
authenticated claim manifest. It must strictly validate the JSON and NDJSON
before invocation, including duplicate JSON keys and resource limits; the
upstream export parser is not a strict JSON-schema validator. This executable
additionally validates the format/exporter version and exact Lean toolchain
metadata before parsing declarations. It rejects unknown configuration fields, empty or
duplicate target names, non-theorem targets, unsafe/partial declarations, and
all unapproved solution axioms. The axiom list may be any subset of the three
shown. No definition holes or additional axioms are supported.

Python 调用方根据独立选择并确认身份的陈述清单提供配置。调用前必须严格验证 JSON 和 NDJSON，包括重复 JSON 键及资源限制；上游导出解析器不是严格的 JSON 模式验证器。本程序在解析声明前，还检查格式/exporter 版本及精确 Lean 工具链元数据。它拒绝未知配置字段、空或重复目标名、非定理目标、unsafe/partial 声明，以及所有未经允许的解答公理。公理列表可以是示例中三个公理的任意子集。不支持定义缺口或额外公理。

The trusted producer must export the selected theorem roots, **every** listed
permitted axiom (even when unused by the theorem), all `primitiveTargets` from
`Main.lean`, and the quotient declarations when `Quot.sound` is allowed, in
both reference and solution. Exporter recursively includes their full
dependencies. Do not use `--ignore-missing`, trim dependency declarations, or
replace them with axioms. Reference theorem bodies can be admitted proofs;
solution theorem bodies must be complete and are independently checked.

可信生成器必须在参考和解答两份导出中包含选定定理根、列表中的**每个**允许公理（即使定理未使用它）、`Main.lean` 中全部 `primitiveTargets`，以及允许 `Quot.sound` 时所需的商类型声明。Exporter 会递归加入完整依赖。不得使用 `--ignore-missing`、裁剪依赖声明或将依赖替换为公理。参考定理证明体可为占位证明；解答定理证明体必须完整，并接受独立检查。

Comparator compares theorem statements, the permitted axiom types and their
dependencies, all definitions used by statements, and the special primitive
declarations. It also audits the target proofs' transitive axiom dependencies.
It allows no definition holes. The reference and its source-to-export process
are trusted mathematical specification inputs, selected independently of the
submitted solution. Matching a reference does not establish that its formal
statement accurately expresses a paper's prose; that correspondence must be
reviewed and recorded by the producer.

Comparator 比较定理陈述、允许的公理类型及其依赖、陈述使用的全部定义和特殊原语声明，同时审查目标证明的传递公理依赖。它不允许定义缺口。参考导出及其源码到导出的过程是可信数学规范输入，应独立于提交的解答选择。与参考匹配并不确立形式陈述准确表达论文原意；生成者必须审查并记录这种对应关系。

On success the only stdout line is deterministic JSON with `status` equal to
`matched` and the original ordered `theorem_names` array. Errors go to stderr
with nonzero exit status. The Python caller must check both the exit code and
the exact returned target list, and separately run Nanoda over the same
immutable solution bytes. A match alone is never a verified proof.

成功时，stdout 只有一行确定性 JSON，其中 `status` 为 `matched`，`theorem_names` 保持原始数组顺序。错误写入 stderr，退出状态非零。Python 调用方必须检查退出码及返回目标列表的精确一致性，并对同一份不可变解答字节另行运行 Nanoda。单独匹配成功从来不等于证明已经验证。

Trust includes the binding program, Comparator, the exporter-format parser,
Lean runtime/compiler, the trusted reference selection, and the operating
system. Proof checking additionally trusts the separately implemented Nanoda
kernel and Rust toolchain. This is implementation diversity, not a claim of
a formally verified end-to-end checker.

信任范围包括绑定程序、Comparator、导出格式解析器、Lean 运行环境/编译器、可信参考选择及操作系统。证明检查还信任独立实现的 Nanoda 内核和 Rust 工具链。这提供实现多样性，不表示完整验证流程已得到形式化验证。

<a id="actual-tool-regression-tests"></a>

## Actual-tool regression tests / 真实工具回归测试

With the pinned Lean tools on `PATH`, after building the bridge, exporter and
Nanoda, run from this directory:

将固定 Lean 工具加入 PATH，构建桥接程序、exporter 和 Nanoda 后，在本目录运行：

```sh
lake build lemqo_compare lean4export
python3 tests/run_offline.py --nanoda /absolute/path/nanoda_bin
```

When running a copied bridge outside this checkout, also supply
`--lemqo-root /absolute/path/to/lemqo-checkout`. The script refuses Python
`-O`/`-OO` mode, which would otherwise disable its regression assertions.

若在当前检出以外运行复制的桥接程序，还应提供 `--lemqo-root /absolute/path/to/lemqo-checkout`。脚本拒绝 Python 的 `-O`/`-OO` 模式，因为这些模式会禁用回归断言。

The test script compiles the trusted `tests/Fixture.lean`, exports its complete
dependency closure and required primitive roots, and constructs hostile
exports. It tests substituted theorem types, modified relevant definitions,
forged allowed axiom types, modified kernel primitives, non-theorem roots,
missing declarations, unsafe/partial definitions, unsupported metadata,
unapproved axioms and invalid configurations. All artifacts and machine-readable
results stay under `.lake/bridge-regressions/`.

测试脚本编译可信的 `tests/Fixture.lean`，导出其完整依赖闭包和必需原语根，并构造恶意导出。案例覆盖替换定理类型、修改相关定义、伪造允许公理的类型、修改内核原语、非定理根、缺失声明、unsafe/partial 定义、不支持的元数据、未经允许的公理及无效配置。全部产物和机器可读结果保存在 `.lake/bridge-regressions/` 下。

The crucial paired test replaces only the theorem's proof: binding must accept
the unchanged statement, while Nanoda must reject the invalid proof. The
uncorrupted fixture must pass both tools. The script requires a real Nanoda
binary and fails if either positive or negative result is unexpected.
The final five tests invoke `lemqo.lean.verify_lean_files`: one acceptance of
the 585-declaration fixture, plus rejection of the corrupted proof, changed
statement, changed relevant definition, and forged axiom type. The script
writes `claim.json`, `backends.json` with actual binary hashes, and `receipt.json`
alongside the exports. On 2026-10-12 all **30 cases** (25 native tool cases and
5 full Python API cases) passed with the pinned tools on Ubuntu 24.04/WSL.
Nanoda is configured with `print_axioms: false` solely to suppress its optional
axiom pretty printer; all declarations and permitted axiom types are still
checked. Without this explicit setting, the pinned version defaults to printing
axioms but has no print destination, producing a pretty-printer error after
successful proof checking. The caller requires the clean, exact success line.

关键配对测试只替换定理的证明体：绑定应接受未改变的陈述，而 Nanoda 必须拒绝无效证明。未破坏的样例必须同时通过两个工具。脚本要求真实 Nanoda 二进制，任何正例或反例结果与预期不符都会失败。最后五个测试调用 `lemqo.lean.verify_lean_files`：接受含 585 条声明的样例，以及分别拒绝破坏的证明、变更的陈述、变更的相关定义和伪造公理类型。脚本在导出旁写入 `claim.json`、含实际二进制哈希的 `backends.json` 和 `receipt.json`。2026-10-12，固定工具在 Ubuntu 24.04/WSL 上通过全部 **30 个案例**（25 个原生工具案例和 5 个完整 Python API 案例）。Nanoda 配置中的 `print_axioms: false` 仅用于关闭可选的公理格式化打印；全部声明及允许公理的类型仍会检查。若不显式设置，固定版本默认打印公理但没有打印目的地，导致证明检查成功后出现格式化打印错误。调用方要求无错误、精确一致的成功行。

<a id="attribution"></a>

## Attribution / 来源与署名

- [Comparator](https://github.com/leanprover/comparator/tree/d03acab154d269c06e60e4de7e4cc85deebff94b), Apache-2.0.
- [lean4export](https://github.com/leanprover/lean4export/tree/076e8e57707e813375e8f9da8bf989799ace9680), Apache-2.0; NDJSON format 3.1.0.
- [Nanoda 0.4.19](https://github.com/ammkrn/nanoda_lib/tree/0f88b5f382f0f3f08aed4af0dd6c0e48c3fd7a44), Apache-2.0; invoked separately.

- [Comparator](https://github.com/leanprover/comparator/tree/d03acab154d269c06e60e4de7e4cc85deebff94b)，Apache-2.0。
- [lean4export](https://github.com/leanprover/lean4export/tree/076e8e57707e813375e8f9da8bf989799ace9680)，Apache-2.0，NDJSON 格式 3.1.0。
- [Nanoda 0.4.19](https://github.com/ammkrn/nanoda_lib/tree/0f88b5f382f0f3f08aed4af0dd6c0e48c3fd7a44)，Apache-2.0，单独调用。

The primitive list and Comparator invocation pattern in `Main.lean` adapt
Henrik Böving's upstream `Main.lean`, copyright 2025 Lean FRO, LLC.

`Main.lean` 的原语列表和 Comparator 调用方式改编自 Henrik Böving 的上游 `Main.lean`，原版权为 2025 Lean FRO, LLC。
