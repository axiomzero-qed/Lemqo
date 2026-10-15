# v0.3 validation and scope / v0.3 验证与范围

Date / 日期: 2026-10-16.

This release addresses the supplied Step-5 field report on v0.2. That report
described 10/10 selected single-theorem checks, 571,046 checked declarations,
and independent hash reconciliation. These are attributed field observations;
this release does not promote those ten targets into the repository's three
archived, independently checked corpus results or claim to have rerun them.

本次根据提供的 v0.2 Step-5 实测反馈改进。反馈报告 10/10 个选定单定理检查通过，共检查 571,046 条声明，并独立核对哈希。这些数字归属于反馈方的观察；本次没有把十个目标混入仓库已有的三个独立核验归档，也不声称重新运行过它们。

## Feedback coverage / 反馈覆盖

| Report / 反馈 | v0.3 implementation / 实现 |
| --- | --- |
| P0-1 | Exact 1–32 `theorem_names` binding in catalog, producer and claim; singular compatibility / 目录、生产器及 claim 精确绑定多定理，兼容单数写法 |
| P0-2 | Per-target rejection/error files, continuation, atomic incremental batch summary and nonzero final exit / 逐目标失败文件、继续处理、原子增量汇总及非零退出 |
| P0-3 | Independent build/export/check phases, provenance-bound export reuse, audited receipt reuse / 独立阶段、溯源绑定的导出复用、审计后复用回执 |
| P1-1 | Catalog-driven target selection, available IDs in unknown-ID error / 目录驱动目标选择，未知 ID 提示可用项 |
| P1-2 | Phase and elapsed-time heartbeats; no invented completed count / 阶段及耗时心跳，不虚构已完成数 |
| P1-3 | Distinct exit/signal/SIGXCPU/deadline rejections / 区分退出、信号、CPU 上限和时限 |
| P1-4 | Heavy-target guidance through 7200 seconds / 重目标时限说明，最高 7200 秒 |
| P1-5 | Export-only phase performs no Lake build/cache request / 仅导出阶段不执行 Lake 构建或缓存请求 |
| P2-1 | `audit-receipt`: consistency, explicitly no fresh proof verification / 回执审计明确只说明一致性 |
| P2-2 | UTC start time, elapsed seconds, reference counts / UTC 起始时间、耗时秒数、参考计数 |
| P2-3 | [Target admission guide](corpus-targets.md) with candidate and inventory contracts / 目标入库指南明确候选及清单契约 |
| P2-4 | Follows any local import root and rejects unresolved roots during catalog checks / 跟踪任意本地根，入库即拒绝未解析根 |
| P2-5 | [MCP stdio reference](mcp.md) calls existing APIs with fixed trust inputs / MCP 参考接口调用现有 API，固定可信输入 |

## Verification evidence / 验证证据

Local release check on Windows, Python 3.12.10: 102 tests, with two POSIX-only
cases skipped; all remaining tests passed. The check also validated all nine
expected IPL example outcomes, documentation links, version consistency,
standard-library runtime imports, and all 349 vendored Lean files. The website's
18 tests passed, including browser/Python result comparisons. Mobile browser
QA checked English layout, valid-proof acceptance and altered-proof rejection.

Windows / Python 3.12.10 本地发布检查：102 项测试，其中两个仅 POSIX 适用的用例跳过，其余全部通过。同时核对了九份 IPL 示例的预期结果、文档链接、版本一致性、标准库运行时导入及全部 349 份随仓库提供的 Lean 文件。网站 18 项测试通过，包括浏览器与 Python 结果对照；手机浏览器实测了英文布局、有效证明通过及篡改证明拒绝。

WSL Ubuntu 24.04 / Python 3.12: all 102 tests passed, including FIFO input
rejection and distinct POSIX signal/CPU-limit errors. The complete release
check also passed on this platform.

WSL Ubuntu 24.04 / Python 3.12：102 项测试全部通过，包括 FIFO 输入拒绝及 POSIX 信号/CPU 限额错误区分；该平台完整发布检查也已通过。

Automated tests cover the original IPL behavior and Lean orchestration plus
multi-target catalog/config matching, batch continuation and recovery, tampered
checkpoints, receipt/file mismatches, old-receipt compatibility, error categories,
MCP initialization/discovery, accepted/rejected IPL requests, trust-input override
rejection and proof-directory restrictions. Mocked native responses test control
flow, not mathematical correctness. Real native regression results and remote
CI must be identified by their actual run, separately from those unit tests.

自动测试覆盖原有 IPL 行为及 Lean 流程，并增加多定理目录匹配、批处理继续与恢复、检查点篡改、回执/文件不一致、旧回执兼容、错误分类、MCP 初始化及发现、有效/无效 IPL 请求、可信输入覆盖拒绝及证明目录限制。模拟原生响应只验证控制流程，不证明数学正确性。真实原生回归及远程 CI 必须按实际运行记录单独说明。

The [v0.2 native and theorem records](validation-v0.2.md) remain historical
evidence for the unchanged backend pins and acceptance boundary. No new
mathematical corpus expansion, general Lean compatibility, or formal correctness
proof is claimed. Resume skips completed local work under the trusted-checkpoint
assumption; receipt auditing cannot authenticate a receipt or replace Nanoda.

[v0.2 原生及定理记录](validation-v0.2.md)仍是相同后端固定版本与验收边界的历史证据。本次不声称新增数学语料、通用 Lean 兼容性或形式化正确性证明。续跑依赖可信本地检查点；回执审计不能认证回执或代替 Nanoda。
