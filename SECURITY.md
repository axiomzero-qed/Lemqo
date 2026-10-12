# Security and logical correctness

Lemqo is experimental. Please report accepted invalid derivations,
claim-binding errors, malformed-input acceptance, resource-limit bypasses,
and release-integrity problems with the smallest reproducing input.

Use the repository's **Security → Report a vulnerability** option if maintainers
have enabled private reporting. If no
private channel is available, open an issue asking maintainers for a private
contact without posting sensitive material. Maintainers must configure a
working private reporting channel before inviting vulnerability submissions.
There is no invented email address or currently claimed response-time guarantee.

Include the verifier version, Python/OS versions, exact claim and proof bytes
or their safely shareable reproducer, command, exit status, and observed vs.
expected result. Distinguish a valid derivation of an unintended statement from
a checker defect; both may matter, but only the latter violates verification.

For the optional Lean path, include target theorem names, export metadata,
the separately selected reference/claim, backend binary hashes and source pins.
Do not execute unknown Lean sources or backend configurations to reproduce an
untrusted certificate. The offline verifier accepts data exports; native
programs and specification inputs must be independently trusted by the caller.

The [trust document](docs/trust.md) defines the input threat model and its
limits. Treat any nonzero exit, exception, interrupted execution or incomplete
receipt as failure. Only a completed check against a reviewed target provides
the stated assurance.
