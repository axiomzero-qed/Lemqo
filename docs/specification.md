<a id="lemqo-v1-certificate-specification"></a>

# Lemqo v1 certificate specification / Lemqo v1 证明证书规范

This is the normative IPL format and calculus introduced in v0.1.0 and
preserved unchanged in v0.2.0. The wire formats are `lemqo-claim-v1` and
`lemqo-proof-v1`, with fixed logic identifier `ipl`. Any incompatible logical
or format change needs a new identifier. Resource-policy changes must be
documented separately.

本文规定 v0.1.0 引入、在 v0.2.0 中保持不变的 IPL 格式和演算。传输格式为 `lemqo-claim-v1` 和 `lemqo-proof-v1`，逻辑标识固定为 `ipl`。任何不兼容的逻辑或格式变更都必须使用新标识。资源策略的变更必须单独记录。

<a id="formulas-and-semantics"></a>

## Formulas and semantics / 公式与语义

Abstract formulas are finite trees:

抽象公式是有限树：

```text
F ::= Atom(name) | False | Imp(F,F) | And(F,F) | Or(F,F)
name ::= [A-Za-z][A-Za-z0-9_]{0,63}
```

Names are case-sensitive uninterpreted propositional variables. There are no
definitions or reserved mathematical meanings attached to names. `Atom("false")`
and `False` are different formulas. Formula equality is exact tree equality;
there is no implicit associativity, commutativity, reduction, or equivalence.
Negation can be written `Imp(A,False)`; truth can be written `Imp(False,False)`.
These are explanations, not additional syntax or primitive rules.

名称是区分大小写、没有解释的命题变量。名称不附带定义或保留的数学含义。`Atom("false")` 与 `False` 是不同公式。公式相等指树结构完全相等，不隐含结合律、交换律、归约或逻辑等价。否定可写为 `Imp(A,False)`，真可写为 `Imp(False,False)`；这些只是说明，不是新增语法或原始推理规则。

A Kripke model consists of a nonempty partially ordered set of worlds `(W, ≤)`
and an upward-closed set of worlds for each atom. Forcing is defined by:

Kripke 模型由非空的世界偏序集 `(W, ≤)` 以及每个原子对应的向上封闭世界集合组成。强制关系定义如下：

- `w ⊩ P` exactly when `w` belongs to the atom's set.
- No world forces `False`.
- `w ⊩ And(A,B)` exactly when `w ⊩ A` and `w ⊩ B`.
- `w ⊩ Or(A,B)` exactly when `w ⊩ A` or `w ⊩ B`.
- `w ⊩ Imp(A,B)` exactly when every `v ≥ w` that forces `A` also forces `B`.

- 当且仅当 `w` 属于原子对应的集合时，`w ⊩ P`。
- 没有世界强制 `False`。
- 当且仅当 `w ⊩ A` 且 `w ⊩ B` 时，`w ⊩ And(A,B)`。
- 当且仅当 `w ⊩ A` 或 `w ⊩ B` 时，`w ⊩ Or(A,B)`。
- 当且仅当每个强制 `A` 的后继世界 `v ≥ w` 也强制 `B` 时，`w ⊩ Imp(A,B)`。

These clauses are persistent upwards. A sequent `Γ ⊢ C` is semantically valid
when, in every model and world, forcing every formula in the finite set `Γ`
implies forcing `C`. The rules below are sound for this semantics. Acceptance
checks a derivation, rather than running a truth-table or finite-model test.
Excluded middle and double-negation elimination are not built-in principles.

以上关系具有向上持久性。如果在每个模型、每个世界中，强制有限集合 `Γ` 中的全部公式都蕴含强制 `C`，则相继式 `Γ ⊢ C` 在语义上有效。下述规则对这一语义是健全的。验收检查具体推导，不是运行真值表或有限模型测试。排中律和双重否定消去不是内置原则。

<a id="byte-level-format"></a>

## Byte-level format / 字节级格式

Each document is one strict UTF-8 JSON object. A BOM, duplicate object keys,
comments, trailing data, malformed UTF-8, and lone surrogate escapes are
rejected. String escapes are decoded before identifiers are compared; `"P"`
and `"\u0050"` denote the same atom. Whitespace and object-key ordering do not
affect derivability. Input hashes refer to original bytes, so these changes do
affect receipt hashes.

