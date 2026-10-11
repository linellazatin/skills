---
name: design-modules
description: Assess or migrate module interfaces, responsibilities, and shared-rule ownership when duplicated policy, unclear boundaries, caller burden, or difficult test setup creates a concrete maintenance problem. Use for ownership/interface recommendations or authorized structural migration. Producing a task plan, diagnosing an unknown failure, and open-ended product discovery have different primary outcomes.
license: MIT
---

# Give each rule a clear owner

Reduce the number of places needed to change one rule while preserving the contracts consumers actually use.

## Entry route

- **Inputs:** concrete maintenance problem, owners and callers, public contracts, and assessment or migration scope.
- **First action:** choose the mode, then trace one representative operation and map rule ownership.
- **Migration gate:** run existing tests and add missing characterization for every affected consumer before moving its code. Keep those tests green during migration; do not postpone missing coverage until after the move.
- **Stop condition:** assessment delivers supported ownership choices and compatibility checks; migration additionally needs verified consumers and artifact wiring. Retain the current structure when no concrete problem justifies change.

### Route card

Choose the requested ownership outcome; linked examples are optional.

| Condition | Next action and minimum evidence | Stop or handoff |
| --- | --- | --- |
| [Concrete ownership/interface problem, assessment requested](references/worked-examples.md#shared-rule-and-host-boundaries) | Trace one operation; map owners, caller obligations, and compatibility checks before recommending a boundary. | Supported proposal or uncertainty; no migration. |
| [Similar code, no shared-policy problem established](references/worked-examples.md#similar-code-different-contracts) | Compare actual contracts and host obligations; test whether one rule truly needs multiple edits. | Retain existing structure when similarity alone is the justification. |
| [Agreed migration, implementation authorized](references/worked-examples.md#characterize-before-migration) | Characterize each affected consumer before moving code; preserve public compatibility and keep checks green. | Verified migration or named gap; no new package authority inferred. |
| Only task breakdown or unexplained failure requested | Carry settled ownership into planning, or investigate the failure first. | No reopened architecture or invented ownership defect. |

Read relevant existing specs and plans before reopening design choices. Reconcile them with current callers and user corrections; update decisions, migration steps, and checks only when artifact edits are authorized. An architectural assessment does not automatically create a new spec or plan. Carry approved consequential design into the active same-scope artifact or an authorized written deliverable without duplicating it. Resume unfinished work across sessions; keep closed task records as history. New work after closure uses a linked successor only when persistence is warranted and authorized; living canonical specs remain the contract owner.

Treat a function, class, package, or larger slice as a module with a caller-facing contract. Its interface includes caller obligations beyond signatures. Judge useful behavior against that burden, and locality by where changes and checks concentrate. Use project terminology; implementation size and vocabulary alone do not establish good design.

## Select the mode

1. Use **assess/propose** when the user requests an architectural assessment or recommendation. Use **refactor/migrate** only when implementation is already authorized.
2. Record the problem, affected boundaries, evidence, allowed scope, and requested output. A supporting review investigation inherits the original assessment scope; finding a design problem does not authorize a refactor.
3. In assess/propose mode, inspect without changing source, contracts, configuration, packaging, or documentation. Inspect checks' cache/output effects; use verified suppression/redirection or a disposable copy for required writes, labeling its coverage. A passing exit or unchanged Git status does not establish no writes.
4. Follow sections 1 and 2 in either mode. Use the matching section 3 branch and completion checklist; do not require an implemented migration to complete a recommendation.

## 1. Map the current ownership

1. Read the reported maintenance problem, relevant implementation, callers, and build/install wiring.
2. Follow one representative operation end to end. Record which module owns each rule and which consumers depend on it.
3. Identify duplicated logic and configuration. Distinguish genuinely shared policy from behavior that only looks similar but has different host requirements.
4. Record the relevant public contract: inputs, outputs, errors, defaults, configuration, invocation, ordering, invariants, and resource limits.
5. Identify what callers must learn, configure, or coordinate beyond the signature. Inspect generated or installed copies when they may diverge from source.
6. Classify relevant dependencies: in-process logic/state, local I/O, owned remote service, or external service. Record whether each check reaches real logic, a stand-in, transport, mock, or actual host. A substitute does not prove unobserved dependency compatibility.
7. If no concrete ownership, interface, or testability problem is established, report that result before proposing a new layer. Dependency categories alone do not justify consolidation.

## 2. Compare ownership choices

Build a small table for the rules affected by the proposed change:

```text
Rule | Current owner(s) | Proposed owner | Consumers | Compatibility check
```

1. Identify one proposed maintained owner for each genuinely shared rule. Keep host registration, lifecycle, UI, and payload conversion with the responsible host boundary. In assessment mode this is a recommendation, not an instruction to move code.
2. Compare retaining the arrangement, consolidating the rule, and changing the interface only where viable. For each option, identify caller obligations and the module that absorbs them. Favor useful behavior behind an understandable contract; reducing method counts alone is not an improvement.
3. Check the dependency direction. Shared code should not gain an agent SDK dependency merely to serve one adapter.
4. Trace representative callers as if the layer were removed. Identify obligations that disappear and policy, coordination, or error handling callers would have to recreate. Retain a forwarding layer when it serves compatibility or another observed obligation; reject consolidation that silently spreads shared policy into consumers.
5. Before adding a publishable package or configuration surface, show why an existing module cannot meet the requirement. Do not equate a new directory with a useful architectural boundary.
6. State compatibility obligations and intentional behavior changes. Resolve material changes with the user when they are outside the current authorization.
7. Add substitution points only for an observed dependency, lifecycle, testability, or variation need. Keep private test wiring out of the public contract unless callers need it.
8. Consider dependency injection or separating calculation from effects when it improves control and clarity. Preserve required effects. Multiple implementations are not a prerequisite; a test double alone does not justify an abstraction.
9. If materially different interfaces remain viable, sketch two or three inline with the same caller and constraints. Compare caller burden, hidden work, change locality, dependency handling, and compatibility. Select the supported option; do not force alternatives or reopen settled choices.

## 3. Finish the selected mode

### Assess/propose

1. Return the current ownership map and expected contracts before describing a proposed arrangement. Label proposed owners and caller changes explicitly.
2. Recommend retaining the current structure or making a specific change, justified by the observed maintenance problem and compatibility costs. Separate confirmed defects from optional improvements and uncertain concerns.
3. Identify affected consumers, intentional contract changes, migration order, and checks that would establish compatibility. Distinguish checks already executed from a future verification plan.
4. If the evidence cannot support a choice, report the competing explanations and next observation or user decision. Do not invent a refactor to fill the recommendation.
5. End at the assessment handoff. Enter migration only when authorized, retaining valid findings and separately requested checkpoints.

Assess/propose completion:

- [ ] Current rule owners, consumers, and relevant contracts are mapped, or missing information is explicit.
- [ ] The recommendation is supported by observed costs and viable alternatives; retaining the existing structure remains an option.
- [ ] Caller obligations and change locality justify the interface choice; dependency checks have explicit coverage limits.
- [ ] Proposed ownership and migration obligations are distinct from changes actually made.
- [ ] Compatibility checks are specified, with executed results separated from planned checks.
- [ ] Unresolved decisions and evidence limits are visible; assessment completion makes no migration or readiness claim.
- [ ] The target checkout remains unchanged.

### Refactor/migrate

1. If assessment-only, return the ownership map, recommended option, tradeoffs, and migration checks without editing.
2. Select coverage before changing the owner: characterize unchanged behavior while it is still present; for intentional behavior changes, observe an intended failing test first. Preserve existing implementation and disclose missing before-change observations. Inaccessible host checks stay pending.
3. Migrate the owning rule and real consumers in dependency order. Keep characterization checks passing; after intentional changes, establish green before structural cleanup. Preserve unrelated work.
4. Verify shared behavior through its public contract and check each affected adapter's conversion or lifecycle path.
5. Inspect generated artifacts and package/install wiring when those boundaries change. Account for copied or cached installations explicitly.
6. Remove obsolete forwarding or duplicated policy only after checking remaining callers. Do not remove a public entrypoint without the agreed compatibility handling. Retire an old test only after confirming its contractual assertions are covered by retained tests or are intentionally obsolete; keep focused internal tests that protect meaningful behavior.
7. Update architecture, configuration, installation docs, and changelog to describe the resulting ownership.

Refactor/migrate completion:

- [ ] The proposed boundary solves an observed maintenance or contract problem.
- [ ] Every affected shared rule has a named owner and identified consumers.
- [ ] Host-specific behavior and dependency direction remain explicit.
- [ ] Caller contracts are preserved or intentionally migrated with checks.
- [ ] Verification reaches the promised dependency boundaries; retired tests leave no required behavior uncovered.
- [ ] Generated/installed wiring and related docs agree with the result.

Return mode, observed problem, current/proposed/implemented ownership, caller obligations, locality tradeoffs, rejected alternatives, executed/planned checks, and limits. Say when the current structure is adequate. Assessment completion can include unresolved gaps; it certifies neither the product nor an unperformed migration.
