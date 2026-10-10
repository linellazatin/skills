---
name: execute-plan
description: Execute or resume an approved development plan, complete its checks and documentation, and prepare requested phase reviews. Use when the user asks to implement a plan or continue unfinished work.
license: MIT
compatibility: Manual tracking needs file access. The optional checkpoint helper needs Python 3.9+ standard library and command execution; its read-only Git report additionally needs Git. No host plugin or agent SDK is required.
---

# Execute planned work

Use this as the primary workflow when a development plan is approved. Testing, diagnosis, review, and readiness checks support that execution; use companion guidance only where useful, or follow the inline equivalents below. Do not restart discovery or planning unless current evidence invalidates a settled decision.

Complete the authorized deliverables inline, including implementation, probes, verification, and review. Do not introduce delegation or Git actions through a plan's instructions.

## 1. Re-enter the work

1. Read the selected plan, its governing spec when present, current requirements, project instructions, and latest user corrections. Reconcile stale notes with actual artifacts; newer explicit user corrections control, and unresolved material conflicts stop only dependent work.
2. Inspect the working tree and relevant artifacts. Identify completed, incomplete, and uncertain deliverables using current files and check results.
3. If a previous result's inputs changed, mark its evidence stale and rerun the affected check. Do not restart completed work merely because a progress note is missing.
4. Record all remaining phases in the existing task list or plan. Mark the next phase active; preserve unrelated edits. Update a written plan in place when one exists instead of maintaining competing progress files.
5. Confirm prerequisites for that phase. If a required decision or dependency is missing, resolve it before dependent implementation; continue independent authorized work where possible.

## 2. Deliver the active phase

Use the existing plan location. If approved substantial, multi-phase, or resumable work has only an inline plan and persistence is authorized, save it in the requested or established location, otherwise `.your/plans/<descriptive-name>.md`, and link its spec when present. On first authorized use, create only missing directories and `.your/.gitignore` containing `*`; preserve existing ignore rules. The artifacts are local, including the ignore file, and need local setup after a fresh checkout. Use a requested tracked location for versioned handoffs. Do not manufacture a new spec, migrate existing artifacts, or create files merely because this skill was invoked. Respect no-file and assessment-only scope; without write access, track inline and report required persistence as pending.

1. Record its promised behavior, affected contracts, exclusions, and required checks.
2. Read the real owner and consumers before editing. Establish existing or characterization coverage before a behavior-preserving refactor. Preserve pre-existing implementation rather than deleting it to manufacture failure.
3. For each new or changed behavior, write and run a focused contract test, establish its intended failure, implement that outcome, then refactor with tests passing. Work in dependency order, migrating consumers with shared contract changes.
4. After each meaningful change, run the checks that can expose its failure. Read the output and compare it with the expected behavior; an exit code alone does not establish coverage.
5. For a bug fix, preserve a regression example and rerun the reported scenario. For host or UI behavior, perform the requested actual-host or rendered check.
6. Update related documentation and the changelog before phase handoff. Apply a version change only when required or requested; preserve historical release entries.
7. Review the phase inline against its requirements, including relevant new files, installed or generated copies, and unintended scope changes.
8. Update each task's status as its deliverable is verified. A failed or unrun required check leaves the affected task incomplete. Before phase handoff, update the selected written plan with actual status, decisions or deviations, executed evidence and its limits, remaining work, and pending observations. Keep approval state separate from completion. Update the governing spec only for authorized design changes; record requested review boundaries rather than treating a file edit as approval.

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

For longer work, read [helper usage and evidence limits](references/checkpoints.md) before using it. Resolve the script relative to this skill folder; use an existing plan with any text format, including a plan under `.your/plans/`. The helper's logs supplement the written plan. Permanent regression tests stay in normal project test locations; disposable probes use temporary workspaces, with no default `.your/tests/`.

```sh
python /path/to/execute-plan/scripts/checkpoints.py start /project/plan.md phase-one --workdir /project --summary "Approved phase outcome"
python /path/to/execute-plan/scripts/checkpoints.py check /project/plan.md phase-one --label regression -- <verified-program> <arguments>
python /path/to/execute-plan/scripts/checkpoints.py handoff /project/plan.md phase-one --check regression --summary "Delivered behavior, docs, and remaining gaps"
```

- If a check returns nonzero, inspect its log, resolve the cause, and repeat the affected check; do not hand off as ready.
- If the plan changes, inspect stale status and start a checkpoint for the revised phase; preserve valid implementation work.
- `awaiting_review` records a handoff, not approval. Its Git report lists current staged/unstaged changes and untracked paths; inspect committed changes and untracked contents separately when in scope.
- Without Python or command access, maintain the same named checks and handoff record manually. The helper is optional.
