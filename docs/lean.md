<a id="independent-checking-of-lean-exports"></a>

# Independent checking of Lean exports / Lean 导出的独立验证

Lemqo v0.2 adds a separate verification path for selected Lean 4 certificates.
The small IPL calculus and `lemqo check` remain available. The Lean path uses
existing implementations rather than adding dependent types to the IPL kernel.
Its trusted boundary is substantially larger than the IPL path.

Lemqo v0.2 为选定的 Lean 4 证书增加独立验证路径。小型 IPL 演算和 `lemqo check` 仍可使用。Lean 路径复用已有实现，不向 IPL 内核加入依赖类型；其可信边界显著大于 IPL 路径。

v0.3 adds [batch recovery, heartbeat diagnostics and receipt audits](batch.md),
[multi-theorem corpus admission](corpus-targets.md), and an optional
[MCP stdio server](mcp.md), preserving the acceptance contract below.

v0.3 增加[批量恢复、心跳诊断及回执审计](batch.md)、[多定理语料入库](corpus-targets.md)及可选 [MCP stdio 服务](mcp.md)，保留下述验收契约。

<a id="acceptance-contract"></a>

## Acceptance contract / 验收契约

```sh
python -m lemqo check-lean solution.ndjson \
  --claim claim.json --reference reference.ndjson \
  --backends /tmp/lemqo-backends/backends.json --json
```

The caller selects the claim, reference, and trusted backend configuration
independently of the submitted proof. A proof cannot choose any of them.
Verification accepts only when all of the following complete:

调用方应独立于提交的证明选择陈述、参考导出和可信后端配置。证明不能自行选择这些内容。只有下列步骤全部完成后，验证才会接受：

1. Copy both exports into a private temporary directory, then strictly preflight
   the exact copied bytes. No supplied Lean source or `.olean` is executed.
2. Authenticate the reference's byte length and SHA256 against the claim.
3. Use the offline Comparator bridge to match the target theorem types, their
   recursively referenced definitions, permitted axiom types, and fixed
   kernel-sensitive primitives. No definition holes are permitted.
4. Require Nanoda to check **every** declaration in the same solution snapshot,
   including all exported proof dependencies. Require its complete, clean
   success message with the exact preflight declaration count.

1. 将两份导出复制到私有临时目录，严格预检复制后的精确字节。不执行提交的 Lean 源码或 `.olean`。
2. 对照陈述中的字节长度及 SHA256，确认参考导出的身份。
3. 使用离线 Comparator 桥接程序，匹配目标定理类型、递归引用的定义、允许的公理类型及固定的内核敏感原语。不允许定义缺口。
4. 要求 Nanoda 检查同一解答快照中的**每一条**声明，包括全部导出的证明依赖；必须获得完整、无错误的成功消息，并且声明数与预检结果精确相同。

Missing targets, an axiom or definition presented as the target theorem,
unapproved axioms, unsafe/partial declarations, mismatches, crashes, timeouts,
and incomplete backend output are rejection. A statement match is insufficient.
The bridge deliberately does not call the Lean proof kernel to accept proofs.

缺失目标、将公理或定义冒充目标定理、未经允许的公理、unsafe/partial 声明、不匹配、崩溃、超时或后端输出不完整，均导致拒绝。仅匹配陈述不足以接受证明。桥接程序的证明验收不调用 Lean 证明内核。

The receipt identifies the claim, reference, solution, backend configuration,
and native binaries by hashes. These hashes identify bytes; they do not prove
logical soundness or authenticate the origin of an arbitrary binary.

回执通过哈希标识陈述、参考导出、解答、后端配置及原生二进制程序。哈希仅标识字节，不证明逻辑健全性，也不验证任意二进制程序的来源。

<a id="logic-and-axioms"></a>

## Logic and axioms / 逻辑与公理

