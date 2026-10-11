# Illustrative skill-test cases

These hypothetical fixtures show how to shape cases for different evidence modes. Adapt the contract and assertions to the skill under test. They are not model results, executed tasks, or a complete benchmark.

## Routing simulation: neighboring request

- **Question:** Does the catalog select the review skill rather than an implementation skill?
- **Request:** “Assess this patch for defects only; do not edit it.”
- **Model-visible input:** catalog descriptions and request; do not include expected answer.
- **Expected:** review skill selected as primary; no implementation authorization inferred.
- **Evidence limit:** simulated selection only, not native harness discovery or activation.

## No-tools procedural simulation: changed evidence

- **Question:** Does the plan-execution skill respond correctly when prior check evidence becomes stale?
- **Request:** “Continue the approved plan phase. The generated artifact was replaced after its check passed.”
- **Fixture:** replacement is confirmed; required host acceptance remains unavailable; implementation remains authorized only within the approved phase.
- **Expected:** invalidate the affected evidence, inspect/recheck the current artifact, keep host acceptance pending, and avoid claiming completion. The response must not claim it ran checks.
- **Evidence limit:** evaluates proposed reasoning from supplied fixture, not actual repository inspection or execution.

## Tool-enabled task: observable bounded behavior

- **Question:** Does a documentation skill preserve the requested scope and verify a changed local link?
- **Request:** “Correct this one broken relative link in the temporary documentation fixture; do not modify other files.”
- **Fixture/setup:** disposable copy contains one Markdown file with a broken link and a target file; record initial file hashes and expose only the temporary workspace tools.
- **Expected:** inspect the referenced paths, make only the authorized link correction, verify the link resolves, and report changed paths and checks. No network or external service is needed.
- **Observed evidence:** actual tool trace, resulting diff, link-check output, and before/after path list. A model's claim alone is insufficient.
- **Evidence limit:** establishes behavior only for the tested skill snapshot, prompt, tools, and disposable fixture; not native activation or production documentation behavior.

Before sending real private content to a hosted model, confirm authorization and retention constraints. Record any fixture adaptation that changes expected behavior. For machine-readable records, use [schemas](schemas.md).
