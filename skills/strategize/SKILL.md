---
name: strategize
description: Clarify an idea and choose a workable design before detailed planning or implementation. Use for new projects, features, components, workflows, or behavior changes whose purpose, requirements, or approach need decisions; also for brainstorming, exploring options, "think this through", "what should we build", and feasibility questions. An approved design needing task breakdown belongs to planning; a specified change or proven correction needing implementation belongs to development; an uncertain failure cause belongs to diagnosis.
license: MIT
---

# Turn an idea into a buildable direction

Produce a design grounded in the user's intended outcome, with visible choices and acceptance examples. Work inline and keep discovery proportional to missing decisions.

## Entry route

- **Inputs:** intended outcome, existing work, prior decisions, and constraints; identify material missing inputs through inspection first.
- **First action:** choose unsettled-design, feasibility, or direct-handoff routing below. Reuse supplied answers.
- **Stop condition:** deliver the scoped design or feasibility conclusion with evidence and open decisions. Continue implementation only within existing authorization.

### Route card

Use the row matching the requested result; linked examples are optional.

| Condition | Next action and minimum evidence | Stop or handoff |
| --- | --- | --- |
| [Outcome or approach unsettled](references/worked-examples.md#local-only-search) | Recover intent and constraints; resolve consequential unknowns; recommend an approach with an acceptance example. | Scoped design through sections 2–5; implementation only within existing authority. |
| [Feasibility only](references/worked-examples.md#unavailable-lifecycle-observation) | Identify the uncertain claim and one distinguishing observation; record its result or why unavailable. | Bounded conclusion and next observation; no forced full design. |
| [Settled design needing tasks](references/worked-examples.md#settled-design-or-specified-change) | Carry known decisions and acceptance into dependency-ordered planning. | Plan; no new discovery interview or unauthorized implementation. |
| Specified change or proven correction, implementation authorized | Inspect the settled contract and consumers; develop with scoped checks and a delivery outline when substantial. | Verified authorized work or named gap; size alone does not reopen design or diagnosis. |
| Broken behavior, cause uncertain | Capture actual/expected behavior and the failing boundary. | Diagnosis; reopen design only if evidence exposes a material choice. |

## 1. Identify the decision to make

1. Read the request, prior decisions, existing requirements, and applicable project instructions. Identify what the user wants to achieve, rather than treating a named technology as the goal.
2. Inspect the relevant existing work, entrypoints, docs, and current changes. For a new project, use supplied examples and constraints; do not invent an existing architecture.
3. Record what is known, what you are assuming, and which unanswered questions would change the result.
4. Use the entry route card. State the immediate next action briefly; do not explain a long process before addressing the idea. For a direct handoff, use available guidance or an inline equivalent; skip the full design checklist.

## 2. Resolve the consequential unknowns

1. Establish the intended user or audience, the operation or experience they need, and what would make the result useful. If missing, ask about a concrete use case before proposing a feature list.
2. Establish constraints that affect the solution: existing stack or materials, compatibility, dependencies, runtime or deployment, data ownership, and time or cost where relevant. Reuse known answers.
3. Identify exclusions and unacceptable outcomes. Separate a necessary requirement from a preference or optional improvement.
4. Choose the unanswered question with the greatest effect on scope or design. Ask one focused question at a time; wait for its answer before deciding dependent work. Continue independent inspection where useful.
5. Use an open question to uncover intent; use a short set of choices when the actual decision is between understood alternatives. If the user delegates the choice, recommend a concrete default and label it as your decision.
6. Reflect the resulting understanding briefly: outcome, constraints, exclusions, and assumptions. Correct misunderstandings when the user responds; do not turn your assumptions into user-approved requirements.
7. Stop interviewing when remaining uncertainty is routine implementation detail. If an unknown still changes supported behavior, ownership, or material cost, resolve it or identify it as a blocker instead of quietly choosing for the user.

Example: local-only document search is required, but storage is undecided. “Use an embedded index” is a recommendation, not approval. If the user says “choose the storage,” record it as a delegated choice. If uploading documents would change privacy or cost and is not authorized, keep that decision unresolved; do not treat silence as consent.

## 3. Choose a viable approach

1. Define the smallest complete result that serves the identified use case. Remove extras that do not contribute to it.
2. When materially different options exist, compare two or three on the same criteria: user fit, compatibility, implementation effort, maintenance, and the important risk. Do not invent alternatives merely to fill a table.
3. Lead with a recommended option and explain the deciding tradeoff. Reuse existing infrastructure unless changing it solves an observed constraint.
4. If one uncertainty determines the choice, obtain distinguishing evidence before elaborating the design. Inspect an existing contract, replay a representative input, or run an authorized disposable probe with a predicted observation.
5. Record the probe's setup, actual result, and limit. Throwaway code is an experiment, not a production deliverable; retained software still needs the normal TDD, compatibility, and review work.
6. If the request spans independent systems, separate outcomes and dependencies, then select the first useful end-to-end increment. Do not bundle unresolved systems into a single vague design.

Use a comparison only when it helps the decision:

```text
Option | Fit and constraints | Effort/maintenance | Main risk
Recommendation: <choice; deciding tradeoff; assumptions>
```

## 4. Describe what will be delivered

1. Describe the normal user journey or operation, from input through result. Include a concrete acceptance example that distinguishes success from a merely completed implementation.
2. Identify responsibilities, interfaces, state/data flow, and important failure behavior where they apply. For non-software work, describe the audience, deliverable, sequence, and operating constraints instead of inventing technical architecture.
3. State compatibility, migration, installation, or lifecycle obligations affected by the design. Keep shared policy ownership and host-specific responsibilities visible.
4. Define how the result will be checked: representative behavior, meaningful boundary/error cases, and any required actual-host or rendered observation. Software development proceeds through TDD; unit tests alone cannot establish unobserved host behavior.
5. Separate user decisions, your recommended defaults, and unresolved material questions. Specify what is excluded from the first increment.
6. Select the artifact: small decisions stay inline; substantial consequential designs, compatibility obligations, resumable handoffs, or requested design reviews use an authorized spec. Resume an active same-scope spec or update the relevant living canonical spec; do not append new work to a closed task-scoped spec. Routine fixes and feasibility answers need no extra spec. Apply the storage and authorization branches below.

```text
Outcome and why: <user/audience; problem; success>
Scope: <first complete result; exclusions>
Approach: <chosen option; tradeoff; defaults not explicitly chosen by the user>
Behavior: <normal operation; boundaries/errors; responsibilities>
Constraints: <compatibility, resources, migration, dependencies>
Acceptance: <examples; checks; required host or rendered observations>
Open decisions: <material questions or none>
Next: <design review, requested planning, or authorized development>
```

### Store a written design

1. Use the requested or established location and naming convention first. Resume unfinished same-scope designs across sessions in their existing spec. For newly authorized design work after task-spec closure, create a linked successor when a written spec is warranted; preserve the closed record. Update a [living canonical product spec](references/worked-examples.md#living-spec-versus-closed-task-spec) when its contract changes instead of creating competing contracts.
2. For an authorized new local spec, use `.your/specs/YYYY-MM-DD-<descriptive-name>.md` with its creation date; retain that date during updates. Do not automatically rename existing files or overwrite a same-day namesake; choose a distinct descriptive name.
3. Create only missing directories and `.your/.gitignore` containing `*`. Preserve existing ignore rules. The ignore file is itself ignored; fresh checkouts need local setup again.
4. For versioned collaboration, use the requested tracked location. Do not migrate files or infer commit authority.
5. File creation needs an explicit request, project convention, or the authorized deliverable. For assessment-only, no-file, or no-write work, provide the design inline unless separately authorized; report required persistence as pending.
6. Keep the spec focused on behavior, constraints, decisions, exclusions, acceptance, and material questions; link evidence rather than accumulating transcripts. At task-spec closure, record the outcome, actual acceptance state, and remaining gaps once. Required open decisions, evidence, or acceptance cannot be closed merely because listed steps are complete. Link the associated plan when present; execution progress stays in that plan. Report the saved path at handoff.

## 5. Check the design and hand it off

1. Read the design as the next implementer. Check whether it answers the intended outcome, chosen approach, interfaces or responsibilities, acceptance examples, and exclusions without requiring this conversation.
2. Resolve contradictions, invented APIs, unsupported assumptions, and omitted failure behavior. Inspect available facts before asking the user to supply them.
3. If a review checkpoint or material user decision remains, present the concrete design and that decision; wait before dependent implementation. If design or planning only was requested, end at that deliverable.
4. If implementation is already authorized and remaining choices are delegated or routine, state the choices and continue within scope. Do not require repeated approval for the same work or interpret silence as acceptance of a pending decision.
5. For substantial software work, carry the resolved design into an implementation plan with TDD slices, dependencies, docs, and requested phase boundaries. Use `plan-work` if available; otherwise prepare that outline directly. No companion skill is required.
6. If new evidence changes a settled assumption, reopen only the affected decisions and update the design and acceptance conditions. Preserve valid prior work and explain the impact.

## Completion check

For feasibility, completion means the claim has evidence or a named unresolved observation, with a recommendation and limits. For direct handoffs, completion means the destination, preserved constraints, and next authorized action are clear; continue that work when already authorized. The checklist below applies only to the full design route.

- [ ] The intended outcome and why it matters are grounded in supplied context or answered questions.
- [ ] The approach is justified against real constraints; alternatives are compared only where useful.
- [ ] Concrete behavior, exclusions, and acceptance examples define the first complete result.
- [ ] Assumptions, delegated defaults, and unresolved material decisions are distinct.
- [ ] Required verification includes the relevant runtime or artifact boundaries.
- [ ] The handoff respects the requested scope, existing authorization, and review checkpoints.
- [ ] The selected inline or written artifact fits the work; saved paths and actual review state are clear.

Return the recommendation and design, important tradeoffs, decisions still needed, and the next authorized action. Keep small decisions brief. Do not add browser tooling, visual-companion resources, mandatory scripts, delegation, or automatic Git actions.
