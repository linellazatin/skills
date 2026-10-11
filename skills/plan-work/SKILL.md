---
name: plan-work
description: Produce or revise an implementation plan from requirements or an agreed design, with ordered tasks, dependencies, and acceptance checks. Use when the requested result is task breakdown or planning a fix, refactor, or multi-package change. Executing an approved plan, diagnosing a failure, and reporting defects in a plan are different primary workflows.
license: MIT
---

# Plan work

Deliver an implementation outline another agent can execute without reconstructing this conversation.

## Entry route

- **Inputs:** requirements or design, current artifacts, constraints, and requested planning or execution scope.
- **First action:** inspect the relevant work and recover settled decisions; identify missing choices before sequencing dependent tasks.
- **Core loop:** map the producer and each real consumer → order characterization, implementation and consumer migration → specify acceptance checks and docs. Planning-only scope means describe these implementation steps without executing them, not omit them.
- **Stop condition:** every requirement has executable steps and a check, or a named unresolved prerequisite. End at the plan unless implementation is already authorized.

### Route card

Use the row matching the requested result; linked examples are optional.

| Condition | Next action and minimum evidence | Stop or handoff |
| --- | --- | --- |
| [Requirements/design ready for task breakdown](references/worked-examples.md#shared-contract-migration) | Map each requirement to owners, consumers, ordered actions, and an observable check. | Executable plan; implement only if separately authorized. |
| [Cause, command, or API unconfirmed](references/worked-examples.md#unconfirmed-integration-command) | Put investigation before dependent work; name the missing observation and its decision. | Provisional affected tasks, not an invented fix or command. |
| [Small prose-only plan](references/worked-examples.md#inline-document-plan) | Use a short inline sequence and document/link checks. | No software red or extra artifact. |
| Review-only or approved execution requested | Preserve the existing contract and scope; route to defect review or execution respectively. | Findings without revision, or authorized delivery; do not substitute another plan. |

## 1. Establish scope

1. Read the request, existing plan, applicable project instructions, and relevant source entrypoints.
2. Record the requested outcome, affected users or callers, supported environments, and explicit exclusions.
3. Identify the assignment: assessment, planning, or implementation. If only planning is requested, do not edit implementation files. Under no-write scope, inspect checks' cache/output effects; use verified suppression/redirection or a disposable copy, labeling its coverage. A passing exit or unchanged Git status does not establish no writes.
4. Carry forward decisions and authorization already supplied. Ask only for missing choices that change supported behavior, compatibility, architecture, or cost.
5. Inspect the current working tree; identify existing work and unrelated edits. Plan around them rather than assuming a clean checkout.

## 2. Establish the design

1. Trace the behavior through its actual producer, shared rules, consumers, and installed or generated copies.
2. Classify each item as a confirmed problem, an unresolved question, or an optional improvement. Attach source or reproduction evidence to confirmed problems.
3. Use the project's priority categories. Put broken intended behavior ahead of cleanup; schedule investigation before promising a fix for an unconfirmed concern.
4. For a material design choice, compare the smallest viable approach with alternatives that change ownership or compatibility. State the chosen approach and its cost.
5. Preserve the product's stated purpose. If a solution would broaden scope, add a dependency, or introduce a publishable package, explain the need and resolve any consequential user decision before including it.

## 3. Specify executable phases

1. Order phases by dependencies and priority. Give each phase one reviewable outcome; combine trivial edits that share the same verification.
2. Identify existing source paths and affected contracts. Use a proposed path only when a new file is actually needed; mark it as proposed.
3. Write steps as actions on those paths, including consumer migration and compatibility handling. Select checks using the routes below.
4. Define a check for each promised outcome: setup, exact inspected command or interaction, expected observable result, and the surface it reaches.
5. Include affected README, changelog, manuals, diagrams, and requested version work. Do not add a release or Git action without its separate authorization.
6. Include the requested review boundary. If phase approval was requested, state what the reviewer will receive and where execution stops; otherwise allow authorized work to continue.
7. If a required runtime cannot be reached, mark its check as pending and name the setup or access needed. Do not replace a host requirement with a unit test.

| Planned work | Check sequence |
| --- | --- |
| New or changed software behavior | Contract test → intended failing observation → implementation → green checks/refactor. |
| Behavior-preserving refactor | Existing tests and missing characterization coverage → structural change with tests passing. |
| Implementation already present | Preserve it; check the contract and disclose any missing pre-change observation. |
| Prose or formatting only | Relevant document, link, example, or formatting checks; no manufactured software failure. |

Use this record for each substantial phase; shorten it for small tasks:

```text
Phase: <name and priority>
Status: <pending, active, complete, or blocked; do not imply approval>
Outcome: <observable behavior>
Depends on: <prerequisites or none>
Paths/contracts: <existing owners, consumers, proposed additions>
Steps: <ordered implementation actions>
Verification: <setup; command/interaction; expected result; coverage limit>
Docs/version: <affected documents and authorized version work>
Handoff: <deliverables; stop for approval only if requested>
```

### Select and save the artifact

- Keep small, clear, single-session plans inline or in the existing task record. Save substantial, multi-phase, resumable, or reviewable plans within authorization.
- Update the existing relevant plan first. Link its governing spec when present; a settled routine fix needs no separate spec.
- Record outcome, scope, decisions, dependencies, paths, ordered tests/implementation, checks, phase status, deviations, and unresolved observations. Specs define intent; plans track delivery.

1. Use the requested or established location first. For an authorized new local plan, the fallback is `.your/plans/<descriptive-name>.md`; date prefixes are optional.
2. Create only missing directories and `.your/.gitignore` containing `*`. Preserve existing ignore rules. All local artifacts, including the ignore file, need setup again in a fresh checkout.
3. For versioned collaboration, use the requested tracked location. Do not migrate files or infer Git authority.
4. File creation needs an explicit request, project convention, or the authorized deliverable. For assessment-only, no-file, or no-write work, keep the result inline unless separately authorized; report required persistence as pending.

Keep permanent regression tests in the project's normal test locations and disposable probes in temporary workspaces. Do not create `.your/tests/` or additional working directories without an actual need. Plans and specs are working records, not substitutes for shipped documentation or current verification.

## 4. Check and hand off the plan

- [ ] Every requirement maps to a phase and an observable check.
- [ ] Every phase has its prerequisites and real consumers identified.
- [ ] Unconfirmed concerns have investigation steps, rather than invented fixes.
- [ ] Commands, paths, APIs, and package names were inspected rather than guessed.
- [ ] Documentation and requested checkpoints are included.
- [ ] Unresolved material decisions and unavailable checks are visible.
- [ ] Artifact selection matches the task; a saved plan links any governing spec and records actual phase/review state.

Return the outcome, chosen design, phases, remaining decisions, and saved plan/spec paths when present. If implementation is also authorized and no required decision remains, proceed inline. Otherwise end at the requested planning deliverable.

## Failure branches

- If requirements conflict with current code, identify the exact mismatch and resolve it before dependent steps.
- If a command or API cannot be confirmed, plan its investigation rather than presenting a fabricated executable step.
- If the user changes scope, update affected phases and checks; preserve already completed work that remains valid.