每份文档都是一个严格的 UTF-8 JSON 对象。BOM、重复对象键、注释、尾随数据、非法 UTF-8 和孤立代理项转义均被拒绝。比较标识符前先解码字符串转义，因此 `"P"` 与 `"\u0050"` 表示同一个原子。空白和对象键顺序不影响可推导性；输入哈希对应原始字节，因此这些变化会改变回执中的哈希。

Only integer JSON numbers with at most nine digits, excluding the minus sign,
are supported. Decimal/exponent notation, NaN, Infinity, and negative zero are
rejected. Every index must have exact integer type, be nonnegative, and satisfy
its range check; booleans are never indices. JSON booleans and null have no
valid location in either document's schema.

只支持最多九位数字的 JSON 整数，负号不计入位数。小数或指数写法、NaN、Infinity 和负零均被拒绝。每个索引必须严格属于整数类型、非负且通过范围检查，布尔值不能作为索引。两种文档的模式均不接受 JSON 布尔值或 null。

All listed keys are mandatory; additional keys are rejected. There are no
includes, external references, executable strings, or extensible rules.

列出的全部键都是必需的，额外键会被拒绝。不支持文件包含、外部引用、可执行字符串或可扩展规则。

<a id="claim-document"></a>

## Claim document / 待核验陈述文档

```json
{
  "format": "lemqo-claim-v1",
  "logic": "ipl",
  "name": "identity",
  "premises": [],
  "goal": ["imp", "P", "P"]
}
```

`name` matches `[A-Za-z][A-Za-z0-9_.-]{0,63}` and labels the report only. Claim
formulas use prefix trees: an atom is a string, falsehood is `["false"]`, and
each binary connective is `["imp"|"and"|"or", left, right]` (the vertical bars
here describe alternatives; they are not JSON syntax). `premises` is a list
of distinct structural formulas. Its order determines receipt premise indices.

`name` 必须匹配 `[A-Za-z][A-Za-z0-9_.-]{0,63}`，仅用于报告标签。陈述公式使用前缀树：原子是字符串，假为 `["false"]`，二元联结词为 `["imp"|"and"|"or", left, right]`（此处竖线表示可选项，不是 JSON 语法）。`premises` 是结构各异的公式列表，其顺序决定回执中的前提索引。

The caller selects this file independently of the proof. Declared premises
are permissions to leave those formulas open; Lemqo never verifies their
truth, consistency, or intended informal interpretation.

调用方应独立于证明选择这份文件。声明的前提表示允许保留哪些未解除的假设；Lemqo 不验证这些前提是否为真、是否一致或是否符合预期的非形式解释。

<a id="proof-document"></a>

## Proof document / 证明文档

```json
{
  "format": "lemqo-proof-v1",
  "logic": "ipl",
  "formulas": [["atom", "P"], ["imp", 0, 0]],
  "steps": [["assume", 0], ["imp_intro", 1, 0]],
  "root": 1
}
```

Formula and step IDs are zero-based row positions, in separate namespaces.
The formula table consists of exactly these row shapes:

公式 ID 和步骤 ID 分属不同的命名空间，分别是从零开始的行号。公式表只允许下列行形式：

| Row / 行 | Meaning / 含义 |
| --- | --- |
| `["atom", name]` | Atom with the given identifier / 指定标识符的原子 |
| `["false"]` | Falsehood / 假 |
| `["imp", a, b]` | Implication of formula rows `a` and `b` / 公式行 `a` 到 `b` 的蕴含 |
| `["and", a, b]` | Conjunction of formula rows `a` and `b` / 公式行 `a` 与 `b` 的合取 |
| `["or", a, b]` | Disjunction of formula rows `a` and `b` / 公式行 `a` 与 `b` 的析取 |

At formula row `i`, child IDs must be strictly less than `i`. Duplicate
structural formulas are permitted and canonicalized using full structural
equality, so different IDs cannot create different meanings for the same
formula. Claim trees and proof DAGs share this identity relation. Intermediate
atoms not present in the claim are allowed and remain uninterpreted.

公式行 `i` 中的子公式 ID 必须严格小于 `i`。允许结构重复的公式；验证器按完整结构相等进行规范化，因此同一公式的不同 ID 不会产生不同含义。陈述树和证明 DAG 共用这一身份关系。中间步骤可以引入陈述中没有出现的原子，它们仍然没有解释。

Each proof row names a rule, an explicit conclusion formula row `f`, and zero
or more parent step IDs. At step `i`, every parent ID must be less than `i`.
Conclusion formula IDs may reference any row of the already validated formula
table. `root` selects any existing step, not necessarily the last one. All
formulas and all steps must validate, including nodes after or unrelated to
the root. Forward references, cycles, and empty tables are rejected.

