<a id="v01-local-validation-record"></a>

# v0.1 local validation record / v0.1 本地验证记录

Recorded on 2026-10-12 for the initial 0.1.0 release candidate.

本记录于 2026-10-12 为初始 0.1.0 发布候选版编写。

| Check / 检查 | Result / 结果 |
| --- | --- |
| Environment / 环境 | Windows; CPython 3.12.10 |
| Full standard-library test suite / 完整标准库测试套件 | 49 tests passed / 49 项测试通过 |
| Example corpus / 示例语料 | Seven valid proofs accepted; two invalid certificates rejected / 七个有效证明被接受，两个无效证书被拒绝 |
| Independent finite Kripke oracle / 独立有限 Kripke 语义参照 | 6,000 deterministic candidates, all ten rules; 3,706 accepted and 2,294 rejected / 6,000 个确定性候选覆盖全部十条规则，接受 3,706 个、拒绝 2,294 个 |
| Semantic observations / 语义观测 | Each accepted result's retained context checked on 145 finite world/valuation observations / 对每个接受结果的保留上下文，检查 145 个有限世界/赋值观测 |
| Archive reproducibility / 归档可复现性 | Two builds compared byte for byte, including checksum files / 两次构建逐字节比较，包括校验和文件 |
| ZIP application / ZIP 应用 | Valid and invalid examples executed outside the checkout in Python isolated mode / 在检出目录外以 Python 隔离模式运行有效和无效示例 |
| Extracted source / 解压后的源码 | Quickstart executed outside the original checkout / 在原检出目录外运行快速入门 |
| Optional pip installation / 可选 pip 安装 | Built and installed into a fresh virtual environment; installed CLI accepted/rejected the expected examples outside the checkout / 在新的虚拟环境构建安装，并在检出目录外确认已安装 CLI 按预期接受/拒绝示例 |
| Release checks / 发布检查 | Required files, local Markdown links, versions and standard-library runtime imports passed / 必需文件、本地 Markdown 链接、版本和标准库运行时导入检查通过 |

A separate GPT-6 Astra reviewer scrutinized the checking modules and performed
targeted adversarial checks. A GPT-6 Luna reviewer checked research and
documentation consistency. No concrete logic or claim-binding defect was found
in these reviews. This was AI-assisted development and review, not a completed
independent human audit or a formal proof of implementation correctness.

另一位 GPT-6 Astra 审阅者仔细检查了验证模块并进行了针对性的对抗检查。GPT-6 Luna 审阅者检查了研究内容和文档一致性。这些审阅没有发现具体的逻辑或 claim 绑定缺陷。这是 AI 辅助的开发与审阅，并非已完成的独立人工审计，也不是实现正确性的形式化证明。

The rule checker is 200 lines including comments and blank lines; the complete
`lemqo/` Python checking path is 425 lines. These counts help locate the code
to inspect; they are not a measurement of total trusted base, which also
includes Python and its relevant standard library.

规则检查器共 200 行，包含注释和空行；完整的 `lemqo/` Python 检查路径共 425 行。这些数字便于定位待检查代码；它们不代表可信计算基础（TCB）的总规模，后者还包括 Python 及其相关标准库。

Reproduce the checks with `python tools/check_release.py`. The finite-model
corpus is bounded testing evidence and does not establish correctness for all
inputs. The mathematical soundness argument is in [trust.md](trust.md).
Remote validation is recorded separately in the public repository's
[GitHub Actions](https://github.com/axiomzero-qed/Lemqo/actions), with each run tied to
its commit. This table records local checks; it is not a claim that all future
remote runs pass. No PyPI publication has been performed.

使用 `python tools/check_release.py` 可复现这些检查。有限模型语料属于有界测试证据，不能证明所有输入均正确。数学健全性论证见 [trust.md](trust.md)。远程验证另行记录在公开仓库的 [GitHub Actions](https://github.com/axiomzero-qed/Lemqo/actions) 中，每次运行都关联到相应提交。本表记录本地检查，不表示未来所有远程运行都会通过。尚未发布到 PyPI。
