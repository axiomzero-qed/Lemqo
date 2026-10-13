<a id="v02-validation-record"></a>

# v0.2 validation record / v0.2 验证记录

Recorded on 2026-10-13. The earlier [v0.1 record](validation.md) describes the
unchanged IPL calculus; its code-size figures are historical, not counts for
the larger optional Lean path.

本记录于 2026-10-13 编写。较早的 [v0.1 记录](validation.md) 描述保持不变的 IPL 演算；其中代码规模数字是历史记录，并非更大的可选 Lean 路径的代码行数。

- The 78 standard-library test methods ran on Windows/Python 3.12.10:
  77 passed and the one POSIX FIFO case was skipped. Linux/Python 3.12.3
  runs that case as well.
  Windows/Python 3.12.10 上运行了 78 个标准库测试方法：77 项通过，一个 POSIX FIFO 用例跳过。Linux/Python 3.12.3 也运行该用例。
- The native regression driver passed 30 actual backend/public-API cases,
  including 585-declaration acceptance, corrupted-proof rejection with an
  unchanged matched statement, definition and primitive replacement, axiom-type
  spoofing, unsupported metadata and missing declarations.
  原生回归驱动通过了 30 个实际后端/公共 API 用例，包括接受 585 个声明、拒绝损坏的证明且匹配陈述保持不变、定义和原语替换、公理类型伪造、不支持的元数据以及缺失声明。
- The public offline API passed the three named OpenAI targets with 22,252,
  41,966 and 70,651 independently checked declarations. Exact scopes, claims,
  source pins and byte identities are in [openai.md](openai.md).
  公共离线 API 通过了三个具名 OpenAI 目标检查，独立检查的声明数分别为 22,252、41,966 和 70,651。准确范围、claim、源码固定版本及字节标识见 [openai.md](openai.md)。
- Lean 4.34.1's official ZIP SHA256 was verified. The repository's safe extractor
  unpacked the actual release under Linux and the extracted executable reported
  the expected version and full commit.
  Lean 4.34.1 官方 ZIP 的 SHA256 已核验。仓库的安全解压器在 Linux 下解压了实际发布包，解压出的可执行文件报告了预期版本和完整提交号。
- Source integrity checks cover all 349 vendored Lean files, comparator configs,
  project metadata and retained Apache license. Native sources are locked to
  exact Git revisions; Nanoda is built with its committed Cargo lock file.
  源码完整性检查覆盖全部 349 个 vendored Lean 文件、Comparator 配置、项目元数据及保留的 Apache 许可证。原生源码锁定到精确 Git 修订；Nanoda 使用仓库提交的 Cargo lock 文件构建。
- Source/Python archives are compared byte for byte and executed outside the
  checkout. Documentation links, versions and runtime imports are checked.
  源码归档和 Python 归档会逐字节比较，并在检出目录之外执行。文档链接、版本和运行时导入也会检查。

Native binary reproducibility across hosts, full Lean compatibility, a human
audit and an end-to-end formal implementation proof are not established by
these checks. AI-assisted implementation/review and bounded tests provide
evidence for inspection. The native workflow tests the small fixture; the three
large paper checks above were performed locally and are independently reproducible.
Remote CI is tied to the repository's actual commit and recorded in
[GitHub Actions](https://github.com/axiomzero-qed/Lemqo/actions).

这些检查尚未证明跨主机原生二进制可复现性、完整 Lean 兼容性，也未完成人工审计或端到端的实现形式化证明。AI 辅助的实现/审阅和有界测试提供了供检查的证据。原生工作流测试小型 fixture；上文三个大型论文检查是在本地完成的，并可独立复现。远程 CI 与仓库实际提交关联，并记录在 [GitHub Actions](https://github.com/axiomzero-qed/Lemqo/actions)。
