# Independent checking of Lean exports

Lemqo v0.2 adds a separate verification path for selected Lean 4 certificates.
The small IPL calculus and `lemqo check` remain available. The Lean path uses
existing implementations rather than adding dependent types to the IPL kernel.
Its trusted boundary is substantially larger than the IPL path.

## Acceptance contract

```sh
python -m lemqo check-lean solution.ndjson \
  --claim claim.json --reference reference.ndjson \
  --backends /tmp/lemqo-backends/backends.json --json
```

The caller selects the claim, reference, and trusted backend configuration
independently of the submitted proof. A proof cannot choose any of them.
Verification accepts only when all of the following complete:

1. Copy both exports into a private temporary directory, then strictly preflight
   the exact copied bytes. No supplied Lean source or `.olean` is executed.
2. Authenticate the reference's byte length and SHA256 against the claim.
3. Use the offline Comparator bridge to match the target theorem types, their
   recursively referenced definitions, permitted axiom types, and fixed
   kernel-sensitive primitives. No definition holes are permitted.
4. Require Nanoda to check **every** declaration in the same solution snapshot,
   including all exported proof dependencies. Require its complete, clean
   success message with the exact preflight declaration count.

Missing targets, an axiom or definition presented as the target theorem,
unapproved axioms, unsafe/partial declarations, mismatches, crashes, timeouts,
and incomplete backend output are rejection. A statement match is insufficient.
The bridge deliberately does not call the Lean proof kernel to accept proofs.

The receipt identifies the claim, reference, solution, backend configuration,
and native binaries by hashes. These hashes identify bytes; they do not prove
logical soundness or authenticate the origin of an arbitrary binary.

## Logic and axioms

This path checks Lean's dependent type theory as implemented by the pinned
Nanoda version, including universes, inductives, recursion, quotient support,
and enabled natural/string literal extensions. It does not translate a Lean
theorem into a propositional approximation. The supported export subset and
backend limits can reject valid Lean proofs; broad compatibility is not claimed.

Claims may permit any subset of `propext`, `Classical.choice`, and `Quot.sound`.
The producer exports every permitted axiom, even if unused, and the bridge
compares its **type** with the reference. Familiar names alone are insufficient.
The receipt lists permitted axioms, not a minimal set of axioms actually used.
Reference theorem bodies may use `sorryAx`; they are specification holes, never
accepted proof evidence. `sorryAx` is always forbidden in the solution.

## Claim format

Exactly these fields are required, with no extra keys:

```json
{
  "format": "lemqo-lean-claim-v1",
  "name": "chosen-main-result",
  "theorem_names": ["SelectedNamespace.main_theorem"],
  "permitted_axioms": ["propext", "Classical.choice", "Quot.sound"],
  "reference": {
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "bytes": 1
  },
  "lean_version": "4.34.1",
  "lean_githash": "5045d0056413266e57c625dcd7c365b10e377c52",
  "export_format": "3.1.0"
}
```

The zero digest is a schema example, not a runnable reference. Target arrays
contain 1–32 distinct ASCII names with identifier namespace components; axiom
arrays may be empty. Names of declarations internal to the export may include
Unicode and numeric components. The trusted reference must actually contain
each selected theorem and every permitted axiom.

## Strict export subset and limits

Inputs are uncompressed UTF-8 NDJSON with exactly one metadata record first.
Metadata must identify `lean4export` 3.1.0, format 3.1.0, and the exact Lean
release above. Each subsequent record has exactly one supported tag; all fields,
scalar types, and existing DAG back-references are checked. Unknown fields,
duplicate object keys, floats, negative numbers, nonfinite numbers, malformed
Unicode, blank records, trailing data, repeated metadata, and `mdata` are rejected.
Name/universe/expression indices must be dense; anonymous name and universe
zero are implicit. Declaration forward dependencies are handled by the native
parsers/checker, including mutual inductives, rather than treated as proof steps.