This path checks Lean's dependent type theory as implemented by the pinned
Nanoda version, including universes, inductives, recursion, quotient support,
and enabled natural/string literal extensions. It does not translate a Lean
theorem into a propositional approximation. The supported export subset and
backend limits can reject valid Lean proofs; broad compatibility is not claimed.

本路径检查固定 Nanoda 版本所实现的 Lean 依赖类型论，包括宇宙层级、归纳类型、递归、商类型支持以及已启用的自然数/字符串字面量扩展。它不把 Lean 定理转换为命题逻辑近似。支持的导出子集及后端限制可能拒绝有效 Lean 证明，因此不声称广泛兼容。

Claims may permit any subset of `propext`, `Classical.choice`, and `Quot.sound`.
The producer exports every permitted axiom, even if unused, and the bridge
compares its **type** with the reference. Familiar names alone are insufficient.
The receipt lists permitted axioms, not a minimal set of axioms actually used.
Reference theorem bodies may use `sorryAx`; they are specification holes, never
accepted proof evidence. `sorryAx` is always forbidden in the solution.

陈述可以允许 `propext`、`Classical.choice` 和 `Quot.sound` 的任意子集。生成器须导出每个允许的公理，即使它未被定理使用；桥接程序将其**类型**与参考导出比较。仅有熟悉的名称不足以通过检查。回执列出的是允许的公理，不是实际使用公理的最小集合。参考定理的证明体可使用 `sorryAx`，但它只是规范缺口，不能作为被接受的证明证据。解答中始终禁止 `sorryAx`。

<a id="claim-format"></a>

## Claim format / 陈述格式

Exactly these fields are required, with no extra keys:

必须恰好包含下列字段，不允许额外键：

```json
{
  "format": "lemqo-lean-claim-v1",
  "name": "chosen-main-result",
  "theorem_names": ["SelectedNamespace.main_theorem"],
  "permitted_axioms": ["propext", "Classical.choice", "Quot.sound"],
  "reference": {
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "bytes": 1
  },
  "lean_version": "4.34.1",
  "lean_githash": "5045d0056413266e57c625dcd7c365b10e377c52",
  "export_format": "3.1.0"
}
```

The zero digest is a schema example, not a runnable reference. Target arrays
contain 1–32 distinct ASCII names with identifier namespace components; axiom
arrays may be empty. Names of declarations internal to the export may include
Unicode and numeric components. The trusted reference must actually contain
each selected theorem and every permitted axiom.

全零摘要只是模式示例，不对应可运行参考导出。目标数组包含 1–32 个互异 ASCII 名称，各命名空间分量为标识符；公理数组可以为空。导出内部声明名可以包含 Unicode 和数字分量。可信参考导出必须实际包含每个选定定理和每个允许的公理。

<a id="strict-export-subset-and-limits"></a>

## Strict export subset and limits / 严格导出子集与限制

Inputs are uncompressed UTF-8 NDJSON with exactly one metadata record first.
Metadata must identify `lean4export` 3.1.0, format 3.1.0, and the exact Lean
release above. Each subsequent record has exactly one supported tag; all fields,
scalar types, and existing DAG back-references are checked. Unknown fields,
duplicate object keys, floats, negative numbers, nonfinite numbers, malformed
Unicode, blank records, trailing data, repeated metadata, and `mdata` are rejected.
Name/universe/expression indices must be dense; anonymous name and universe
zero are implicit. Declaration forward dependencies are handled by the native
parsers/checker, including mutual inductives, rather than treated as proof steps.

输入为未压缩 UTF-8 NDJSON，第一条必须是唯一的元数据记录。元数据须标识 `lean4export` 3.1.0、格式 3.1.0 和上述精确 Lean 版本。后续每条记录必须恰好具有一个受支持标签；所有字段、标量类型及已有 DAG 的向后引用均须检查。未知字段、重复对象键、浮点数、负数、非有限数、非法 Unicode、空记录、尾随数据、重复元数据和 `mdata` 均被拒绝。名称/宇宙层级/表达式索引必须连续；匿名名称和宇宙零层级隐式存在。包括相互归纳类型在内的声明前向依赖，由原生解析器和验证器处理，而不是当作证明步骤处理。

