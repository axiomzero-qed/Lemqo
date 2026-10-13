<a id="releasing-lemqo-v02"></a>

# Releasing Lemqo v0.2 / 发布 Lemqo v0.2

<a id="local-verification"></a>

## Local verification / 本地验证

Run from the repository root with Python 3.11+:

从仓库根目录使用 Python 3.11 或更高版本运行：

```sh
python tools/check_release.py
python tools/build_release.py --out dist
python dist/lemqo-0.2.0.pyz check examples/identity.proof.json --claim examples/identity.claim.json
```

The release check runs the complete test suite and checks documented example
outcomes, local documentation links, version consistency, required files, and
standard-library runtime imports. The IPL command remains cross-platform. The
optional Lean path has only been validated on Linux; this does not assert that
v0.2 CI or a release tag has been verified.

发布检查会运行完整测试套件，并检查文档示例结果、本地文档链接、版本一致性、必需文件及标准库运行时导入。IPL 命令仍可跨平台使用。可选 Lean 路径目前仅在 Linux 上验证；这并不表示 v0.2 的 CI 或发布标签已得到验证。

The build writes three files:

构建会生成以下三个文件：

- `lemqo-0.2.0.pyz`: source ZIP application, launched with `python`; Python is
  still required. It includes the checker and its MIT license.
  `lemqo-0.2.0.pyz`：源代码 ZIP 应用，通过 `python` 启动；仍然需要 Python。它包含检查器及其 MIT 许可证。
- `lemqo-0.2.0-source.zip`: allowlisted source, docs, tests, examples, and CI
  configuration under the `lemqo-0.2.0/` directory.
  `lemqo-0.2.0-source.zip`：位于 `lemqo-0.2.0/` 目录下的白名单源码、文档、测试、示例和 CI 配置。
- `SHA256SUMS`: exact-byte SHA-256 values for those two archives.
  `SHA256SUMS`：上述两个归档文件逐字节计算的 SHA-256 值。

Extracting the source archive and running its quickstart requires no network.
The tests build twice, compare every byte, and launch the runnable archive
from outside the checkout with Python isolated mode.

解压源码归档并运行其中的快速入门不需要网络。测试会构建两次、逐字节比较，并在检出目录之外以 Python 隔离模式启动可运行归档。

<a id="reproducibility-contract"></a>

## Reproducibility contract / 可复现性约定

Given identical allowlisted source contents after CRLF-to-LF normalization,
the archive builder produces identical bytes. It sorts paths, uses stored
uncompressed ZIP entries, fixes timestamps to 1980-01-01, and normalizes file
modes. It excludes git history, caches, build outputs, virtual environments,
and unlisted workspace files. No compiler, zlib version, local timezone, wall
clock, or package index affects these archive bytes.

对经过 CRLF 转 LF 规范化且白名单内容相同的源文件，归档构建器会生成完全相同的字节。它会对路径排序，使用不压缩的 ZIP 条目，将时间戳固定为 1980-01-01，并规范化文件模式。它排除 Git 历史、缓存、构建产物、虚拟环境和未列入清单的工作区文件。编译器、zlib 版本、本地时区、系统时钟或软件包索引都不会影响归档字节。

To independently compare builds:

如需独立比较构建结果：

```sh
python tools/build_release.py --out dist/first
python tools/build_release.py --out dist/second
```

Compare both archives and checksum files byte for byte. Checksums identify
artifacts; they are not authentication. Independently verify the source and
obtain release checksums through a trusted channel. The builder itself does
not run tests; use the release check before building.

逐字节比较两个归档和校验和文件。校验和用于标识制品，不提供身份认证。应独立核验源码，并通过可信渠道获取发布校验和。构建器本身不会运行测试；构建前请先运行发布检查。

<a id="optional-package-installation"></a>

## Optional package installation / 可选的软件包安装

For a conventional local installation:

如需进行常规本地安装：

```sh
python -m pip install .
lemqo check examples/identity.proof.json --claim examples/identity.claim.json
```

The runtime has no package dependencies. This optional installation uses a
PEP 517 setuptools build backend pinned in `pyproject.toml`; fetching it may
require network access. The archive reproducibility claim above applies to
the standard-library ZIP builder, not arbitrary wheel or installer output.
No package has been uploaded to PyPI and no package-name reservation is claimed.

运行时没有软件包依赖。此可选安装使用 `pyproject.toml` 中固定的 PEP 517 setuptools 构建后端；获取该后端可能需要网络。上文的归档可复现性声明适用于标准库 ZIP 构建器，不适用于任意 wheel 或安装器输出。尚未向 PyPI 上传软件包，也不声称已预留软件包名称。

<a id="github-publication"></a>

## GitHub publication / GitHub 发布

The public repository is [axiomzero-qed/Lemqo](https://github.com/axiomzero-qed/Lemqo).
Before publishing a release tag, review repository metadata and security-reporting
contact options and record the reviewed release commit. The homepage is
`https://lemqo.com`; no live deployment or current domain-content claim is part
of this release.

公开仓库为 [axiomzero-qed/Lemqo](https://github.com/axiomzero-qed/Lemqo)。发布标签前，应审查仓库元数据和安全问题报告联系方式，并记录经过审查的发布提交。主页是 `https://lemqo.com`；本次发布不声称网站已经上线，也不声称域名当前呈现特定内容。

Push the reviewed source, wait for CI, then create a reviewed release tag and
release described by [CHANGELOG.md](../CHANGELOG.md). The manual
`Build release artifacts` workflow tests and uploads the archives as a workflow
artifact; it never publishes a GitHub release automatically. Attach the three
reviewed files to the release and preserve the commit, CI evidence, Python
version and checksums with the release record.

推送经过审查的源码，等待 CI 完成，然后创建经过审查的发布标签和 [CHANGELOG.md](../CHANGELOG.md) 所述发布。手动的 `Build release artifacts` 工作流会测试并上传归档作为工作流制品；它不会自动发布 GitHub Release。将三个经过审查的文件附加到发布中，并在发布记录中保留提交、CI 证据、Python 版本和校验和。

The bilingual Markdown in `docs/` is the canonical documentation source.
The English IPL specification is normative for its wire format; the Chinese
text explains the same contract. A future lemqo.com site can publish these
same versioned files and link each release to its source, specification,
examples, and checksums. Avoid a second, independently edited technical
specification on the website.

`docs/` 中的双语 Markdown 是正式文档源。英文 IPL 规范是传输格式的规范性依据，中文说明同一契约。未来的 lemqo.com 网站可以发布相同的版本化文件，并将每个版本链接到其源码、规范、示例和校验和。避免在网站上另行维护一份独立编辑的技术规范。
