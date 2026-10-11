# Inline checkpoint helper

Use Python 3.9+ with the standard library. Resolve the script's path from this skill directory; commands can run from any directory. No host bootstrap or agent API is involved. The existing plan can use any text format. Without command access, record the same phase outcome, named check results, documentation updates, and remaining work manually in the existing plan.

```sh
python /path/to/execute-plan/scripts/checkpoints.py status /project/plan.md
python /path/to/execute-plan/scripts/checkpoints.py start /project/plan.md phase-one --workdir /project --summary "Deliver the approved behavior"
python /path/to/execute-plan/scripts/checkpoints.py check /project/plan.md phase-one --label regression --timeout 300 -- python -m unittest discover
python /path/to/execute-plan/scripts/checkpoints.py handoff /project/plan.md phase-one --check regression --summary "Behavior and docs updated; live reload remains unverified"
python /path/to/execute-plan/scripts/checkpoints.py review /project/plan.md
```

`status` reads without creating files. It reports `state.revision`, `current_revision`, and, when stale, `plan_change`: a diff against the saved snapshot, bounded to 200 lines and 16,000 characters. If `truncated` is true, inspect the full saved snapshot and current plan before deciding. Snapshots preserve exact bytes; displayed diffs decode UTF-8 with replacement and normalize line endings, so inspect the files for encoding-only changes. Missing or corrupt snapshots leave the diff unavailable.

Other commands store local JSON, plan snapshots, and logs in `.workflow/` beside the plan, with a local Git ignore file. `start` resets active checks and reconciliation history; older snapshots and logs remain. A changed plan blocks checks and handoff by default. Check labels retain their latest result independently, with the plan revision at execution recorded in `plan_revision`. Commands run as argument lists without shell expansion, with standard input closed and combined output recorded. Failure, launch errors, timeout, or interruption cannot satisfy a handoff. An unexpected process termination can leave a running result and lock: confirm the process has stopped before removing the lock and repeating the check. Use one writer at a time.

`handoff` requires successful named checks and records `awaiting_review`; it does not grant approval or certify the checkout. Later edits can invalidate recorded results, so rerun affected checks before handoff. Include documentation changes and unverified surfaces in the summary. The helper does not infer coverage or discover which checks are required.

## Reconcile progress-only plan edits

1. Finish implementation and relevant checks, then update the written plan's progress, observed results, and gaps. Run `status` and inspect the diff. Confirm the outcome, acceptance conditions, scope, dependencies, and required checks did not change, and relevant code, configuration, dependencies, fixtures, and installed inputs remain unchanged.
2. For progress-only edits, set `FROM_REVISION` to the inspected `state.revision` and `TO_REVISION` to `current_revision`. The command below is a template using those values. Give a specific reason and declare `--progress-only`; this is a caller attestation, not automated classification or checkout verification.
3. If material plan content changed, use `start` and rerun required checks instead. If checked inputs changed, rerun affected checks; never reconcile merely to keep an old success. An unchanged plan needs no reconciliation, but changed checked inputs still need reruns.

```sh
python /path/to/execute-plan/scripts/checkpoints.py reconcile /project/plan.md phase-one --from-revision "$FROM_REVISION" --to-revision "$TO_REVISION" --progress-only --summary "Recorded regression results; contract and checked inputs unchanged"
python /path/to/execute-plan/scripts/checkpoints.py handoff /project/plan.md phase-one --check regression --summary "Delivered behavior and docs; live reload remains unverified"
```

`reconcile` requires the exact inspected old/current digests, the active phase, the attestation, a nonempty reason, and a valid saved snapshot. It retains check results, original check revisions, and logs; records both plan snapshots, revisions, reason, and caller attestation in the active history; and returns to `working`, removing any previous handoff. It does not rerun checks, upgrade failed/incomplete/running results, or grant approval. If the plan or checkpoint changed after inspection, inspect status again before deciding. Legacy checkpoints remain readable and usable for an unchanged plan; reconciliation without a valid snapshot requires a fresh `start` and rerun.

The helper fingerprints the plan only. It cannot detect code, dependency, environment, or host changes or verify that an attestation is truthful. Check coverage and freshness remain the caller's responsibility. For `.your/plans/<name>.md`, state stays in `.your/plans/.workflow/`, covered by `.your/.gitignore`. No separate `.your/logs/` or `.your/tests/` is required. Read-only Git reports omit ignored `.your/` contents, so inspect selected working specs/plans explicitly when in scope.

`review` requires Git and produces a JSON bundle of current status, staged and unstaged diffs, and untracked paths. It does not include previously committed changes or untracked file contents: inspect those separately when they belong to the review scope. No Git mutation is performed. Check commands are user-selected programs and can themselves modify files; choose only commands authorized for the task.
