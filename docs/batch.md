# Batch verification and recovery / 批量核验与恢复

v0.3 separates the trusted producer into three phases. Each selected target is
attempted even if another fails. The final exit status is nonzero if any target
failed. `batch-summary.json` is atomically updated after each completed target;
each success has `receipt.json`, and each failure has `failed.json` with a code,
message and elapsed time. A new attempt removes stale success evidence for the
target it is about to process. An interrupted target has no success receipt.

v0.3 将可信生产器拆为三个阶段。单个目标失败后，仍会尝试其余选定目标；只要有目标失败，整批退出码就非零。每个目标结束后原子更新 `batch-summary.json`；成功写入 `receipt.json`，失败写入带错误码、原因和耗时的 `failed.json`。新一轮处理会清除该目标过期的成功回执；被中断的目标不会留下成功回执。

```sh
python tools/openai_certificates.py --phase build --work /tmp/lemqo-openai --out /tmp/certificates
python tools/openai_certificates.py --phase export --work /tmp/lemqo-openai --out /tmp/certificates
python tools/openai_certificates.py --phase check --work /tmp/lemqo-openai --out /tmp/certificates --backends /tmp/lemqo-backends/backends.json --timeout 7200
```

| Phase / 阶段 | Behavior / 行为 |
| --- | --- |
| `build` | Prepare pinned workspace, build exporter, optionally fetch Mathlib cache, build challenge/solution modules / 准备固定工作区，构建导出器，可选获取 Mathlib 缓存，构建挑战及解答模块 |
| `export` | Use existing exporter and `.olean` files through `lake env`; no `lake build` or cache download / 通过 `lake env` 使用已有导出器和 `.olean`；不调用构建或下载缓存 |
| `check` | Validate the export checkpoint, then run the offline verifier; no Lean or Lake needed / 核对导出检查点后运行离线验证；不需要 Lean 或 Lake |
| `all` (default / 默认) | Build → export → check for each selected target / 对每个选定目标执行构建、导出、检查 |

`--only ID` may be repeated. IDs come from `corpus/openai/catalog.json`, without
a code-side allowlist; an unknown ID reports the available IDs. Omit it for all
catalog candidates. Build/export currently require Linux/WSL and the pinned
toolchains. `--work` remains required for CLI compatibility but is unused in
the check phase. Functions `build_target`, `export_target`, and `check_target`
are also independently callable by trusted local drivers.

可重复传入 `--only ID`。ID 来自语料目录，无代码侧硬编码列表；未知 ID 的错误会列出可用项。省略时处理全部目录候选。构建与导出目前需要 Linux/WSL 和固定工具链。为保持 CLI 兼容，检查阶段仍要求传入 `--work`，但不会使用它。可信本地驱动也可独立调用 `build_target`、`export_target`、`check_target`。

## Reuse / 复用

```sh
python tools/openai_certificates.py --work /tmp/lemqo-openai --out /tmp/certificates --backends /tmp/lemqo-backends/backends.json --reuse-exports --timeout 7200
python tools/openai_certificates.py --phase check --work /tmp/lemqo-openai --out /tmp/certificates --backends /tmp/lemqo-backends/backends.json --resume --timeout 7200
```

`--reuse-exports` skips build/export only when both exports, the claim, and the
completed provenance checkpoint match their exact hashes, selected theorem
array, current catalog, upstream revision, and pinned Lake manifest. Changed,
partial or v0.2 checkpoints are regenerated in `all`/`export`; `check` rejects
them. An existing export by itself is insufficient. `--resume` additionally
audits an existing success receipt and compares the backend configuration and
actual executable hashes. A matching receipt is labelled **reused**, not a new
kernel check. Missing/stale receipts are checked again. This assumes the local
checkpoint and previous receipt come from a trusted run: hashes do not prevent
someone from forging a self-consistent receipt. Neither option resumes the
middle of a running Nanoda check; that individual check starts again.

`--reuse-exports` 仅在两份导出、claim 和完整溯源检查点的精确哈希、选定定理数组、当前目录、上游提交和固定 Lake 清单均匹配时跳过构建及导出。变更、不完整或 v0.2 检查点会在 `all`/`export` 重新生成，在 `check` 被拒绝。仅存在导出文件还不够。`--resume` 还会审计已有成功回执，并比较后端配置及实际可执行文件哈希。匹配的回执标为 **reused**，不表示新跑了一次内核检查；缺失或过期回执会重新检查。这里假定本地检查点和之前回执来自可信运行：哈希不能防止伪造一份自洽的回执。两种开关都不能恢复 Nanoda 的内部执行进度；被中断的单次检查需重来。

