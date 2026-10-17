# Worked diagnostic decisions

## Concise unresolved diagnosis

Hypothetical report: “TL;DR: cause unresolved; size alone does not explain the timeout. Comparable small and large payloads both timed out. Next observation: trace whether the request reaches the service before the timeout; host traces are currently unavailable. No remediation performed.” Keep detailed probe records in the linked notes rather than repeating them here.

These are hypothetical walkthroughs, not results observed in your checkout. Use only the example relevant to an unclear decision; the entry route card is sufficient for routine work.

## Reload registration boundary

- **Request:** “Find why the extension fails after reload. No edits.”
- **Given evidence:** A standalone runner passes, but the reported host operation fails registration. Source and installed manifests are available; the installed manifest names an older entrypoint absent from that copy.
- **Decision and action:** Capture the actual reload invocation/error and trace registration through the installed manifest, not just the runner. Hypothesis: the stale entrypoint causes lookup failure; inspection of the host's resolved path should identify that missing file. Inspect the path non-destructively, or use a disposable copy for any experiment needing changes.
- **Result and limit:** Matching path/error evidence can support a source-derived cause and proposed refresh. It does not establish a successful reload after an unperformed refresh. If the host cannot be observed, label that gap; do not patch the installed manifest in diagnosis-only scope.

## Contradicted timeout explanation

- **Request:** “Investigate the timeout; no remediation.”
- **Given evidence:** The current hypothesis predicts failure only for large payloads. A comparable small payload also times out. New host traces are unavailable.
- **Decision and action:** Reject size alone as the explanation. Record comparable workload/runtime conditions and identify the next distinguishing observation, such as whether the request reaches the service before the timeout. Do not keep varying payload size when it adds no separating evidence or persistently increase timeout settings.
- **Result and limit:** Return the rejected explanation, remaining possibilities, and missing trace. A supported cause may remain unresolved; diagnosis does not require a speculative workaround or patch.

## Established byte-counting cause

- **Request:** “The cap counts characters instead of bytes; the cause is proven. Correct it with regression coverage.”
- **Given evidence:** `éé` is four UTF-8 bytes; the current code accepts it under a 3-byte cap. Equality at four must be accepted. The user authorizes this correction.
- **Decision and action:** Confirm current code still has the established mismatch. Carry the evidence into development without repeating broad diagnosis: observe a regression rejecting the over-budget input fail for the understood reason, implement byte counting, and rerun equality, affected consumers, and the original operation.
- **Result and limit:** Report actual regression/original-scenario observations and any pending host check. If the same cause is supplied during diagnosis-only review, propose this correction but do not implement it.
