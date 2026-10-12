# OpenAI math formalizations in Lemqo

Three selected main theorem targets from the pinned OpenAI math corpus passed Lemqo's offline statement binding and independent Rust Nanoda checks. The source snapshot, exact target scope, and verification evidence are retained for reproduction and review.

## Upstream snapshot

The snapshot is pinned to [openai/math](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb), commit fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb. Upstream source is under [corpus/openai/lean/](../corpus/openai/lean/); its Apache-2.0 license is retained at [corpus/openai/LICENSE](../corpus/openai/LICENSE). [catalog.json](../corpus/openai/catalog.json) lists theorem declarations, comparator challenge and solution modules, paper and scope links, pinned project metadata, and deduplicated Lean source paths with byte sizes and SHA256 hashes.

The [October 2026 release announcement](https://openai.com/index/sharing-ai-progress-in-mathematics/) described 722 manuscripts. By this pinned repository snapshot, the collection had been revised to 719; only a subset has Lean formalizations. The upstream [revision history](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/history.md) records those changes. This snapshot includes three catalogue-listed main results. Supporting lemmas are not counted as additional results here.

## Main results included

- **Erdős–Gallai cycle decomposition:** There is a universal constant $C > 0$ such that every finite simple graph on $n$ vertices has an edge-disjoint decomposition into cycles and single edges using at most $Cn$ pieces. The formalized statement includes edgeless and small graphs; it does not determine the optimal constant. [Paper](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/A-linear-cycle-and-edge-decomposition-of-every-graph-September-24-2026/main.pdf) · [scope note](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/181.md).
- **Seymour’s second-neighborhood conjecture:** Every nonempty finite oriented graph has a vertex whose number of out-neighbors at directed distance exactly two is at least its outdegree. The second neighborhood excludes the starting vertex and first out-neighbors; sinks are included. [Paper](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/A-proof-of-Seymours-second-neighborhood-conjecture-September-23-2026/paper.pdf) · [scope note](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/173.md).
- **A nine-dimensional counterexample to Borsuk’s assertion:** The comparator target proves that the compact set of rank-one orthogonal projectors onto lines in $\mathbb{R}^4$ lies in the trace-one symmetric matrix space, has diameter $\sqrt{2}$, and cannot be covered by ten arbitrary subsets of strictly smaller diameter. The solution module derives an isometric image in $\mathbb{R}^9$ giving the nine-dimensional Euclidean counterexample; that corollary is not among this comparator’s named theorem targets. [Paper](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/A-nine-dimensional-counterexample-to-Borsuks-covering-assertion-September-23-2026/paper.pdf) · [scope note](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/156.md).

## Verification status

Recorded on 2026-10-13 using Ubuntu 24.04 under WSL, Python 3.12.3, Lean 4.34.1, Rust 1.94.0 and the pinned Nanoda 0.4.19 source. All source modules built without modifying the vendored proofs. The solution exports contain complete transitive proof dependencies; no missing declarations were replaced by axioms or omitted from checking.

| Selected target | Nanoda declarations | Reference bytes | Solution bytes | Result |
| --- | ---: | ---: | ---: | --- |
| Seymour second neighborhood | 22,252 | 6,425,597 | 120,954,904 | Matched; independently checked |
| Erdős–Gallai cycle decomposition | 41,966 | 21,712,669 | 268,967,194 | Matched; independently checked |
| Borsuk projector main theorem | 70,651 | 77,807,309 | 523,141,577 | Matched; independently checked |

The [machine-readable summary](../corpus/openai/verification/summary.json) links these counts to full SHA256 identities. Per-result folders in [verification/](../corpus/openai/verification/) retain the claim, exact receipt and production provenance. The [build information](../corpus/openai/verification/build-information.json) identifies compilers and actual native binaries. The [archived catalog input](../corpus/openai/verification/catalog-input.json) preserves the exact UTF-8 catalog used during production, before its status fields were updated; hash its `utf8_text` encoded as UTF-8 to reproduce the provenance digest. Current source and check status are in [catalog.json](../corpus/openai/catalog.json).

These are successful checks of the explicitly selected formal statements under `propext`, `Classical.choice` and `Quot.sound`, subject to the implementation assumptions in [lean.md](lean.md). They are not an independent human audit of the prose-to-formalization correspondence or a claim that the whole corpus has been checked. The Borsuk target is the projector statement described above; its separate Euclidean corollary is outside the named target list.

## Reproduce

Follow [the native backend build](lean.md), then run:

```sh
python tools/openai_certificates.py --work /tmp/lemqo-openai --out /tmp/lemqo-certificates --backends /tmp/lemqo-backends/backends.json
```

Omit `--only` to check all three, or select one of `seymour_second_neighborhood`, `cycle_decomposition`, `borsuk_nine`. The build instantiates a minimal pinned Mathlib project instead of the full upstream project's unrelated research dependencies. The initial Mathlib cache download is substantial; `--no-cache` in a fresh workspace builds from source. No untrusted `.lean` source service or sandbox is provided.

The output for each result includes `reference.ndjson`, `solution.ndjson`, `claim.json`, `provenance.json`, and a receipt only on acceptance. Full data exports are kept outside Git because their combined size approaches one gigabyte. Verification of existing exports needs only the prepared native programs and Python, without Lake, Mathlib cache access or network:

```sh
python -m lemqo check-lean /tmp/lemqo-certificates/seymour_second_neighborhood/solution.ndjson --claim /tmp/lemqo-certificates/seymour_second_neighborhood/claim.json --reference /tmp/lemqo-certificates/seymour_second_neighborhood/reference.ndjson --backends /tmp/lemqo-backends/backends.json --json
```
