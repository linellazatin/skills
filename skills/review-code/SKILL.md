---
name: review-code
description: Review code, changes, extensions, documentation, or implementation plans against requirements and report prioritized defects or omissions. Also evaluate review feedback before accepting it. Assessment stays read-only. Revising a plan and establishing completion or release readiness are different primary outcomes.
license: MIT
---

# Assess the current work

Produce findings tied to actual behavior and scope. Do not change files in an assessment-only review.

## Entry route

- **Inputs:** review surface or feedback, requirements, current revision/artifacts, and allowed remediation scope.
- **First action:** establish the contract and requested surfaces before judging differences.
- **Stop condition:** return supported findings or no actionable findings, executed checks, and coverage gaps. Assessment completion is not product readiness.

### Route card

Choose the requested assessment; linked examples are optional. Supporting review retains the active workflow's scope; no companion skill is required.

| Condition | Next action and minimum evidence | Stop or handoff |
| --- | --- | --- |
| [Defect review of code/docs/changes](references/worked-examples.md#supported-default-regression) | Establish the contract; trace a concrete trigger through owner, caller, and guards. | Supported location/trigger/consequence finding or no actionable findings; no edits inferred. |
| [Review feedback to evaluate](references/worked-examples.md#rejected-empty-input-feedback) | Test the claimed mismatch against current code and evidence before accepting it. | Reject unsupported feedback; propose supported remedies without unauthorized fixes. |
| [Plan omissions, no revision](references/worked-examples.md#plan-review-not-revision) | Compare requirements/consumers with planned steps and checks. | Findings; proposed checks are not executed evidence, and the plan stays unchanged. |
| Plan revision or readiness decision requested | Route to planning or requirement-level verification respectively. | Do not substitute defect findings for a revised plan or readiness coverage. |

- Check existing specs and plans against current code and newer user corrections. Inspect ignored working artifacts directly; Git diffs omit them.
- Update findings, decisions, or verification gaps in those artifacts only when edits are authorized. Assessment-only and no-file requests remain inline unless report writing is separately requested; do not create a plan or spec for every review.

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
2. Carry the problem, artifacts, evidence, scope, and expected return into the inline investigation. For assessment-only review, use diagnosis-only or assess/propose. Companion skills are optional; their absence does not change the scope.
3. Keep assessment-only work read-only in the target checkout and persistent environment. Use non-destructive checks or disposable reproductions; add no product fix, test, refactor, or doc update. If remediation is explicitly authorized, use the matching implementation branch and limit changes to that remedy.
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
2. If unsupported, explain the evidence and leave behavior unchanged. If material intent is ambiguous, resolve that decision before editing. Supported feedback alone does not authorize remediation.
3. For authorized remediation, select checks first: intended regression red for changed behavior; passing characterization for refactors; document checks for prose. Preserve existing work and disclose missing pre-change observations. Unavailable host checks stay pending.
4. Apply only the scoped correction, establish green, verify affected consumers, and reassess findings.
5. Respect separately requested source and documentation review boundaries. Do not infer Git authority from acceptance of findings.

## Completion check

- [ ] Every named review surface was inspected or recorded as unavailable.
- [ ] Findings have locations, triggers, consequences, and an evidence basis.
- [ ] Confirmed issues, open questions, and optional improvements are separated.
- [ ] Assessment-only work remains read-only.
- [ ] Supporting investigations preserve the original scope; proposed remedies and planned checks are distinct from work performed.
- [ ] Validation scope and remaining runtime gaps are disclosed.

Return prioritized findings, executed checks, planned verification, and gaps. State coverage and material questions. Label author self-review honestly; do not imply independence or product readiness. End assessment-only work at the report; planning or remediation needs an explicit request or existing authorization.