Provenance is written last; `.partial` files are never reused. Do not run two
producers against the same output or Lake workspace concurrently. Catalog
changes conservatively invalidate every cached target. Keep large exports
outside Git. Plain `lemqo check-lean` still accepts v0.2 exports and claims;
the stricter producer checkpoint does not change the public certificate format.

溯源文件最后写入；`.partial` 文件不会复用。不要让两个生产器同时写入相同输出目录或 Lake 工作区。目录变更会保守地使所有缓存目标失效。大型导出应保存在 Git 之外。普通 `lemqo check-lean` 仍可使用 v0.2 导出与 claim；生产器检查点的额外要求不改变公共证书格式。

## Heavy targets and diagnostics / 重目标与诊断

The default check deadline remains 1800 seconds; heavy targets may need
`--timeout 7200`. The Step-5 field report described one check taking 4767 seconds
and repeated Lake trace scans taking 3.5–6 minutes. These are reported workload
observations, not universal performance promises. Running export/check phases
separately avoids repeating a completed build or trace scan. The deadline
covers offline verification, not the producer's Lake build/export commands.

检查默认时限仍为 1800 秒；重目标可能需要 `--timeout 7200`。Step-5 实测反馈报告过一次 4767 秒检查，以及每轮 3.5–6 分钟的 Lake trace 扫描。这些是特定工作负载的反馈，不是通用性能承诺。分开运行导出及检查可避免重复已完成的构建或 trace 扫描。此时限覆盖离线验证，不覆盖生产器的 Lake 构建及导出命令。

The CLI prints phase changes and ten-second elapsed-time heartbeats to stderr;
`--json` stdout remains a single receipt. `check-lean --quiet` suppresses these
logs. Nanoda reports no incremental completed-declaration count: the heartbeat
shows the total and elapsed time, never a fabricated percentage. Python API
users may pass `progress=callback` and `progress_interval=10`.

CLI 向 stderr 打印阶段变化及每十秒的耗时心跳；`--json` 的 stdout 仍只有一份回执。`check-lean --quiet` 可关闭日志。Nanoda 不报告已完成声明数，因此心跳仅显示总量和耗时，不虚构百分比。Python API 可传入 `progress=callback` 和 `progress_interval=10`。

Rejections distinguish `backend-exit` (nonzero exit), `backend-signal` (POSIX
signal), `backend-cpu-limit` (SIGXCPU), and `lean-timeout` (wall deadline).
SIGKILL cannot reliably distinguish an OOM kill, hard resource limit or an
external kill. Linux gives the CPU soft limit a one-second hard-limit grace so
SIGXCPU is observable; the independent wall deadline still applies.

拒绝区分 `backend-exit`（非零退出）、`backend-signal`（POSIX 信号）、`backend-cpu-limit`（SIGXCPU）及 `lean-timeout`（墙钟时限）。无法仅凭 SIGKILL 判断是内存不足、硬资源上限还是外部终止。Linux 的 CPU 软上限与硬上限相差一秒，以便观察 SIGXCPU；独立的墙钟时限仍然适用。

<a id="audit-receipt"></a>

## Audit an existing receipt / 审计已有回执

```sh
python -m lemqo audit-receipt receipt.json --reference reference.ndjson --solution solution.ndjson --claim claim.json --json
```

This streams both exports through strict preflight, recomputes SHA256, byte,
record and declaration counts, and checks the claim, target/axiom arrays and
success fields. It accepts v0.2 receipts without timing. New v0.3 Lean receipts
add UTC `started_at`, `duration_seconds`, and reference byte/record/declaration
counts. Timing is observational metadata, not deterministic proof identity.

此命令对两份导出流式执行严格预检，重算 SHA256、字节数、记录数及声明数，并核对 claim、定理/公理数组和成功状态字段。它兼容不含时间信息的 v0.2 回执。v0.3 Lean 回执新增 UTC `started_at`、`duration_seconds` 及参考导出的字节数/记录数/声明数。时间是观察元数据，不是确定性的证明标识。

Success is **CONSISTENT** / `status: "consistent"`, with
`proof_verified: false`. No backend is invoked or authenticated. A forged
receipt can be internally consistent; use `check-lean` for a fresh mathematical
check. The audit remains linear in export size but avoids expensive kernel work.

成功结果为 **CONSISTENT** / `status: "consistent"`，并带有 `proof_verified: false`。不会调用或认证后端。伪造回执也可能内部一致；如需新的数学检查，应运行 `check-lean`。审计耗时仍与导出大小成正比，但避免了昂贵的内核工作。