每个证明行指定一条规则、明确的结论公式行 `f`，以及零个或多个父步骤 ID。在步骤 `i` 中，所有父步骤 ID 必须小于 `i`。结论公式 ID 可以引用已验证公式表中的任意一行。`root` 可以选择任意已有步骤，不要求是最后一步。所有公式和步骤均须通过验证，包括根之后或与根无关的节点。前向引用、环和空表均被拒绝。

<a id="ten-inference-rules"></a>

## Ten inference rules / 十条推理规则

Each checked step is a judgment `(C, Γ)` with conclusion `C` and a finite,
immutable set of open assumption formulas `Γ`. The certificate supplies `C`
but never supplies `Γ`. The checker computes it. In the table, `j:(C,Γ)` means
that parent step `j` has the indicated already checked judgment.

每个已检查步骤对应判断 `(C, Γ)`：`C` 是结论，`Γ` 是有限且不可变的未解除假设公式集合。证书提供 `C`，但不提供 `Γ`；后者由验证器计算。表中的 `j:(C,Γ)` 表示父步骤 `j` 已通过检查，且具有该判断。

| Row / 行 | Required shapes / 必需形状 | Computed judgment / 计算所得判断 |
| --- | --- | --- |
| `["assume", f]` | `f = A` | `(A, {A})` |
| `["imp_intro", f, j]` | `f = A → B`; `j:(B,Γ)` | `(A → B, Γ \ {A})` |
| `["imp_elim", f, j, k]` | `f = B`; `j:(A → B,Γ)`; `k:(A,Δ)` | `(B, Γ ∪ Δ)` |
| `["and_intro", f, j, k]` | `f = A ∧ B`; `j:(A,Γ)`; `k:(B,Δ)` | `(A ∧ B, Γ ∪ Δ)` |
| `["and_left", f, j]` | `f = A`; `j:(A ∧ B,Γ)` | `(A,Γ)` |
| `["and_right", f, j]` | `f = B`; `j:(A ∧ B,Γ)` | `(B,Γ)` |
| `["or_left", f, j]` | `f = A ∨ B`; `j:(A,Γ)` | `(A ∨ B,Γ)` |
| `["or_right", f, j]` | `f = A ∨ B`; `j:(B,Γ)` | `(A ∨ B,Γ)` |
| `["or_elim", f, j, k, l]` | `f = C`; `j:(A ∨ B,Γ)`; `k:(C,Δ)`; `l:(C,Θ)` | `(C, Γ ∪ (Δ \ {A}) ∪ (Θ \ {B}))` |
| `["false_elim", f, j]` | `f = C`; `j:(False,Γ)` | `(C,Γ)` |

Contexts contain formulas, not named assumption occurrences. Weakening and
contraction are admissible structural principles. Vacuous discharge and
discharging all occurrences of an identical formula are valid. Discharge
creates a new context; it cannot remove assumptions from a shared parent.
`or_elim` removes only the left disjunct from the left branch and the right
disjunct from the right branch, retaining the disjunction-producing context.
Branches need not actually use their respective branch assumption.

上下文包含公式，而不是带名称的假设出现位置。弱化和收缩是可容许的结构原则。允许解除未实际使用的假设，也允许解除同一公式的全部出现。解除假设会产生新上下文，不能修改共享父步骤的假设。`or_elim` 只从左分支移除左析取项、从右分支移除右析取项，并保留产生析取式的证明所依赖的上下文。分支不要求实际使用对应的分支假设。

At the root, conclusion tree equality with the supplied claim's goal is
required, and its computed context must be a subset of the declared premises.
An empty computed context certifies a closed derivation. Extra declared
premises may be unused. Dependencies are not promised to be mathematically
minimal. No rule can introduce a closed proof of falsehood in this calculus.

根步骤的结论树必须与所提供陈述的目标完全相等，计算出的上下文必须是声明前提的子集。空上下文表示闭合推导。允许部分声明前提未被使用，但不保证依赖集合在数学上最小。在本演算中，没有规则能导出假命题的闭合证明。

<a id="fixed-resource-policy"></a>

## Fixed resource policy / 固定资源策略

These limits apply before acceptance and can reject valid large proofs:

下列限制在验收前执行，因此可能拒绝数学上有效但规模过大的证明：

