# Worked review decisions

These are hypothetical walkthroughs, not results observed in your checkout. Use only the example relevant to an unclear decision; the entry route card is sufficient for routine work.

## Supported default regression

- **Request:** “Review these changes for defects; no edits.”
- **Given evidence:** In this fixture, `adapter.py:12` changes the default from disabled to enabled. The documented caller omits that option and requires disabled behavior. Tracing the caller finds no later guard or deliberate contract change.
- **Decision and action:** Report the concrete mismatch: omission now enables behavior that the caller expects disabled. Attach the changed location, caller/contract evidence, and user-visible consequence; rank using the project's severity vocabulary. Propose restoring the default or resolving an intentional compatibility change.
- **Result and limit:** The source trace supports a finding without pretending to have run the host. The proposed remedy and regression check remain unperformed. If a check is useful under strict no-write scope, inspect its outputs first: Python imports can create ignored bytecode despite a passing exit and unchanged Git status. Python's `-B` suppresses import bytecode only, not arbitrary test writes; otherwise use a disposable copy and label the narrower evidence. Do not patch or infer product readiness from completing the review.

## Rejected empty-input feedback

- **Request:** “This review comment says empty input crashes. Is it valid? Don't fix yet.”
- **Given evidence:** The current public entrypoint guards empty input before indexing, and its focused empty-input check passes. The comment's alleged path does not bypass that guard.
- **Decision and action:** Trace the claimed input through the actual entrypoint and inspect the check's assertion. Reject the crash claim using the guard and passing contract check; do not add another guard merely to accept feedback. If a different entrypoint remains plausible, report that as a question requiring evidence.
- **Result and limit:** No actionable finding for the demonstrated path; behavior stays unchanged. Do not manufacture cosmetic findings or imply that one public-input check covers unrelated callers.

## Plan review, not revision

- **Request:** “Review the migration plan for omissions. Don't revise it.”
- **Given evidence:** The requirements name adapters A and B. The plan implements and checks A but contains no migration/check step for B; source inspection confirms B consumes the changing contract.
- **Decision and action:** Report the omitted consumer and consequence at the plan's relevant phase. Propose adding B's characterization/migration and compatibility check in dependency order. Identify that check as future work, not executed evidence.
- **Result and limit:** Deliver the finding without editing the plan or implementation. A request to revise would select planning; a readiness decision additionally needs requirement-level current observations.
