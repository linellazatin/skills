---
name: design-modules
description: Assess or refactor module interfaces, responsibility, and contract ownership across shared code, CLI, adapters, extensions, and configuration. Use when duplicated rules, unclear boundaries, unnecessary layers, complex interfaces, scattered caller knowledge, or difficult test setup make changes hard or inconsistent. Open-ended product discovery belongs to strategy; task breakdown for a settled design belongs to planning.
license: MIT
---

# Give each rule a clear owner

Reduce the number of places needed to change one rule while preserving the contracts consumers actually use.

Read relevant existing specs and plans before reopening design choices. Reconcile them with current callers and user corrections; update decisions, migration steps, and checks only when artifact edits are authorized. An architectural assessment does not automatically create a new spec or plan. Carry approved consequential design into the existing artifact or an authorized written deliverable without duplicating it.

Treat a module as code with a caller-facing contract, whether a function, class, package, or larger slice. Its interface includes every obligation callers must understand, not just method signatures. Evaluate depth by useful behavior provided for that caller burden, and locality by where changes and verification concentrate. Use the project's terminology; neither implementation size nor a mandatory vocabulary establishes good design.

## Select the mode

1. Use **assess/propose** when the user requests an architectural assessment or recommendation. Use **refactor/migrate** only when implementation is already authorized.
2. Record the problem, affected boundaries, evidence, allowed scope, and requested output. A supporting review investigation inherits the original assessment scope; finding a design problem does not authorize a refactor.
3. In assess/propose mode, inspect and run appropriate non-destructive checks without changing source, contracts, configuration, packaging, or documentation. Keep any necessary experiment isolated from the target checkout.
4. Follow sections 1 and 2 in either mode. Use the matching section 3 branch and completion checklist; do not require an implemented migration to complete a recommendation.

## 1. Map the current ownership

1. Read the reported maintenance problem, relevant implementation, callers, and build/install wiring.
2. Follow one representative operation end to end. Record which module owns each rule and which consumers depend on it.
3. Identify duplicated logic and configuration. Distinguish genuinely shared policy from behavior that only looks similar but has different host requirements.
4. Record supported inputs, outputs, errors, defaults, configuration, invocation forms, invariants, ordering requirements, and relevant performance or resource constraints. Inspect what callers must know or coordinate beyond the signature. Include generated or installed copies that may diverge from source.
5. Classify affected dependencies as in-process computation/state, local I/O, owned remote services, or external services. Record what the tests actually reach: real logic, local stand-in, transport, mock, or actual host. A substitute may test owned behavior without establishing database, network, provider, or lifecycle compatibility.
6. If no concrete ownership, interface, or testability problem is established, report that result before proposing a new layer. Dependency categories alone do not justify consolidation.

## 2. Compare ownership choices

Build a small table for the rules affected by the proposed change:

```text
Rule | Current owner(s) | Proposed owner | Consumers | Compatibility check
```

1. Identify one proposed maintained owner for each genuinely shared rule. Keep host registration, lifecycle, UI, and payload conversion with the responsible host boundary. In assessment mode this is a recommendation, not an instruction to move code.
2. Compare retaining the current arrangement, consolidating the rule, and changing the interface only where each is viable. Identify what callers learn, configure, sequence, or repeat in each option, and which module absorbs that work. Favor useful behavior behind an understandable contract and changes that stay with their owner; reducing method counts alone is not an improvement.
3. Check the dependency direction. Shared code should not gain an agent SDK dependency merely to serve one adapter.
4. Trace representative callers as if the layer were removed. Identify obligations that disappear and policy, coordination, or error handling callers would have to recreate. Retain a forwarding layer when it serves compatibility or another observed obligation; reject consolidation that silently spreads shared policy into consumers.
5. Before adding a publishable package or configuration surface, show why an existing module cannot meet the requirement. Do not equate a new directory with a useful architectural boundary.
6. State compatibility obligations and intentional behavior changes. Resolve material changes with the user when they are outside the current authorization.
7. Place substitution points where an observed dependency, lifecycle, testability, or variation need warrants them. Keep private test wiring out of the public contract unless callers need it. Inject dependencies or separate calculation from effects when that improves control and clarity; preserve required side effects. Multiple implementations can justify an interface but are not a prerequisite, and a test double alone does not prove the abstraction useful.
8. When materially different interfaces remain viable, sketch two or three inline using the same representative caller and constraints. Compare caller obligations, hidden work, change locality, dependency handling, and compatibility. Select the supported option; do not force alternatives, delegation, or a second design exercise for a settled choice.

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
2. Before a behavior-preserving refactor, run existing contract tests and add missing characterization coverage while the current behavior is still present. For intentional behavior changes, observe a focused test fail for the intended reason before implementation, then keep it green through structural cleanup. Preserve already implemented work and disclose any missing before-change observation; record inaccessible host checks as pending.
3. If refactoring is authorized, migrate the owning rule and real consumers in dependency order while keeping characterization checks passing. Preserve unrelated work.
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

Return the mode, observed problem, current and proposed or implemented ownership, caller obligations, locality tradeoffs, alternatives rejected with reasons, executed checks, planned checks, and evidence limits. If the current structure already satisfies the need, say so rather than manufacturing a refactor. A completed assessment can identify an unresolved design gap; it does not certify the product or an unperformed migration.