| Resource / 资源 | Limit / 上限 |
| --- | --- |
| Bytes per input file / 每份输入字节数 | 2,097,152 |
| JSON container nesting per file / 每份文件的 JSON 容器嵌套深度 | 96 |
| JSON values per file, counting object keys too / 每份文件的 JSON 值数（包含对象键） | 200,000 |
| Decoded characters per JSON string / 每个 JSON 字符串解码后的字符数 | 128 |
| Digits per JSON integer / 每个 JSON 整数的位数 | 9 |
| Certificate formula rows / 证书公式行数 | 10,000 |
| Formula depth, atom/false depth = 1 / 公式深度（原子与假为 1） | 64 |
| Formula occurrences across all claim trees / 全部陈述树中的公式出现数 | 10,000 |
| Proof steps / 证明步骤数 | 20,000 |
| Declared distinct premises / 声明的不同前提数 | 256 |
| Open formulas in any step's context / 任一步骤上下文中的开放公式数 | 256 |
| Sum of context cardinalities over all proof steps / 全部证明步骤的上下文大小总和 | 200,000 |

The shared interner can contain up to the sum of claim occurrences and proof
formula rows (20,000), not just the certificate row limit. DAG comparison
never unfolds shared subtrees. The CLI displays the bounded claim tree.
This is a bounded input/work policy, not an OS-level memory or time guarantee.

共享驻留表最多可包含陈述公式出现数与证明公式行数之和，即 20,000 项，而非仅限于证书公式行数。比较 DAG 时不会展开共享子树。命令行显示的是有界的陈述树。这是对输入与工作量的限制，不是操作系统级的内存或时间保证。

<a id="cli-and-receipt"></a>

## CLI and receipt / 命令行与验证回执

```text
python -m lemqo check PROOF --claim CLAIM [--json]
python -m lemqo --version
```

| Exit code / 退出码 | Meaning / 含义 |
| --- | --- |
| 0 | Completed verification and accepted the supplied claim/certificate pair / 验证完成且接受所提供陈述与证书 |
| 1 | Input, inference, claim-binding, or resource-policy rejection / 输入、推理、陈述绑定或资源策略拒绝 |
| 2 | Command-line usage or input-file I/O error / 命令行用法或输入文件读写错误 |
| 3 | Internal or environmental exception; verification did not complete / 内部或环境异常，验证未完成 |

On rejection, stdout is empty and stderr explains the error. With `--json`,
verification rejections emit a JSON error on stderr; usage, I/O, and internal
errors remain plain diagnostic text. Unexpected process termination and
output errors must also be treated as failure. A consumer should require
exit 0 and a complete receipt, not search logs for the word `VALID`.

拒绝时，stdout 为空，stderr 解释错误。使用 `--json` 时，验证拒绝在 stderr 输出 JSON 错误；用法、输入输出及内部错误仍输出普通诊断文本。进程意外终止和输出错误也必须视为失败。使用方应同时要求退出码为 0 且回执完整，不能只在日志中搜索 `VALID`。

A successful JSON receipt contains `status`, `verifier`, `version`, `logic`,
`claim`, `kind`, `goal`, `declared_premises`, `used_premise_indices`,
`formula_rows`, `checked_steps`, `root`, `claim_sha256`, and `proof_sha256`.
`kind` is `closed` if the retained context is empty, otherwise `conditional`.
Hashes identify exact input bytes; they are neither signatures nor proofs of
truth. All success output is constructed after checking the complete input.

成功的 JSON 回执包含 `status`、`verifier`、`version`、`logic`、`claim`、`kind`、`goal`、`declared_premises`、`used_premise_indices`、`formula_rows`、`checked_steps`、`root`、`claim_sha256` 和 `proof_sha256`。保留的上下文为空时，`kind` 为 `closed`；否则为 `conditional`。哈希标识精确的输入字节，不是签名，也不是命题为真的证明。全部成功输出均在完整输入检查结束后构造。

The public Python API is `lemqo.verify_bytes(claim_bytes, proof_bytes)`. It
returns the same receipt or raises `lemqo.Rejection`, whose `code` identifies
the rejection category. It accepts bytes only. Other unexpected exceptions
must be treated as verification failure. Kernel-internal helpers are not a
supported interface for skipping byte-level validation.

公开 Python API 为 `lemqo.verify_bytes(claim_bytes, proof_bytes)`。它返回同样的回执，或抛出 `lemqo.Rejection`，其 `code` 标识拒绝类别。接口只接受 bytes。其他意外异常必须视为验证失败。内核内部辅助函数不是用于绕过字节级验证的受支持接口。
