<a id="examples"></a>

# Examples / 示例

Every proof is checked against its matching `NAME.claim.json`. All files use
the fixed format described in the [specification](../docs/specification.md).
Run commands from the repository root:

每份证明都针对与之对应的 `NAME.claim.json` 核验。所有文件均采用[规范](../docs/specification.md)所述的固定格式。请从仓库根目录运行以下命令：

```sh
python -m lemqo check examples/identity.proof.json --claim examples/identity.claim.json
```

| Name / 名称 | Formal result / 形式化结果 | Outcome / 结果 |
| --- | --- | --- |
| identity | `P → P` | Closed proof / 闭合证明 |
| composition | `(P → Q) → ((Q → R) → (P → R))` | Closed proof / 闭合证明 |
| conjunction | `(P ∧ Q) → (Q ∧ P)` | Closed proof / 闭合证明 |
| disjunction | `(P ∨ Q) → (Q ∨ P)` | Closed proof / 闭合证明 |
| distributivity | `(P ∧ (Q ∨ R)) → ((P ∧ Q) ∨ (P ∧ R))` | Closed proof / 闭合证明 |
| modus_ponens | `P → Q, P ⊢ Q` | Conditional on both premises / 以两个前提为条件 |
| ex_falso | `⊥ → P` | Closed proof; it does not prove `⊥` / 闭合证明；这并未证明 `⊥` |
| identity.invalid | A forged implication elimination targeting `P → P` / 伪造的蕴含消去，目标为 `P → P` | Rejected inference / 推理被拒绝 |
| false.invalid | An open assumption submitted as a closed proof of `⊥` / 将开放假设作为 `⊥` 的闭合证明提交 | Rejected undeclared assumption / 未声明假设被拒绝 |

In the identity certificate, formula row 0 denotes `P`, and row 1 denotes
`P → P`. Step 0 assumes `P`. Step 1 applies implication introduction and
discharges that assumption. The final open context is empty.

在 identity 证书中，公式行 0 表示 `P`，公式行 1 表示 `P → P`。步骤 0 假设 `P`；步骤 1 应用蕴含引入并解除该假设。最终开放上下文为空。

The disjunction example first assumes `P ∨ Q`. In its left branch, an assumed
`P` gives `Q ∨ P`; in its right branch, an assumed `Q` gives the same result.
`or_elim` removes the respective branch assumptions but retains `P ∨ Q`.
Implication introduction then discharges the remaining assumption.

析取示例先假设 `P ∨ Q`。在左分支中，假设 `P` 可推出 `Q ∨ P`；在右分支中，假设 `Q` 也可推出同一结果。`or_elim` 解除各分支假设，但保留 `P ∨ Q`。随后蕴含引入会解除剩余假设。

The `modus_ponens` receipt lists used premise indices `[0, 1]`. This reports
dependencies of this derivation and does not establish either premise's truth.

`modus_ponens` 回执列出已使用的前提索引 `[0, 1]`。这表示该推导依赖哪些前提，并不能证明任一前提为真。