Fixed bounds are 4 GiB per export, 4 MiB per record, 50 million records,
16 nested JSON containers, one million names, and 64 MiB cumulative rendered
name characters. Names are at most 4096 characters; natural literal strings
are canonical decimal with at most 100,000 digits. Other numeric fields follow
the supported backend's unsigned ranges. These are acceptance restrictions,
not additional logical rules.

The default total deadline is 1800 seconds (`--timeout 1` through `7200`).
Each backend's stdout and stderr are limited to 64 KiB. Linux execution also
limits address space to 10 GiB, CPU time to the remaining deadline, file writes
to zero bytes, and disables core dumps. Failed POSIX process groups are killed.
The tested native platform is Linux, including WSL; other platforms do not
receive the Linux resource limits. These measures bound common failures; they
are not an operating-system sandbox or a guarantee against kernel defects.

## Build and reproduce

Use Linux/WSL with Python 3.11+, Git, Lean **4.34.1** and Rust **1.94.0** on PATH.
Install Lean through its normal [toolchain instructions](https://github.com/leanprover/lean4#building-from-source)
or the [pinned release](https://github.com/leanprover/lean4/releases/tag/v4.34.1).
Then build the native programs from this checkout:

```sh
python tools/build_lean_backends.py --work /tmp/lemqo-backends
python /tmp/lemqo-backends/bridge/tests/run_offline.py \
  --nanoda /tmp/lemqo-backends/nanoda/target/release/nanoda_bin --lemqo-root .
```

The build tool checks the toolchain, locked Git revisions, clean source files,
and binary SHA256. It writes `backends.json` and `build-information.json`.
The second command generates trusted fixtures and exercises the actual
native programs, including a correct proof and a corrupted proof whose statement
still matches. It has no backend-skip mode.

Producer builds may execute pinned upstream Lean metaprograms. They belong to
the trusted preparation stage, not the offline checker. The OpenAI producer
uses only this repository's hash-checked [source snapshot](openai.md), a minimal
Lake project, and pinned Mathlib. Mathlib's build cache is a preparation-stage
trust input; use `--no-cache` in a fresh work directory for a full source build. Offline
verification neither fetches a cache nor runs Lake.

Pinned dependencies:

| Component | Source revision | Role |
| --- | --- | --- |
| [Nanoda 0.4.19](https://github.com/ammkrn/nanoda_lib/tree/0f88b5f382f0f3f08aed4af0dd6c0e48c3fd7a44) | `0f88b5f382f0f3f08aed4af0dd6c0e48c3fd7a44` | Independent Rust proof checking |
| [Comparator](https://github.com/leanprover/comparator/tree/d03acab154d269c06e60e4de7e4cc85deebff94b) | `d03acab154d269c06e60e4de7e4cc85deebff94b` | Statement/definition/axiom binding |
| [lean4export](https://github.com/leanprover/lean4export/tree/076e8e57707e813375e8f9da8bf989799ace9680) | `076e8e57707e813375e8f9da8bf989799ace9680` | Dependency-complete certificate production and format parsing |
| [Mathlib](https://github.com/leanprover-community/mathlib4/tree/d13f23b723b8a846827a245b89c10fc7d3f11612) | `d13f23b723b8a846827a245b89c10fc7d3f11612` | Selected mathematical definitions and proofs |

The exporter/Comparator revisions target Lean 4.34.0 upstream; Lemqo builds
and tests them on 4.34.1. All are Apache-2.0. Native binary builds are pinned
and identifiable, but are not claimed byte reproducible across build hosts.
Lemqo's Python/source archives retain their deterministic packaging contract.

## Trust and statement fidelity

Mathematical validity depends on the calculus and allowed axioms. Statement
fidelity depends on the independently reviewed reference and its definitions.
Implementation correctness depends on Lemqo's parser/orchestration, the
Comparator/Export parser and binding code, Nanoda, their compilers/runtimes,
and the OS/hardware. The Lean compiler/runtime is trusted to execute the
binding program; its proof kernel is not the independent proof-checking step.

A valid receipt does not establish that a reference expresses a paper's prose,
that a claim is novel, or that the checking implementations have no defects.
Independent rebuilding, source review, mutation tests, and implementation
diversity provide audit evidence, not an end-to-end formal correctness proof.
