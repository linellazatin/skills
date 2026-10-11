---
name: debug-systematically
description: Diagnose a bug, failing check, regression, integration issue, or performance problem when the cause is uncertain or a proposed explanation needs evidence. Use actual inputs, code, and runtime observations. An established correction needing implementation belongs to development; diagnosis can support an active approved plan without replacing it.
license: MIT
---

# Diagnose the reported behavior

For a troubleshooting or fix response, lead with a short TL;DR. State observed facts separately from hypotheses and missing observations.

## Entry route

- **Inputs:** reported operation, expected/actual behavior, relevant artifacts, and diagnosis-only or remediation authorization.
- **First action:** establish the mode, capture the actual failure, and identify the boundary the reproduction must reach.
- **Stop condition:** diagnosis ends with a supported cause or bounded uncertainty and next observation. A fix needs regression, original-scenario, and affected-consumer evidence; missing host checks remain pending.

### Route card

Choose the evidence/scope route; linked examples are optional.

| Condition | Next action and minimum evidence | Stop or handoff |
| --- | --- | --- |
| [Cause uncertain](references/worked-examples.md#reload-registration-boundary) | Establish diagnosis-only or authorized-fix mode; capture actual/expected behavior and probe one falsifiable explanation at its boundary. | Supported cause or bounded uncertainty; no patch in diagnosis-only mode. |
| [Prediction contradicted or runtime unavailable](references/worked-examples.md#contradicted-timeout-explanation) | Reject unsupported hypotheses; name the next distinguishing observation and what is missing. | Stop speculative retries; do not invent a cause or runtime result. |
| [Cause already established](references/worked-examples.md#established-byte-counting-cause) | Verify evidence still applies; carry it into regression-first correction only when remediation is authorized. | Diagnosis proposal if read-only; otherwise fix with original/consumer checks. |

Use relevant existing specs or plans to recover intended behavior and prior evidence, then verify against current artifacts and user corrections. In authorized remediation, update the existing record with the supported cause, correction, checks, and gaps when artifact edits are within scope. Diagnosis-only work does not create or update planning files unless report writing is separately authorized.

## Select the mode

1. Read the requested outcome and existing authorization. Use **diagnosis-only** for investigation or assessment requests; use **diagnose-and-fix** when remediation is already authorized.
2. Record the problem, relevant evidence, allowed scope, and requested output in the existing task notes. A review handoff inherits the review's scope; discovering a defect does not authorize fixing it.
3. Keep diagnosis-only work read-only in the target checkout and persistent environment. Run appropriate non-destructive checks; use a disposable workspace for experiments that require changes. Do not alter product code, tests, docs, or settings to finish a diagnosis.
4. Follow sections 1 and 2 while a cause needs investigation, then the matching section 3 branch. If existing evidence already establishes the cause, verify that it still applies and enter the authorized fix branch directly. Diagnosis completion never requires an implementation.

## 1. Capture the failure

1. Record the attempted operation, expected result, actual result, and exact error or measurement.
2. Read the relevant call path, configuration, recent changes, and installed artifact. Identify which layer could own the failure: application, shared core, adapter, extension, host, or environment.
3. Construct the smallest check that still reaches the reported behavior. Reuse the actual invocation or payload shape; do not simplify away the failing boundary.
4. Run it before editing and retain the outcome. For intermittent failures, record conditions and attempts; for performance, hold workload and runtime settings comparable.
5. If the actual runtime is unavailable, record available source or historical evidence and the missing observation. Continue investigation, but label any reproduction elsewhere as narrower evidence.

## 2. Test an explanation

1. Follow the failing input through the owner and its consumers. Identify the first observed result that differs from the expected contract.
2. Compare a working case where available. Inspect differences in input, configuration, lifecycle, installed version, and environment that could explain the divergence.
3. Write a falsifiable explanation: `<condition> causes <wrong behavior> at <location>; <probe> should show <result> if this is correct`.
4. Run the probe with one meaningful variable changed. Prefer inspection or an isolated experiment before changing persistent settings.
5. If the prediction fails, discard or revise the explanation using the new evidence. Remove your failed experimental change before trying another; preserve the user's work.
6. If repeated attempts add no distinguishing evidence, stop speculative experiments. Summarize ruled-out explanations and seek the missing observation, reference, or material user decision. Do not claim a cause merely to close the investigation.

Record each meaningful probe in the existing task notes:

```text
Symptom: <operation; expected; observed>
Explanation: <condition and causal location>
Probe: <input/change and predicted result>
Observed: <actual output or measurement>
Decision: <supported, rejected, or still uncertain; next observation>
```

## 3. Finish the selected mode

### Diagnosis-only

1. State the supported explanation and causal location, or explicitly bound the uncertainty if the cause remains unresolved.
2. Distinguish reproduced behavior, source-supported conclusions, rejected explanations, and missing observations. An unavailable runtime leaves its behavior unverified.
3. Describe the proposed correction only as a proposal. Identify affected consumers and the regression, original-scenario, and runtime checks that would verify it; label them planned rather than executed.
4. Return the diagnosis to the requesting assessment with its evidence and limits. End without a patch; move into remediation only when authorized by the user, carrying the established evidence forward.

Diagnosis-only completion:

- [ ] The symptom, expected behavior, and relevant layer are characterized.
- [ ] The explanation is supported, or the uncertainty and next distinguishing observation are explicitly bounded.
- [ ] Proposed corrections and future checks are distinct from work performed.
- [ ] The target checkout and persistent settings remain unchanged.
- [ ] The report states whether the cause is established or unresolved; it makes no post-fix or product-readiness claim.

### Diagnose-and-fix

1. Check whether the request authorizes remediation. If assessment-only, report the diagnosis and proposed correction without editing.
2. Select the test route: a new fix needs a behavior-reaching regression failure, not a setup error. Existing implementation must be preserved, with any missing pre-fix observation disclosed. An inaccessible host needs reachable-contract tests and a repeatable live procedure; keep its result pending.
3. Apply one coherent correction at its owning boundary, rerun the regression, and refactor only with checks passing. Do not add unrelated refactors, broaden the product's role, or change an expectation merely to match faulty behavior.
4. Rerun the regression and original scenario. If either still fails, return to the explanation with the new evidence; do not stack an unverified workaround onto the patch.
5. Run required checks for affected callers. Compare current installed/generated copies where the original problem involved loading or packaging.
6. Remove only investigation artifacts you introduced and no longer need. Update affected operational docs and changelog before reporting the fix ready.

Diagnose-and-fix completion:

- [ ] The explanation accounts for the actual reported failure, with evidence at the relevant layer.
- [ ] The correction is within authorization and targets that cause.
- [ ] The regression check and original scenario establish the intended result.
- [ ] Affected consumers and required documentation are checked.
- [ ] Unavailable runtime checks or intermittent limits are explicit.

Return `TL;DR`, mode, cause or bounded uncertainty, proposed/applied correction, executed checks, planned checks, and gaps. A workaround needs its operating conditions and unresolved cause stated. Diagnosis completion can leave a cause unresolved or a defect unfixed; a direct runner pass never establishes an unobserved host result.
