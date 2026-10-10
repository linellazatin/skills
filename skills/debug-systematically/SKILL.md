---
name: debug-systematically
description: Diagnose a bug, failing check, regression, integration issue, or performance problem using the actual inputs, code, and runtime. Use when the cause is uncertain or a proposed fix needs evidence.
license: MIT
---

# Diagnose the reported behavior

For a troubleshooting or fix response, lead with a short TL;DR. State observed facts separately from hypotheses and missing observations.

Use relevant existing specs or plans to recover intended behavior and prior evidence, then verify against current artifacts and user corrections. In authorized remediation, update the existing record with the supported cause, correction, checks, and gaps when artifact edits are within scope. Diagnosis-only work does not create or update planning files unless report writing is separately authorized.

## Select the mode

1. Read the requested outcome and existing authorization. Use **diagnosis-only** for investigation or assessment requests; use **diagnose-and-fix** when remediation is already authorized.
2. Record the problem, relevant evidence, allowed scope, and requested output in the existing task notes. A review handoff inherits the review's scope; discovering a defect does not authorize fixing it.
3. Keep diagnosis-only work read-only in the target checkout and persistent environment. Run appropriate non-destructive checks; use a disposable workspace for experiments that require changes. Do not alter product code, tests, docs, or settings to finish a diagnosis.
4. Follow sections 1 and 2 in either mode, then use only the matching section 3 branch and completion checklist. Do not require implementation evidence to complete a diagnosis.

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
2. Before changing the cause, run a behavior-reaching regression test and observe failure for the reported defect, not setup errors. Then apply the correction, rerun the same test, and refactor only with checks passing. If implementation already exists, preserve it and disclose the missing pre-fix observation. If the actual host is unavailable, test the reachable contract and retain a repeatable live procedure with the host result marked pending; do not substitute mock success for host evidence.
3. Apply one coherent correction at its owning boundary. Do not add unrelated refactors, broaden the product's role, or change a test expectation merely to match faulty behavior.
4. Rerun the regression and original scenario. If either still fails, return to the explanation with the new evidence; do not stack an unverified workaround onto the patch.
5. Run required checks for affected callers. Compare current installed/generated copies where the original problem involved loading or packaging.
6. Remove only investigation artifacts you introduced and no longer need. Update affected operational docs and changelog before reporting the fix ready.

Diagnose-and-fix completion:

- [ ] The explanation accounts for the actual reported failure, with evidence at the relevant layer.
- [ ] The correction is within authorization and targets that cause.
- [ ] The regression check and original scenario establish the intended result.
- [ ] Affected consumers and required documentation are checked.
- [ ] Unavailable runtime checks or intermittent limits are explicit.

Return `TL;DR`, then the mode, cause or bounded uncertainty, proposed or applied correction, checks actually performed, planned checks, and remaining gaps. If only a workaround was established, state its operating conditions and what remains unresolved. Never turn a direct runner pass into a claim about an unobserved loaded host. A completed diagnosis report can still contain an unresolved cause or an unfixed defect; say so explicitly.
