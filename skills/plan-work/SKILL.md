---
name: plan-work
description: Turn requirements or an agreed design into executable development phases with dependencies, priorities, implementation steps, and checks. Use for task breakdown, substantial fixes, refactors, multi-package changes, or revising an implementation plan. Resolve remaining design decisions as needed; open-ended ideation belongs to strategy and design exploration.
license: MIT
---

# Plan work

Deliver an implementation outline another agent can execute without reconstructing this conversation.

## 1. Establish scope

1. Read the request, existing plan, applicable project instructions, and relevant source entrypoints.
2. Record the requested outcome, affected users or callers, supported environments, and explicit exclusions.
3. Identify the assignment: assessment, planning, or implementation. If only planning is requested, do not edit implementation files.
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
3. Write steps as actions on those paths, including consumer migration and compatibility handling. For new or changed behavior, order each slice as a contract test, an observed intended failure, implementation, and a green refactor/check. For behavior-preserving refactors, establish existing or characterization tests first and keep them passing.
4. Define a check for each promised outcome: setup, exact inspected command or interaction, expected observable result, and the surface it reaches.
5. Include affected README, changelog, manuals, diagrams, and requested version work. Do not add a release or Git action without its separate authorization.
6. Include the requested review boundary. If phase approval was requested, state what the reviewer will receive and where execution stops; otherwise allow authorized work to continue.
7. If a required runtime cannot be reached, mark its check as pending and name the setup or access needed. Do not replace a host requirement with a unit test.

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

Keep a small, clear, single-session plan inline or in the existing task record. Save a written plan for substantial, multi-phase, resumable, or reviewable implementation work within the requested authorization. Update the existing relevant plan before creating another. Link the governing spec when present; do not require a separate spec for a settled routine fix. Include the outcome, scope, decisions, dependencies, affected paths, ordered tests and implementation, checks, phase status, deviations, and unresolved observations. Specs define the intended result; plans track its delivery.

Use the requested or established project location first; otherwise use `.your/plans/<descriptive-name>.md`. On first authorized use, create only missing directories and `.your/.gitignore` containing `*`; preserve an existing ignore file. Date prefixes are optional. These files, including the ignore file, are local and are not carried by Git into a fresh checkout. Use a requested tracked location for versioned collaboration; do not migrate files or infer Git authority. Explicit requests, project conventions, or the authorized deliverable must justify file creation; invocation alone does not. For assessment-only or no-file requests, keep the result inline unless artifact writing is separately authorized. Without write access, disclose any required persistence as pending.

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
