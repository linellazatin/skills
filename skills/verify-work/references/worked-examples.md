# Worked verification decisions

## Concise incomplete-readiness report

Hypothetical report: “Readiness incomplete: current source/core, CLI, and documentation checks passed; details are in the verification map. Copied-installation reload remains unverified because the host is inaccessible. Next observation: reload and invoke the copied artifact in that host.” The host gap appears once; the underlying map still accounts for every required surface.

These are hypothetical walkthroughs, not results observed in your checkout. Use only the example relevant to an unclear decision; the entry route card is sufficient for routine work.

## Source, package, and doc evidence

- **Request:** “Verify readiness for the core, CLI, copied installation, and docs. No corrective edits.”
- **Given evidence:** Current source/core and CLI checks pass. The copied artifact and installation instructions have not been checked. All four surfaces are required.
- **Decision and action:** Map each requirement separately: current artifact, check/expected observation, actual result, and limit. Inspect/execute the copied artifact rather than reusing source results; compare its entrypoints and required contents with source. Check documented commands/defaults against implementation. Retain any failed, partial, or unrun item in the map.
- **Result and limit:** Source/core and CLI may be established; readiness remains incomplete until artifact/docs evidence is obtained. Verification does not authorize repairing a stale installation or rewriting instructions. Do not omit unchecked surfaces to report a smaller denominator as complete.

## Missing host is not product failure

- **Request:** “Can this release be declared ready? Reload in the actual host is required.”
- **Given evidence:** Unit and mock checks pass. The host is inaccessible; no reload was observed.
- **Decision and action:** Record reachable contracts as established only at their scope. Mark host acceptance unverified and retain the live setup, reload/invocation, expected observation, and cleanup procedure. Continue independent reachable checks; propose no corrective edit merely because access is missing.
- **Result and limit:** Readiness is incomplete. Neither “host reload failed” nor “reload passed” follows from unavailable access. Passing mocks cannot establish the required host observation; a genuinely observed contract mismatch would instead be failed evidence.

## Document-only scope

- **Request:** “Verify the rewritten installation paragraph and links. No edits.”
- **Given evidence:** Only documentation changed; no runtime, host, or release acceptance was requested. The paragraph points to an existing helper and describes its flags.
- **Decision and action:** Resolve affected links and compare the described flags/defaults with the actual helper interface. Check any relevant executable examples without changing product state. Report a mismatch if found, rather than correcting it without authority.
- **Result and limit:** A passing document check can establish the named document scope. It does not establish host behavior or release readiness, but unrelated host checks are not blockers for this request.