Fixed bounds are 4 GiB per export, 4 MiB per record, 50 million records,
16 nested JSON containers, one million names, and 64 MiB cumulative rendered
name characters. Names are at most 4096 characters; natural literal strings
are canonical decimal with at most 100,000 digits. Other numeric fields follow
the supported backend's unsigned ranges. These are acceptance restrictions,
not additional logical rules.

固定限制为每份导出 4 GiB、每条记录 4 MiB、5,000 万条记录、16 层 JSON 容器、100 万个名称，以及渲染后名称累计 64 × 1024² 个字符。名称长度最多 4096 个字符；自然数字面量字符串须为规范十进制写法，最多 100,000 位。其他数字字段遵循受支持后端的无符号范围。这些是验收限制，不是新增逻辑规则。

The default total deadline is 1800 seconds (`--timeout 1` through `7200`).
Each backend's stdout and stderr are limited to 64 KiB. Linux execution also
limits address space to 10 GiB, CPU time to the remaining deadline, file writes
to zero bytes, and disables core dumps. Failed POSIX process groups are killed.
The tested native platform is Linux, including WSL; other platforms do not
receive the Linux resource limits. These measures bound common failures; they
are not an operating-system sandbox or a guarantee against kernel defects.

默认总时限为 1800 秒，`--timeout` 可设置为 1 到 7200 秒。每个后端的 stdout 和 stderr 分别限制为 64 KiB。Linux 下还将地址空间限制为 10 GiB、CPU 时间限制为剩余时限、文件写入限制为零字节，并禁用核心转储。失败的 POSIX 进程组会被终止。已测试的原生平台是 Linux（包括 WSL）；其他平台不具有这些 Linux 资源限制。这些措施约束常见失败情况，不是操作系统沙箱，也不保证证明内核没有缺陷。

<a id="build-and-reproduce"></a>

## Build and reproduce / 构建与复现

