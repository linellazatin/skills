# Worked execution decisions

## Concise phase handoff

Hypothetical handoff: “Both callers use the shared byte-cap rule; compatibility checks passed against the current source. Details: linked check log. Phase acceptance remains incomplete: required host reload is unverified because the host is unavailable.” Update the phase status in place; do not copy its checklist or earlier reports into this handoff. On resume, retain the source result only if its inputs remain unchanged and keep the host requirement pending.

These are hypothetical walkthroughs, not results observed in your checkout. Use only the example relevant to an unclear decision; the entry route card is sufficient for routine work.

## Resume with unchanged evidence

- **Request:** “Resume the approved phase. Keep work inline; no commits.”
- **Given evidence:** An earlier session saved an active plan at `.your/plans/2026-10-10-policy-migration.md`. Task one has observed passing checks against unchanged inputs. Task two remains unimplemented. The plan authorizes both tasks and specifies no approval stop between them.
- **Decision and action:** Resume that same plan without renaming its creation date or creating a second plan because the session changed. Inspect current artifacts to confirm task one's evidence still applies; retain its verified status. Implement task two through the appropriate test route, run its consumer checks, update affected docs and existing progress notes, and review the delivered phase.
- **Result and limit:** Continue the authorized remainder without redoing task one or inventing a fresh approval gate. Completion still needs task two's actual evidence; a progress note alone cannot establish it. Do not commit.

## Stale copy and unavailable host

- **Request:** “Finish this phase; verify the installed copy and host reload.”
- **Given evidence:** A copied artifact was replaced after the earlier source test. Host reload is a required acceptance observation, but that host is inaccessible.
- **Decision and action:** Reopen the affected evidence, inspect the current copied artifact, and run reachable contract checks against it. Record a repeatable host setup, reload/invocation, expected observation, and cleanup procedure. Continue independent authorized tasks.
- **Result and limit:** The copy may be established by new observations, but the host requirement remains incomplete. Neither historical source success nor a mocked reload establishes current host behavior. Do not infer that the inaccessible host failed or report the entire phase ready.

## Record progress without losing evidence

- **Request:** “Record completed checks in the existing plan without rerunning unchanged checks.”
- **Given evidence:** The checkpoint has a valid snapshot and a passed named check. Only progress/results text changed; contract and relevant check inputs are unchanged. The caller inspected the full old/current diff and both digests.
- **Decision and action:** Use the [documented reconciliation sequence](checkpoints.md#reconcile-progress-only-plan-edits), binding both digests and declaring progress-only with a specific reason. Inspect the retained check result, original `plan_revision`, and log; then hand off with the required labels.
- **Result and limit:** Reconciliation returns to `working`; handoff records `awaiting_review`, not approval. Changed requirements require a fresh start and rerun. Changed code/configuration/dependencies require affected reruns even if the plan is unchanged; reconciliation cannot detect or certify their freshness.
