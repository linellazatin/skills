---
name: review-code
description: Review code, working-tree changes, extensions, or documentation against requirements and report prioritized, actionable findings. Also use to evaluate review feedback before applying it. Assessment-only requests stay read-only; completion or release-readiness claims require verification across the requested requirements.
license: MIT
---

# Assess the current work

Use this as the primary workflow for defect assessment or review feedback. A request to establish completion or release readiness belongs to requirement-by-requirement verification; review findings support that decision but do not certify readiness. Perform either task inline if companion guidance is unavailable.

Produce findings tied to actual behavior and scope. Do not change files in an assessment-only review.

Read relevant existing specs and plans as requirements and progress records, checking them against current code and newer user corrections. Update their findings, decisions, or verification gaps only when artifact edits are authorized. Do not create a spec or plan for every review; assessment-only and no-file requests remain inline unless report writing is separately requested. Ignored working artifacts need explicit inspection because Git diffs omit them.

## 1. Define the review surface

1. Read the request, requirements, project instructions, and any supplied patch or review comments. Record whether the scope is assessment-only or includes authorized remediation. Finding a problem does not expand that authority.
2. Identify the requested checkout or revision range. Include staged, unstaged, and relevant new files when assessing current development work; do not assume the last commit contains the whole change.
3. List named packages, extensions, adapters, UI, generated artifacts, and documentation to inspect. Mark unavailable surfaces explicitly.
4. Read the behavior's owner, callers, and relevant checks. Establish the expected contract before treating a difference as a defect.

## 2. Inspect behavior and documentation

1. Trace important inputs through changed code and affected consumers. Check compatibility, errors, configuration defaults, ownership, and host/lifecycle behavior where relevant.
2. Compare README, manuals, settings, commands, installation steps, and diagrams in scope with current implementation. Verify actual defaults and paths rather than trusting neighboring prose.
3. Run appropriate non-destructive checks or reproductions when they add evidence. A source-derived finding can stand without runtime access; label it as such.
4. For each suspected problem, identify the concrete trigger and consequence. Inspect enough surrounding code to rule out an existing guard or intentional contract.
5. Exclude cosmetic preferences unless requested or necessary for correctness. Keep optional improvements separate from confirmed regressions.

### Carry scope into supporting investigation

1. Use deeper diagnosis only when a concrete failure needs explanation, and ownership analysis only when evidence exposes a boundary or shared-rule problem. These are conditional investigations, not a mandatory skill chain or delegation.
2. If using `debug-systematically` or `design-modules`, pass the problem, relevant artifacts, known evidence, allowed scope, and expected return. For an assessment-only review, select diagnosis-only or assess/propose respectively. If those skills are unavailable, perform the scoped investigation inline using the same boundaries.
3. In assessment-only mode, keep the target checkout and persistent settings unchanged. Use non-destructive checks or an isolated disposable reproduction; do not add a production fix, refactor, regression test, or doc update to complete the assessment. For explicitly authorized remediation, pass that scope to the supporting investigation and use its implementation branch; changes remain limited to the authorized remedy.
4. Bring the conclusion back into this review: supported finding or bounded uncertainty, affected consumers, executed evidence, proposed correction, planned verification, and remaining limits. Keep planned checks visibly distinct from passing results.
5. Reassess the finding's priority and confidence using that evidence. Report unresolved concerns as questions or gaps rather than upgrading a hypothesis into a confirmed defect.

```text
Supporting investigation: <problem and relevant artifacts>
Known evidence: <observations and uncertainties>
Allowed scope: <assessment-only or explicitly authorized remediation>
Return: <conclusion; executed checks; proposed correction; planned checks; limits>
```

## 3. Record findings

Use the project's severity vocabulary. Rank by effect on users, likelihood under supported use, and scope of impact; do not invent precision without evidence.

```text
<priority> <short finding title>
Location: <file_path:line_number>
Trigger: <supported input, operation, or condition>
Expected/actual: <contract and mismatch>
Consequence: <user-visible impact or maintenance failure>
Evidence: <reproduced check, source trace, or observation still needed>
Correction: <smallest supported remedy; no unauthorized edit>
```

- If the contract or trigger is uncertain, report an investigation question rather than a confirmed bug.
- If behavior is intentional and accurately documented, do not report it as missing solely because an alternative seems preferable.
- If a check fails during review, determine whether it exposes the proposed change, unrelated existing behavior, or test setup before assigning blame.
- If no actionable findings remain, say so and retain the coverage and uncertainty summary; do not add filler findings.

## 4. Handle feedback or authorized fixes

1. For a review comment, verify its claimed trigger and contract against current code before accepting it.
2. If the claim is supported and remediation is authorized, observe a focused regression test fail for the intended defect before correcting behavior, then rerun it and keep it green through cleanup. For behavior-preserving refactors, establish passing existing or characterization coverage first. Preserve already implemented work and disclose missing pre-change observations; use document checks for prose-only edits and mark unavailable host checks pending. Make only the scoped correction, verify affected consumers, and reassess the findings.
3. If unsupported, explain the evidence and leave the behavior unchanged. If material intent is ambiguous, present the decision needed before editing.
4. Respect separately requested source and documentation review boundaries. Do not infer Git authority from acceptance of findings.

## Completion check

- [ ] Every named review surface was inspected or recorded as unavailable.
- [ ] Findings have locations, triggers, consequences, and an evidence basis.
- [ ] Confirmed issues, open questions, and optional improvements are separated.
- [ ] Assessment-only work remains read-only.
- [ ] Supporting investigations preserve the original scope; proposed remedies and planned checks are distinct from work performed.
- [ ] Validation scope and remaining runtime gaps are disclosed.

Return prioritized findings first, followed by executed checks, planned verification, and gaps. State the covered scope and whether material questions remain. Assessment completion means the report is complete for that scope, not that the product is correct or release-ready. Identify an author self-review honestly; do not imply an independent reviewer inspected the work. End assessment-only work at the report; planning or remediation needs its own request or existing authorization.
