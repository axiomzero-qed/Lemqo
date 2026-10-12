# Security and logical correctness

Lemqo v0.1 is experimental. Please report accepted invalid derivations,
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

The [trust document](docs/trust.md) defines the input threat model and its
limits. Treat any nonzero exit, exception, interrupted execution or incomplete
receipt as failure. Only a completed check against a reviewed target provides
the stated assurance.
