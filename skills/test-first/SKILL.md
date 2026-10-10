---
name: test-first
description: Implement specified new or changed software behavior and established bug corrections through test-driven development; protect behavior-preserving refactors with characterization tests. Use as direct development or support within an approved phase. Uncertain causes need diagnosis first; prose-only edits use document checks instead.
license: MIT
---

# Develop behavior through tests

Use test-driven development by default for new and changed software behavior. Keep execution and review inline; preserve the user's scope and existing work. Within a plan, diagnosis, or migration, these cycles support the active task rather than replacing its tracking or handoff.

## Entry route

- **Inputs:** specified behavior or established correction, current implementation, and inspected test commands.
- **First action:** choose the special-case route below, then select one input/condition and its independent expected result.
- **Core cycle:** test one contract → observe intended red → implement the outcome → observe green → refactor only when useful, retaining green.
- **Stop condition:** the promised behavior and affected checks are observed, with unavailable required checks still explicit. Do not claim a red-green cycle for an exception route.

“Implement this specified flag” or “correct this proven byte-counting defect” selects development. “Find why it fails” selects diagnosis first. “Rewrite the README” needs document checks, not a software test cycle.

## 1. Select one behavior

Use acceptance examples in existing specs and plans as test inputs, checking them against current requirements. Record cycle evidence and missing observations in the existing authorized plan when present; do not create a planning file for every test cycle. Permanent regression tests belong in the project's normal test locations, while disposable probes use temporary workspaces rather than a default `.your/tests/`.

1. Read the requirement, actual caller, existing implementation, project instructions, and test commands. Reuse the established framework and test location.
2. Write the contract as an input or condition and an observable result. Include errors and side effects when they are part of the promise.
3. List meaningful examples: normal use, the relevant boundary, and failure or alternate supported input. Choose one example for the next cycle; do not implement all examples before running their tests.
4. Choose the lowest-cost entrypoint that reaches this contract. Use a unit test for an owned rule, an integration test for collaborating components, and an actual host or rendered interaction for lifecycle or UI behavior.
5. Record the focused test command and the affected consumer/regression checks. Establish existing failures before attributing them to new work.

Route special cases explicitly:

- **Bug fix:** reproduce the reported input or invocation in a failing regression test before changing the cause.
- **Behavior-preserving refactor:** run existing tests and add missing characterization coverage first. Then change structure while those tests stay green; do not invent a failure for behavior that should remain unchanged.
- **Implementation already exists:** preserve it. Test the contract and disclose that no pre-implementation failure was observed. Use an authorized isolated earlier-version reproduction when helpful; never delete user work to recreate red.
- **Host cannot be automated or accessed:** test the reachable contract first and retain a repeatable live procedure. Report the host check as pending or manually observed; a mock does not establish loading, registration, or rendered behavior.
- **Prose-only or formatting-only change:** use relevant document or formatting checks. If documentation contains executable examples or schemas, check those contracts where affected.

## 2. Red: make the contract fail visibly

1. Write one focused test with a clear setup, action, and assertion. Name it for the behavior and condition it demonstrates.
2. Derive the expected result from the requirement or an independent known example. Do not calculate it using the same algorithm as the implementation.
3. Run the focused test before writing the behavior. Read the failure and confirm it exposes the missing or incorrect outcome.
4. If it fails at unrelated setup, imports, fixtures, or environment, repair the test setup and rerun. A missing API can be the intended failure for a new contract; an unrelated dependency error cannot.
5. If it passes unexpectedly, inspect whether the behavior already exists or the assertion misses the distinction. Correct the test or narrow the promised change; do not manufacture red by breaking working behavior.

Proceed to implementation only after the selected behavior has an understood failing observation, or the special-case route above has been recorded honestly.

## 3. Green: implement the selected outcome

1. Make the smallest coherent production change that satisfies the contract across its supported inputs. Avoid speculative options and unrelated cleanup.
2. Run the same test again. If it still fails, investigate the actual mismatch; do not weaken the requirement to accept the patch.
3. Run nearby tests that share the changed rule or consumer. If they fail, determine whether the implementation broke a supported contract or the requirement intentionally changed it.
4. Keep existing expectations unless an intentional contract change justifies updating them. Record that decision and verify its affected callers.
5. Once the selected test and relevant checks pass, proceed to refactor or the next behavior. Do not pile additional functionality onto an unverified change.

## 4. Refactor: improve structure with green evidence

