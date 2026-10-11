# Worked decisions

These are hypothetical walkthroughs, not results observed in your checkout. Use only the example relevant to an unclear decision; the entry route card is sufficient for routine work.

## Local-only search

- **Request:** “Choose an offline document-search design. Uploads are prohibited; storage is your choice. Do not implement yet.”
- **Given evidence:** Documents already live locally; repeated searches and incremental updates matter. A fixture document A contains “oauth setup”; document B contains “billing”. No storage decision was previously approved.
- **Decision and action:** Compare scanning documents on each query with maintaining a local index. Scanning avoids index maintenance; an index adds update handling but avoids repeating the scan. Recommend the index as a delegated choice, not an explicitly user-selected technology. Keep updates and queries in process; do not add a hosted service.
- **Result and limit:** The first increment indexes local documents and returns A, not B, for “oauth”, without sending documents over the network. Define update/error checks and exclude remote search. Record this as the design's acceptance example, not a passing test. Stop at the requested design; resolve any remaining privacy or compatibility choice before dependent work.

## Unavailable lifecycle observation

- **Request:** “Can indexing work without a background service? Feasibility only.”
- **Given evidence:** Local calculation is possible, but the decisive question is whether the host permits work after its UI closes. That host is inaccessible.
- **Decision and action:** Identify the lifecycle observation: start indexing, close the UI, and observe whether the task survives. Inspect available lifecycle documentation, separating it from a live observation. Do not run a standalone worker and claim it proves host behavior.
- **Result and limit:** Feasibility remains conditional on the missing lifecycle check. Recommend in-process work while the application is open, if that operating limit fits the user; otherwise name the decision needed. Stop without a full design interview or implementation.

## Settled design or specified change

- **Request:** “The local-search design and compatibility rules are approved. Break them into tasks; do not implement.”
- **Given evidence:** Interfaces, local-only behavior, and acceptance are settled; only delivery order is missing.
- **Decision and action:** Carry those choices into planning: characterize existing behavior, implement the index/update contracts, wire real consumers, and specify acceptance/docs checks. Do not reopen storage or ask who the users are again.
- **Result and limit:** Deliver the plan, not code or an unrequested second spec. If instead the request authorizes a specified flag change or proven byte-counting correction across several consumers, inspect its settled contract and proceed through development/checks. Substantial work may need a delivery outline, not renewed discovery or diagnosis merely because it is large.

A proven cause is not necessarily a settled correction. If the timeout cause is known but buffering or retention behavior remains undecided, resolve those design choices before dependent implementation; do not repeat cause diagnosis or invent the missing behavior. An unknown cause still needs diagnosis. These routes do not require the full design checklist unless material design choices actually remain.
