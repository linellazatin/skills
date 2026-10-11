---
name: verify-work
description: Verify a fix, development phase, or release against its requested behavior, code, docs, packages, and runtime surfaces before reporting readiness. Use for final passes and phase handoffs; it does not authorize publication.
license: MIT
---

# Establish readiness

Tie each readiness claim to a current artifact and an observation that reaches the claimed behavior.

## Entry route

- **Inputs:** requested deliverables, acceptance conditions, current artifacts, and required check environments.
- **First action:** map each requirement to an artifact, check, expected result, and coverage limit.
- **Core loop:** inspect current inputs → obtain relevant evidence → classify each requirement as established, failed, partial, or unverified.
- **Stop condition:** all required items are established for the named scope, or report incomplete readiness with missing observations. Verification does not authorize publication.

An inaccessible test host means **unverified**, not a failed product or failed reload. Name the missing host observation; do not invent a run or infer its outcome. Passing mocks cannot replace required host acceptance. Continue reachable checks and report incomplete readiness.

Verification alone authorizes checks and findings, not corrective edits. Apply fixes only within already authorized implementation scope; otherwise propose the correction and retain the failed or unverified status.

### Route card

Choose the acceptance scope; linked examples are optional. During execution, return results to the active phase without replacing its handoff.

| Condition | Next action and minimum evidence | Stop or handoff |
| --- | --- | --- |
| [Readiness across declared deliverables](references/worked-examples.md#source-package-and-doc-evidence) | Map every requirement to current artifacts and actual checks; classify established, failed, partial, or unverified. | Ready only for the named scope when all required items are established. |
| [Required observation missing or evidence too narrow](references/worked-examples.md#missing-host-is-not-product-failure) | Record the supported part and exact missing observation; keep reachable checks going. | Incomplete readiness; unavailable is not failed behavior, and mocks cannot replace host acceptance. |
| [Document-only verification](references/worked-examples.md#document-only-scope) | Check affected commands, defaults, and links against the document contract. | Scoped document result; no unrelated host gate or corrective edit inferred. |
| Defect review only | Trace the requested surface against its contract and report findings. | Review, not a readiness claim; review alone cannot establish all requirement coverage. |

Include relevant existing specs and plans in the requirement map, including ignored working files that Git reports omit. Check their claims against current code and user corrections. When artifact updates are authorized, record actual results and pending observations in the existing plan; assessment-only work reports discrepancies inline. Do not create a separate planning document merely to perform verification.

## 1. Build the verification map

1. Read the requested deliverables, plan, acceptance conditions, latest corrections, and required project checks.
2. Inspect the current checkout and relevant built or installed copies. Identify which inputs changed since prior verification.
3. List every requested surface: shared code, CLI, affected adapters/extensions, packaging, host lifecycle, UI, and documentation as applicable.
4. For each requirement, record the artifact, check, expected result, and coverage limit. Mark unavailable checks as pending; do not silently substitute a narrower check.

```text
Requirement/surface | Current artifact | Check and expected observation | Actual result | Limit/status
```

## 2. Obtain current evidence

1. Run the required project checks and read their results. Investigate failures before continuing dependent verification.
2. For a fix, repeat the reported operation with its relevant input or payload shape. Include affected callers after shared-contract changes.
3. For packaging or copied installations, inspect or execute that actual artifact and compare it with source. A source pass alone does not establish artifact parity.
4. For requested host behavior, verify loading/reloading and invocation in that host. For visible UI behavior, inspect and exercise the rendered state.
5. Reuse earlier results only if their relevant inputs remain unchanged. If code, configuration, dependencies, fixtures, or installation changed, rerun affected checks.
6. Record command/interaction, environment needed to interpret it, outcome, and limits. Keep credentials and private payloads out of the report.

## 3. Check documentation

1. Enumerate every documentation surface named by the user and those affected by the change.
2. Compare commands, paths, defaults, versions, installation, architecture, limitations, and references with the delivered behavior.
3. Validate local links and relevant rendered diagrams when their correctness is in scope. Reading diagram text alone does not prove it renders.
4. If assessment-only, report mismatches without editing. If updates are authorized, complete them and the related changelog before readiness handoff.
5. Preserve historical release entries and separately requested source/documentation approval or commit boundaries.

## 4. Decide what can be claimed

- If observed results contradict a requirement, mark it failed and name the mismatch. Recheck after an authorized correction.
- If a required check is unrun or its scope is too narrow, mark that requirement unverified and name the missing observation.
- If the evidence supports only part of a requirement, state the supported part and the remaining gap; do not mark the entire requirement passed.
- If later edits affect evidence, reopen the relevant requirement and rerun its check.
- Declare the requested scope ready only when every required item is established. Optional deferred improvements do not become blockers unless they affect a requirement.

## Completion check

- [ ] Every explicit deliverable has a result in the verification map.
- [ ] Evidence matches the current relevant inputs and actual artifacts.
- [ ] Required regressions, consumers, host/UI observations, and docs are covered.
- [ ] Failed, unverified, and partial results are visible.
- [ ] The conclusion matches the evidence without implying approval, a Git action, or publication.

Return:

```text
Readiness: <ready for the named scope, or incomplete>
Established: <requirements and supporting observations>
Blockers/gaps: <failed, partial, or unrun requirements; next observation>
Docs: <surfaces checked or updated>
Limits: <host, artifact, timing, or evaluation limits>
```

Shorten the record for a small change, but retain any material gap. Do not start a separately checkpointed next phase through a readiness claim.