1. Inspect the implementation and tests for duplication, unclear naming, avoidable coupling, or excessive setup introduced by the cycle.
2. If cleanup improves the delivered code, make a behavior-preserving change and rerun affected tests after each meaningful edit. If no cleanup is useful, record that and continue.
3. If a refactor breaks a test, establish whether it changed the public contract or exposed a test tied to private arrangement. Fix the actual defect; do not discard an assertion that protects required behavior.
4. Repeat red-green-refactor for the next meaningful example. Add boundary and failure cases that distinguish plausible wrong implementations.
5. At the phase boundary, run required regression and consumer checks against the final state. Repeat the reported operation when focused tests cover a narrower layer.

## Write tests that detect mistakes

Apply the checks relevant to the selected contract; do not turn every item below into an additional test or mandatory tool.

- **Assert the contract:** check returned values, observable state, errors, or externally meaningful effects. A test that merely checks non-null or no exception is insufficient when a precise result is promised.
- **Make failure diagnostic:** use behavior-based names, explicit expected values, and assertions whose output identifies the mismatch. Keep setup, action, and assertions visibly separate.
- **Keep one scenario focused:** several assertions may establish one result, such as an error plus unchanged state. Split unrelated behaviors instead of enforcing one assertion per test.
- **Cover distinctions:** choose cases at, below, and above a meaningful threshold, or empty, absent, malformed, repeated, and alternate supported inputs where the contract defines them. Do not add combinatorial cases without a distinct failure risk.
- **Protect failure behavior:** when an operation should fail safely, assert the intended error and absence of forbidden side effects, such as a partially written record or duplicate request.
- **Use real owned logic:** do not mock the function under test or all collaborating code and then claim the system works. Mock external boundaries or expensive/non-deterministic dependencies when necessary, and retain integration or contract checks for those boundaries.
- **Assert interactions only when contractual:** exact call counts, ordering, and payloads belong in a test when retry, lifecycle, transaction, or protocol behavior requires them. Do not freeze incidental helper calls.
- **Isolate state:** use per-test fixtures, temporary directories, and explicit cleanup. Tests must not depend on execution order, previous runs, a developer's credentials, or shared production data.
- **Control nondeterminism:** inject or control time, randomness, network responses, and scheduling where feasible. Wait for observable conditions with bounded timeouts rather than arbitrary sleeps; do not hide flaky behavior with retries.
- **Choose useful fixtures:** retain the failure-causing shape with minimal irrelevant data. Use generated properties or parameterized examples when they exercise distinct contracts; snapshots need stable contents and review of what changed.
- **Check test sensitivity:** ask which plausible bug would fail this test. When uncertainty matters, try a deliberate wrong implementation in an isolated disposable copy and confirm the test catches it. Never mutate user work merely to prove the test.
- **Use coverage as a locator:** unexercised branches can reveal missing scenarios, but high line coverage or test count does not establish correct assertions or host behavior.

Example test design, using a hypothetical UTF-8 byte-budget contract:

| Scenario | Independent expected observation | Mistake detected |
| --- | --- | --- |
| Two `é` characters, budget 3 bytes | Reject: the known encoded input occupies 4 bytes. | Counting characters instead of bytes |
| Same input, budget 4 bytes | Accept at the exact limit. | Rejecting equality with the cap |
| Same input, budget 5 bytes | Accept below the limit. | An implementation that rejects every input |

The fixture expectations come from the stated byte contract, not a call to the implementation to generate expected answers. Add invalid-budget cases only after defining how the public contract handles them.

## Retain evidence and complete the phase

Record meaningful cycles in the existing task notes; do not create a separate ledger for every assertion:

```text
Behavior: <input/condition and independent expected outcome>
Test/entrypoint: <focused command and boundary reached>
Red: <observed intended failure, or named special-case route>
Green: <same test and observed passing outcome>
Refactor: <cleanup and rerun, or no useful cleanup>
Final checks: <affected consumers, regressions, original scenario>
Limits: <unobserved host/runtime behavior or existing failures>
```

- Retain tests in the established test location; retain live setup, invocation, observation, and cleanup steps where automation cannot reach the host.
- Keep secrets and private logs out of fixtures and reports. Update related test instructions, affected docs, and changelog before handoff.

Before declaring the phase ready:

- [ ] New or changed behavior has an observed, understood red result before implementation, or an explicitly recorded special-case route.
- [ ] Expected outcomes are independent of the implementation; meaningful boundary and failure cases are covered.
- [ ] Tests exercise real relevant behavior, isolate state, and produce useful failure diagnostics.
- [ ] Green and any refactor checks were observed against the final relevant inputs.
- [ ] Required consumers, regressions, documentation, and live observations are established; pending checks remain visible and keep the affected requirement incomplete.

Return the behavior delivered, red/green/refactor evidence, final checks, and remaining gaps. Do not claim a test-driven cycle or a live-host result that was not actually observed.