Use Linux/WSL with Python 3.11+, Git, Lean **4.34.1** and Rust **1.94.0** on PATH.
Install Lean through its normal [toolchain instructions](https://github.com/leanprover/lean4#building-from-source)
or the [pinned release](https://github.com/leanprover/lean4/releases/tag/v4.34.1).
Then build the native programs from this checkout:

使用 Linux/WSL，并将 Python 3.11+、Git、Lean **4.34.1** 和 Rust **1.94.0** 放入 PATH。通过常规[工具链说明](https://github.com/leanprover/lean4#building-from-source)或[固定版本发布页](https://github.com/leanprover/lean4/releases/tag/v4.34.1)安装 Lean，然后从当前检出构建原生程序：

```sh
python tools/build_lean_backends.py --work /tmp/lemqo-backends
python /tmp/lemqo-backends/bridge/tests/run_offline.py \
  --nanoda /tmp/lemqo-backends/nanoda/target/release/nanoda_bin --lemqo-root .
```

The build tool checks the toolchain, locked Git revisions, clean source files,
and binary SHA256. It writes `backends.json` and `build-information.json`.
The second command generates trusted fixtures and exercises the actual
native programs, including a correct proof and a corrupted proof whose statement
still matches. It has no backend-skip mode.

构建工具检查工具链、锁定的 Git 版本、源码无修改状态及二进制 SHA256，并写入 `backends.json` 和 `build-information.json`。第二条命令生成可信测试样例并运行真实原生程序，包括正确证明以及陈述仍匹配但证明已被破坏的输入。没有跳过后端的运行模式。

Producer builds may execute pinned upstream Lean metaprograms. They belong to
the trusted preparation stage, not the offline checker. The OpenAI producer
uses only this repository's hash-checked [source snapshot](openai.md), a minimal
Lake project, and pinned Mathlib. Mathlib's build cache is a preparation-stage
trust input; use `--no-cache` in a fresh work directory for a full source build. Offline
verification neither fetches a cache nor runs Lake.

生成器的构建可能执行固定版本的上游 Lean 元程序；它们属于可信准备阶段，不属于离线验证器。OpenAI 生成器仅使用本仓库经过哈希检查的[源码快照](openai.md)、最小 Lake 项目和固定 Mathlib。Mathlib 构建缓存是准备阶段的信任输入；如需完全从源码构建，应在新的工作目录中使用 `--no-cache`。离线验证不获取缓存，也不运行 Lake。

Pinned dependencies:

固定版本依赖：

| Component / 组件 | Source revision / 源码版本 | Role / 作用 |
| --- | --- | --- |
| [Nanoda 0.4.19](https://github.com/ammkrn/nanoda_lib/tree/0f88b5f382f0f3f08aed4af0dd6c0e48c3fd7a44) | `0f88b5f382f0f3f08aed4af0dd6c0e48c3fd7a44` | Independent Rust proof checking / 独立 Rust 证明检查 |
| [Comparator](https://github.com/leanprover/comparator/tree/d03acab154d269c06e60e4de7e4cc85deebff94b) | `d03acab154d269c06e60e4de7e4cc85deebff94b` | Statement/definition/axiom binding / 陈述、定义及公理绑定 |
| [lean4export](https://github.com/leanprover/lean4export/tree/076e8e57707e813375e8f9da8bf989799ace9680) | `076e8e57707e813375e8f9da8bf989799ace9680` | Dependency-complete certificate production and format parsing / 完整依赖证书生成及格式解析 |
| [Mathlib](https://github.com/leanprover-community/mathlib4/tree/d13f23b723b8a846827a245b89c10fc7d3f11612) | `d13f23b723b8a846827a245b89c10fc7d3f11612` | Selected mathematical definitions and proofs / 选定的数学定义与证明 |

The exporter/Comparator revisions target Lean 4.34.0 upstream; Lemqo builds
and tests them on 4.34.1. All are Apache-2.0. Native binary builds are pinned
and identifiable, but are not claimed byte reproducible across build hosts.
Lemqo's Python/source archives retain their deterministic packaging contract.

上游 exporter/Comparator 版本面向 Lean 4.34.0；Lemqo 使用 4.34.1 构建并测试。它们均采用 Apache-2.0。原生二进制构建版本已固定且可识别，但不声称不同构建宿主产生逐字节一致结果。Lemqo 的 Python/源码归档仍遵循确定性打包契约。

<a id="trust-and-statement-fidelity"></a>

## Trust and statement fidelity / 信任与陈述忠实度

Mathematical validity depends on the calculus and allowed axioms. Statement
fidelity depends on the independently reviewed reference and its definitions.
Implementation correctness depends on Lemqo's parser/orchestration, the
Comparator/Export parser and binding code, Nanoda, their compilers/runtimes,
and the OS/hardware. The Lean compiler/runtime is trusted to execute the
binding program; its proof kernel is not the independent proof-checking step.

数学有效性依赖演算和允许的公理。陈述忠实度依赖经独立审查的参考导出及其定义。实现正确性依赖 Lemqo 解析和流程控制、Comparator/Export 解析器及绑定代码、Nanoda、它们的编译器/运行环境和操作系统/硬件。Lean 编译器/运行环境因执行绑定程序而受信任；其证明内核不是独立证明检查步骤。

A valid receipt does not establish that a reference expresses a paper's prose,
that a claim is novel, or that the checking implementations have no defects.
Independent rebuilding, source review, mutation tests, and implementation
diversity provide audit evidence, not an end-to-end formal correctness proof.

有效回执不确立参考导出表达了论文原意，不确立陈述具有新颖性，也不确立验证实现没有缺陷。独立重建、源码审查、变异测试及实现多样性提供审计证据，而不是从输入到结果的完整形式化正确性证明。
