# Offline statement binding

`lemqo_compare config.json` reads a trusted reference NDJSON export and an
untrusted solution NDJSON export. It does not execute supplied Lean source,
import supplied `.olean` files, run Lake, or invoke the Lean proof kernel.
Success means statement binding only. Lemqo must additionally obtain success
from its pinned independent Nanoda proof checker before reporting a valid proof.

Build this directory with Lean 4.34.1 using `lake build lemqo_compare`.
The executable is `.lake/build/bin/lemqo_compare`. Lake dependencies are pinned
in `lakefile.toml`; retain the resulting `lake-manifest.json` for reproducibility.
The selected Comparator and exporter sources target Lean 4.34.0 upstream;
they were successfully compiled with this project's 4.34.1 toolchain on
2026-10-12. The generated manifest records both exact dependency commits.

The generated configuration has exactly these required fields:

```json
{
  "reference_file": "/absolute/path/reference.ndjson",
  "solution_file": "/absolute/path/solution.ndjson",
  "theorem_names": ["OAI.SelectedNamespace.main_theorem"],
  "permitted_axioms": ["propext", "Classical.choice", "Quot.sound"]
}
```

The Python caller supplies this configuration from its separately selected,
authenticated claim manifest. It must strictly validate the JSON and NDJSON
before invocation, including duplicate JSON keys and resource limits; the
upstream export parser is not a strict JSON-schema validator. This executable
additionally validates the format/exporter version and exact Lean toolchain
metadata before parsing declarations. It rejects unknown configuration fields, empty or
duplicate target names, non-theorem targets, unsafe/partial declarations, and
all unapproved solution axioms. The axiom list may be any subset of the three
shown. No definition holes or additional axioms are supported.

The trusted producer must export the selected theorem roots, **every** listed
permitted axiom (even when unused by the theorem), all `primitiveTargets` from
`Main.lean`, and the quotient declarations when `Quot.sound` is allowed, in
both reference and solution. Exporter recursively includes their full
dependencies. Do not use `--ignore-missing`, trim dependency declarations, or
replace them with axioms. Reference theorem bodies can be admitted proofs;
solution theorem bodies must be complete and are independently checked.

Comparator compares theorem statements, the permitted axiom types and their
dependencies, all definitions used by statements, and the special primitive
declarations. It also audits the target proofs' transitive axiom dependencies.
It allows no definition holes. The reference and its source-to-export process
are trusted mathematical specification inputs, selected independently of the
submitted solution. Matching a reference does not establish that its formal
statement accurately expresses a paper's prose; that correspondence must be
reviewed and recorded by the producer.

On success the only stdout line is deterministic JSON with `status` equal to
`matched` and the original ordered `theorem_names` array. Errors go to stderr
with nonzero exit status. The Python caller must check both the exit code and
the exact returned target list, and separately run Nanoda over the same
immutable solution bytes. A match alone is never a verified proof.

Trust includes the binding program, Comparator, the exporter-format parser,
Lean runtime/compiler, the trusted reference selection, and the operating
system. Proof checking additionally trusts the separately implemented Nanoda
kernel and Rust toolchain. This is implementation diversity, not a claim of
a formally verified end-to-end checker.

## Actual-tool regression tests

With the pinned Lean tools on `PATH`, after building the bridge, exporter and
Nanoda, run from this directory:

```sh
lake build lemqo_compare lean4export
python3 tests/run_offline.py --nanoda /absolute/path/nanoda_bin
```

When running a copied bridge outside this checkout, also supply
`--lemqo-root /absolute/path/to/lemqo-checkout`. The script refuses Python
`-O`/`-OO` mode, which would otherwise disable its regression assertions.

The test script compiles the trusted `tests/Fixture.lean`, exports its complete
dependency closure and required primitive roots, and constructs hostile
exports. It tests substituted theorem types, modified relevant definitions,
forged allowed axiom types, modified kernel primitives, non-theorem roots,
missing declarations, unsafe/partial definitions, unsupported metadata,
unapproved axioms and invalid configurations. All artifacts and machine-readable
results stay under `.lake/bridge-regressions/`.

The crucial paired test replaces only the theorem's proof: binding must accept
the unchanged statement, while Nanoda must reject the invalid proof. The
uncorrupted fixture must pass both tools. The script requires a real Nanoda
binary and fails if either positive or negative result is unexpected.
The final five tests invoke `lemqo.lean.verify_lean_files`: one acceptance of
the 585-declaration fixture, plus rejection of the corrupted proof, changed
statement, changed relevant definition, and forged axiom type. The script
writes `claim.json`, `backends.json` with actual binary hashes, and `receipt.json`
alongside the exports. On 2026-10-12 all **30 cases** (25 native tool cases and
5 full Python API cases) passed with the pinned tools on Ubuntu 24.04/WSL.
Nanoda is configured with `print_axioms: false` solely to suppress its optional
axiom pretty printer; all declarations and permitted axiom types are still
checked. Without this explicit setting, the pinned version defaults to printing
axioms but has no print destination, producing a pretty-printer error after
successful proof checking. The caller requires the clean, exact success line.

## Attribution

- [Comparator](https://github.com/leanprover/comparator/tree/d03acab154d269c06e60e4de7e4cc85deebff94b), Apache-2.0.
- [lean4export](https://github.com/leanprover/lean4export/tree/076e8e57707e813375e8f9da8bf989799ace9680), Apache-2.0; NDJSON format 3.1.0.
- [Nanoda 0.4.19](https://github.com/ammkrn/nanoda_lib/tree/0f88b5f382f0f3f08aed4af0dd6c0e48c3fd7a44), Apache-2.0; invoked separately.

The primitive list and Comparator invocation pattern in `Main.lean` adapt
Henrik Böving's upstream `Main.lean`, copyright 2025 Lean FRO, LLC.
