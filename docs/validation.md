# v0.1 local validation record

Recorded on 2026-10-12 for the initial 0.1.0 release candidate.

| Check | Result |
| --- | --- |
| Environment | Windows; CPython 3.12.10 |
| Full standard-library test suite | 49 tests passed |
| Example corpus | Seven valid proofs accepted; two invalid certificates rejected |
| Independent finite Kripke oracle | 6,000 deterministic candidates, all ten rules; 3,706 accepted and 2,294 rejected |
| Semantic observations | Each accepted result's retained context checked on 145 finite world/valuation observations |
| Archive reproducibility | Two builds compared byte for byte, including checksum files |
| ZIP application | Valid and invalid examples executed outside the checkout in Python isolated mode |
| Extracted source | Quickstart executed outside the original checkout |
| Optional pip installation | Built and installed into a fresh virtual environment; installed CLI accepted/rejected the expected examples outside the checkout |
| Release checks | Required files, local Markdown links, versions and standard-library runtime imports passed |

A separate GPT-6 Astra reviewer scrutinized the checking modules and performed
targeted adversarial checks. A GPT-6 Luna reviewer checked research and
documentation consistency. No concrete logic or claim-binding defect was found
in these reviews. This was AI-assisted development and review, not a completed
independent human audit or a formal proof of implementation correctness.

The rule checker is 200 lines including comments and blank lines; the complete
`lemqo/` Python checking path is 425 lines. These counts help locate the code
to inspect; they are not a measurement of total trusted base, which also
includes Python and its relevant standard library.

Reproduce the checks with `python tools/check_release.py`. The finite-model
corpus is bounded testing evidence and does not establish correctness for all
inputs. The mathematical soundness argument is in [trust.md](trust.md).
Remote validation is recorded separately in the public repository's
[GitHub Actions](https://github.com/axiomzero-qed/Lemqo/actions), with each run tied to
its commit. This table records local checks; it is not a claim that all future
remote runs pass. No PyPI publication has been performed.
