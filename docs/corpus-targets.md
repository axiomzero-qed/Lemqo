# Add a corpus target / 新增语料目标

The catalog is a trusted, pinned source inventory. Adding a candidate does not
establish that its theorem is proved; preserve `pending` until a real independent
check succeeds. Review the formal statement and its definitions separately.

语料目录是可信、固定版本的源码清单。加入候选不表示定理已获证明；在真实独立检查成功前应保留 `pending` 状态。形式陈述与定义还需要单独审查。

1. Choose one exact upstream commit. Copy the challenge `.lean`, its Comparator
   `.json`, solution module and complete local import closure into
   `corpus/openai/lean/`, retaining paths and exact bytes. Retain the upstream
   license. Do not copy build caches or `.olean` files.
   选定精确上游提交。将挑战 `.lean`、Comparator `.json`、解答模块及完整本地导入闭包复制到 `corpus/openai/lean/`，保留路径和精确字节，同时保留上游许可。不要复制构建缓存或 `.olean`。
2. Add an entry to `catalog.json` using the fields below. Theorem, definition,
   module and axiom arrays must match the upstream Comparator config exactly.
   在 `catalog.json` 中按下表加入候选。定理、定义、模块及公理数组必须与上游 Comparator 配置完全相同。
3. Inventory every copied `.lean` in `source_files` (or in `project_files` for
   upstream project metadata such as `lakefile.lean`). Update counts and hashes
   from the bytes on disk, not from reserialized text. Run the integrity checker.
   在 `source_files` 列出每份 `.lean`（`lakefile.lean` 等上游项目元数据放入 `project_files`）。用磁盘字节更新计数及哈希，不能用重新序列化的文本代替。运行完整性检查。
4. Build, export and check the target using the [batch guide](batch.md). Preserve
   its claim, receipt, production provenance and build information if publishing
   a result. Record the actual checked targets, not a count of supporting lemmas.
   按[批量指南](batch.md)构建、导出并检查。如发布结果，应保留 claim、回执、生产溯源及构建信息。记录实际检查的目标，不把辅助引理计为额外成果。

```json
{
  "id": "example_target",
  "title": "Example target",
  "theorem_names": ["Example.first", "Example.second"],
  "challenge_module": "ComparatorChallenges.Example",
  "solution_module": "OAI.Example.Main",
  "challenge_spec": "lean/ComparatorChallenges/Example.lean",
  "challenge_config": "lean/ComparatorChallenges/Example.json",
  "challenge_config_bytes": 0,
  "challenge_config_sha256": "REPLACE_WITH_EXACT_SHA256",
  "definition_names": [],
  "permitted_axioms": ["propext", "Classical.choice", "Quot.sound"],
  "enable_nanoda": false,
  "independent_check_status": "pending"
}
```

This illustrates fields, not a runnable target; replace the byte count and hash.
`enable_nanoda` mirrors upstream configuration and does **not** disable Lemqo's
mandatory independent kernel check.

此处仅示意字段，不是可运行目标；须替换字节数与哈希。`enable_nanoda` 反映上游配置，**不会**关闭 Lemqo 强制要求的独立内核检查。

| Candidate field / 候选字段 | Contract / 契约 |
| --- | --- |
| `id` | Unique lowercase `[a-z][a-z0-9_]{0,63}`; also the output directory name / 唯一小写安全 ID，也是输出目录名 |
| `title` | Human-readable description / 供人阅读的描述 |
| `theorem_names` | 1–32 unique canonical ASCII names; order must match Comparator config / 1–32 个互异规范 ASCII 名称；顺序与 Comparator 配置相同 |
| `theorem` | Backward-compatible single target; if both spellings exist, the array must equal `[theorem]` / 兼容单目标旧写法；若同时存在，数组必须等于 `[theorem]` |
| `challenge_module`, `solution_module` | Canonical module names matching the config / 与配置一致的规范模块名 |
| `challenge_spec` | Relative POSIX path under `lean/`, listed in `source_files` / `lean/` 下的 POSIX 相对路径，须在源码清单中 |
| `challenge_config` | Unique JSON path under `lean/ComparatorChallenges/` / 该目录下唯一的 JSON 配置路径 |
| `challenge_config_bytes`, `challenge_config_sha256` | Exact config bytes and lowercase SHA256 / 配置的精确字节数及小写 SHA256 |
| `definition_names`, `permitted_axioms`, `enable_nanoda` | Exact upstream values; Lemqo's supported claims still restrict permitted axioms / 与上游精确一致；Lemqo claim 仍限制允许公理集合 |
| `independent_check_status` | Evidence annotation; never a verifier input or substitute for checking / 证据注记，不是验证输入，也不能代替实际检查 |

The top-level `schema_version` remains `1`. `source_files` paths are relative to
`lean/`; each record has `path`, `bytes`, `sha256`. `source_file_count` and
`source_bytes` equal the number and summed bytes of those records.
`project_files` uses the same record shape for upstream toolchain, Lake files,
metadata and guides; these are inventoried but not all copied to the minimal
producer project. `upstream_catalogue` points to a catalogued project file such
as `lean/formalization.yaml`; it is provenance, not proof evidence.
`unique_upstream_file_count` counts the union of source paths, project paths
and candidate config paths. `upstream` records the repository, exact commit,
license path/SPDX label and exact license SHA256.

顶层 `schema_version` 仍为 `1`。`source_files` 路径相对于 `lean/`，每条含 `path`、`bytes`、`sha256`；`source_file_count` 与 `source_bytes` 分别等于这些记录的数量及字节总和。`project_files` 用同样结构记录上游工具链、Lake 文件、元数据和指南；它们纳入清单，但不全部复制到最小生产项目。`upstream_catalogue` 指向清单内的项目文件，例如 `lean/formalization.yaml`；它是溯源信息，不是证明证据。`unique_upstream_file_count` 是源码路径、项目路径及候选配置路径并集的大小。`upstream` 记录仓库、精确提交、许可证路径/SPDX 标识及许可证精确 SHA256。

```sh
python tools/check_openai_sources.py
python tools/openai_certificates.py --phase build --work /tmp/lemqo-openai --out /tmp/certificates --only example_target
```

Admission checks reject extra/missing Lean files, traversal, symlinks, duplicate
paths, changed hashes/configs and unresolved local imports. Import discovery
follows any local module root, strips nested Lean comments, and explicitly
allows the pinned external roots listed in `EXTERNAL_ROOTS` in
`tools/check_openai_sources.py`. A new dependency needs a reviewed pin and an
explicit resolver update; it must not be silently ignored. Existing package
roots are resolved by the pinned toolchain during build. Multi-target production
exports and binds every selected theorem together.

入库检查拒绝多余/缺失 Lean 文件、路径穿越、符号链接、重复路径、哈希或配置不匹配及无法解析的本地导入。导入发现会追踪任意本地模块根，去除 Lean 嵌套注释，并显式允许 `tools/check_openai_sources.py` 的 `EXTERNAL_ROOTS` 所列固定外部根。新依赖需要经审查的固定版本及解析器显式更新，不能静默忽略。已有外部包根的模块由固定工具链在构建时解析。多目标生产会一起导出并绑定所有选定定理。
