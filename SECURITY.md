<a id="security-and-logical-correctness"></a>

# Security and logical correctness / 安全与逻辑正确性

Lemqo is experimental. Please report accepted invalid derivations,
claim-binding errors, malformed-input acceptance, resource-limit bypasses,
and release-integrity problems with the smallest reproducing input.

Lemqo 仍处于实验阶段。若发现被接受的无效推导、待核验陈述绑定错误、接受格式错误的输入、绕过资源限制或发布完整性问题，请使用尽可能小的复现输入进行报告。

Use the repository's **Security → Report a vulnerability** option if maintainers
have enabled private reporting. If no
private channel is available, open an issue asking maintainers for a private
contact without posting sensitive material. Maintainers must configure a
working private reporting channel before inviting vulnerability submissions.
There is no invented email address or currently claimed response-time guarantee.

如果维护者启用了私密报告，请使用仓库的 **Security → Report a vulnerability** 选项。如果没有私密渠道，请先创建 issue，请求维护者提供私密联系方式，不要公开敏感材料。邀请用户提交漏洞报告前，维护者必须配置可用的私密报告渠道。这里不虚构电子邮件地址，也不声称存在响应时间保证。

Include the verifier version, Python/OS versions, exact claim and proof bytes
or their safely shareable reproducer, command, exit status, and observed vs.
expected result. Distinguish a valid derivation of an unintended statement from
a checker defect; both may matter, but only the latter violates verification.

请提供核验器版本、Python/操作系统版本、准确的待核验陈述和证明字节（或可安全分享的复现材料）、命令、退出状态，以及实际结果与预期结果。请区分“对非预期陈述的有效推导”和“检查器缺陷”：两者都可能值得关注，但只有后者违反了核验保证。

For the optional Lean path, include target theorem names, export metadata,
the separately selected reference/claim, backend binary hashes and source pins.
Do not execute unknown Lean sources or backend configurations to reproduce an
untrusted certificate. The offline verifier accepts data exports; native
programs and specification inputs must be independently trusted by the caller.

对于可选 Lean 路径，请提供目标定理名称、导出元数据、单独选定的参考导出/待核验陈述、后端二进制哈希和源码固定版本。请勿执行未知 Lean 源码或后端配置来复现不可信证书。离线核验器接收的是数据导出；调用方必须独立信任原生程序和规范输入。

The [trust document](docs/trust.md) defines the input threat model and its
limits. Treat any nonzero exit, exception, interrupted execution or incomplete
receipt as failure. Only a completed check against a reviewed target provides
the stated assurance.

[信任文档](docs/trust.md)定义输入威胁模型及其限制。任何非零退出、异常、中断执行或不完整回执都应视为失败。只有针对经过审查的目标完成检查，才能提供所述保证。
