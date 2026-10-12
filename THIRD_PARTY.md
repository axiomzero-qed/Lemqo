# Third-party sources and dependencies

The root MIT license covers Lemqo's original Python implementation and tools.
It does not replace the licenses of retained upstream code or proof sources.

- `corpus/openai/` contains unmodified selected sources from
  [openai/math](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb),
  under Apache-2.0. Its full license is retained at
  [corpus/openai/LICENSE](corpus/openai/LICENSE); original source notices remain.
- `bridge/lean/Main.lean` adapts Comparator's primitive target list and invocation
  pattern, copyright 2025 Lean FRO, LLC, author Henrik Böving. This bridge is
  Apache-2.0, with attribution in the source and the full license at
  [bridge/lean/LICENSE](bridge/lean/LICENSE).
- Comparator, lean4export, Nanoda and Mathlib are pinned Apache-2.0 dependencies
  fetched by build tools, rather than included as native binaries. Their source
  links, revisions and roles are listed in [docs/lean.md](docs/lean.md).

Generated mathematical certificates contain terms derived from these upstream
proofs. Preserve the applicable source attributions and Apache-2.0 license when
redistributing them. Compiler/runtime licenses also apply to redistributed
native binaries; Lemqo's source archives do not bundle those binaries.
