---
name: execute-plan
description: Execute or resume an approved development plan or established authorized phased work, including its checks, documentation, and handoffs. Use when the user asks to implement that plan or continue its remaining phases. A bare request to continue investigation, design, or editing does not establish plan execution or approval.
license: MIT
compatibility: Manual tracking needs file access. The optional checkpoint helper needs Python 3.9+ standard library and command execution; its read-only Git report additionally needs Git. No host plugin or agent SDK is required.
---

# Execute planned work

Complete authorized planned deliverables inline, including implementation, probes, verification, and review. Supporting workflows do not replace the active phase or introduce delegation or Git actions.

## Entry route

- **Inputs:** approved written or inline plan, established phase scope, current artifacts, and latest corrections.
- **First action:** recover the plan and authorization, then reconcile progress with current files and evidence.
- **Core loop:** retain verified tasks with unchanged inputs → implement the next incomplete task → run its relevant checks → update docs and progress → continue through the authorized scope. An absent approval checkpoint is not a blocker; stop only at a requested checkpoint or a material missing prerequisite.
- **Stop condition:** deliver verified phases through the authorized scope, stopping at requested approval boundaries or missing material prerequisites.

### Route card

Use the row matching current work; linked examples are optional.

| Condition | Next action and minimum evidence | Stop or handoff |
| --- | --- | --- |
| [Approved phase has an incomplete remainder](references/worked-examples.md#resume-with-unchanged-evidence) | Retain tasks with unchanged inputs; implement the next task and check its promised outcome. | Continue authorized scope; stop at requested checkpoints or material prerequisites. |
| [Inputs changed or required runtime unavailable](references/worked-examples.md#stale-copy-and-unavailable-host) | Rerun affected checks against current artifacts; keep unavailable observations pending. | Affected requirement incomplete, not falsely verified. |
| [Only plan progress changed](references/worked-examples.md#record-progress-without-losing-evidence) | Inspect the full old/current diff and check inputs; use optional explicit reconciliation only if unchanged. | Retained check provenance and awaiting-review handoff, not approval. |
| No approved plan or established phased scope | Recover the prior task and its authority; continue that workflow, asking only for consequential missing scope. | No invented plan or approval; do not reopen valid decisions. |

## 1. Re-enter the work

1. Read the selected plan, its governing spec when present, current requirements, project instructions, and latest user corrections. Reconcile stale notes with actual artifacts; newer explicit user corrections control, and unresolved material conflicts stop only dependent work.
2. Inspect the working tree and relevant artifacts. Identify completed, incomplete, and uncertain deliverables using current files and check results.
3. If a previous result's inputs changed, mark its evidence stale and rerun the affected check. Do not restart completed work merely because a progress note is missing.
4. Record remaining phases in the active same-scope task list or plan, even when resuming from another session. Mark the next phase active; preserve unrelated edits. Do not append newly authorized work to a closed plan; select a successor only when a written plan is warranted.
5. Confirm prerequisites for that phase. If a required decision or dependency is missing, resolve it before dependent implementation; continue independent authorized work where possible.

## 2. Deliver the active phase

Select working artifacts before delivery:

1. Resume unfinished same-scope work in its existing plan and location. For new authorized work after closure, use a linked successor when persistence is warranted; preserve the closed record. Link its governing spec when present. Update a living canonical spec for authorized contract changes rather than creating competing specs.
2. If substantial approved work has only an inline plan and persistence is authorized, use the requested or established location and naming convention; otherwise `.your/plans/YYYY-MM-DD-<descriptive-name>.md`, using the creation date. Retain that date during updates; do not automatically rename existing files or overwrite a namesake. A new plan path has separate checkpoint storage; do not transfer old checks as verification of the new scope.
3. Create only missing directories and `.your/.gitignore` containing `*`, preserving existing rules. This local setup, including the ignore file, is not carried into fresh checkouts.
4. For versioned handoffs, use the requested tracked location. Do not manufacture a spec, migrate artifacts, or infer Git authority.
5. With no-file, assessment-only, or no-write scope, track inline unless separately authorized. Report any required persistence as pending.

Choose the check route for each task before changing it:

| Task | Required route |
| --- | --- |
| New or changed software behavior | Focused contract test → intended failure → implementation → green checks/refactor. |
| Behavior-preserving refactor | Passing existing tests and missing characterization coverage first; keep them green. |
| Implementation already present | Preserve it, test the current contract, and disclose missing pre-implementation red; never delete work to recreate failure. |
| Prose or formatting only | Check documents, links, examples, schemas, or formatting as affected; no software red required. |
| Required host inaccessible | Test reachable contracts and retain a repeatable live procedure. Host result stays pending; mocks do not establish host behavior. |

1. Record its promised behavior, affected contracts, exclusions, and required checks.
2. Read the real owner and consumers before editing. Establish the selected check route; do not count unrelated setup errors as an intended failure.
3. Deliver one outcome at a time in dependency order. Apply the route above and migrate consumers with shared contract changes.
4. After each meaningful change, run the checks that can expose its failure. Read the output and compare it with the expected behavior; an exit code alone does not establish coverage.
5. For a bug fix, preserve a regression example and rerun the reported scenario. For accessible host or UI behavior, perform the requested actual-host or rendered check; otherwise retain the pending observation.
6. Update related documentation and the changelog before phase handoff. Apply a version change only when required or requested; preserve historical release entries.
7. Review the phase inline against its requirements, including relevant new files, installed or generated copies, and unintended scope changes.
8. Update task status as each deliverable is verified. Failed or unrun required checks leave affected tasks incomplete.
9. Before handoff, update the active plan concisely with status, deviations, evidence links and limits, remaining work, and pending observations; do not accumulate transcripts or repeat historical reports. At closure, record outcome, actual acceptance state, and remaining gaps once. Checked steps do not close unresolved required work, evidence, or acceptance. Keep approval separate from completion. Update the governing spec only for authorized design changes; a file edit is not approval.

## 3. Handle deviations

- If a check fails, determine whether code, test setup, configuration, or the plan is wrong. Correct the identified cause and rerun; do not bypass the check to obtain a green result.
- If the plan contains a routine mistake, resolve it within scope and record the old assumption, the correction, and affected later steps.
- If the correction changes supported behavior, architecture, or authorization, present that decision to the user before dependent work.
- If a runtime is unavailable, record the exact missing observation and remaining setup. Finish other authorized work, but do not claim that surface verified.
- If later edits invalidate a successful check, rerun it before handoff. Never reuse a helper's historical success as checkout certification.

## 4. Prepare the handoff

Before reporting the phase ready:

- [ ] Promised behavior and all affected consumers are implemented.
- [ ] Required checks ran against relevant current inputs; results and limits are recorded.
- [ ] Related documentation and changelog agree with the delivered behavior.
- [ ] Inline review findings are fixed or explicitly left for a user decision.
- [ ] Remaining work, deviations, and unavailable observations are visible.
- [ ] Existing written plan/spec links and authorized updates reflect current decisions and progress; no competing artifact was created.

Use a concise record:

```text
Phase: <name; complete, incomplete, or blocked on a named prerequisite>
Delivered: <behavior and affected consumers>
Evidence: <check/interaction; observed result; coverage limit>
Docs: <updated surfaces>
Artifacts: <existing plan/spec paths or inline record; actual review state>
Decisions/gaps: <deviations, deferred findings, unrun required checks>
Next: <continue authorized phase, requested approval boundary, or missing input>
```

If the user requested approval between phases, stop at that boundary. Otherwise continue ordinary authorized work. Implementation approval does not authorize commits, branches, publishing, or a separately checkpointed phase. Keep source and documentation approval distinct when the user does.

## Optional checkpoint helper

For longer work, read [helper usage and evidence limits](references/checkpoints.md) before using it. Resolve the script relative to this skill folder; use an existing plan with any text format, including a plan under `.your/plans/`. The helper's logs supplement the written plan. Its writing commands create checkpoint JSON, plan snapshots, and check logs in `.workflow/` beside the selected plan, wherever that plan lives. Manual tracking needs no such directory; `status` creates no files. Permanent regression tests stay in normal project test locations; disposable probes use temporary workspaces, with no default `.your/tests/`.

```sh
python /path/to/execute-plan/scripts/checkpoints.py start /project/plan.md phase-one --workdir /project --summary "Approved phase outcome"
python /path/to/execute-plan/scripts/checkpoints.py check /project/plan.md phase-one --label regression -- <verified-program> <arguments>
python /path/to/execute-plan/scripts/checkpoints.py handoff /project/plan.md phase-one --check regression --summary "Delivered behavior, docs, and remaining gaps"
```

- If a check returns nonzero, inspect its log, resolve the cause, and repeat the affected check; do not hand off as ready.
- If the plan changes, inspect the saved/current diff. Use the reference's explicit reconciliation route only for progress-only edits with unchanged check inputs; material changes require a fresh start and rerun. Preserve valid implementation work; reconciliation is a caller attestation, not verification.
- `awaiting_review` records a handoff, not approval. Its Git report lists current staged/unstaged changes and untracked paths; inspect committed changes and untracked contents separately when in scope.
- Without Python or command access, maintain the same named checks and handoff record manually. The helper is optional.
