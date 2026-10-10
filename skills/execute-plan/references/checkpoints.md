# Inline checkpoint helper

Use Python 3.9+ with the standard library. Resolve the script's path from this skill directory; commands can run from any directory. No host bootstrap or agent API is involved. The existing plan can use any text format. Without command access, record the same phase outcome, named check results, documentation updates, and remaining work manually in the existing plan.

```sh
python /path/to/execute-plan/scripts/checkpoints.py status /project/plan.md
python /path/to/execute-plan/scripts/checkpoints.py start /project/plan.md phase-one --workdir /project --summary "Deliver the approved behavior"
python /path/to/execute-plan/scripts/checkpoints.py check /project/plan.md phase-one --label regression --timeout 300 -- python -m unittest discover
python /path/to/execute-plan/scripts/checkpoints.py handoff /project/plan.md phase-one --check regression --summary "Behavior and docs updated; live reload remains unverified"
python /path/to/execute-plan/scripts/checkpoints.py review /project/plan.md
```

`status` reads without creating files. Other commands store local JSON and logs in `.workflow/` beside the plan, with a local Git ignore file. `start` resets the active phase's checks; older logs remain. A changed plan is reported stale and requires a fresh start. Check labels retain their latest result independently. Commands run as argument lists without shell expansion, with standard input closed and combined output recorded. Failure, launch errors, timeout, or interruption cannot satisfy a handoff. An unexpected process termination can leave a running result and lock: confirm the process has stopped before removing the lock and repeating the check. Use one writer at a time.

`handoff` requires successful named checks and records `awaiting_review`; it does not grant approval or certify the checkout. Later edits can invalidate recorded results, so rerun affected checks before handoff. Include documentation changes and unverified surfaces in the summary. The helper does not infer coverage or discover which checks are required.

For `.your/plans/<name>.md`, helper state remains beside the plan in `.your/plans/.workflow/`; the `.your/.gitignore` wildcard covers it. No separate `.your/logs/` or `.your/tests/` is required. Update the written plan's phase status, deviations, results, and gaps before reporting the handoff. Those text edits change its digest: finish plan updates before `start` and checks when possible, or start a fresh checkpoint and rerun affected checks after edits. Do not treat an earlier digest's handoff as verification of the revised plan. Read-only Git reports omit ignored `.your/` contents, so inspect selected working specs/plans explicitly when in scope.

`review` requires Git and produces a JSON bundle of current status, staged and unstaged diffs, and untracked paths. It does not include previously committed changes or untracked file contents: inspect those separately when they belong to the review scope. No Git mutation is performed. Check commands are user-selected programs and can themselves modify files; choose only commands authorized for the task.
