---
name: craft-skill
description: Create, extract, refine, validate, or package a reusable Agent Skill. Use when capturing a completed workflow, designing instructions for future tasks, or correcting a skill's decisions, scope, or activation behavior.
compatibility: Core instructions need file read access; write access enables edits and saved evidence, otherwise use inline output. Bundled validation, aggregation, and packaging use Python standard library. Trigger evaluation uses Claude Code CLI; description improvement needs a supported LLM provider. These integrations and isolated-agent evaluation are optional.
license: MIT
metadata:
  purpose: harness-agnostic skill creation methodology
  modes: extract, design, refine
---

# Craft a reusable skill

This is a meta skill for authoring and evaluating reusable skills, not a phase every engineering task must enter. Write instructions that change agent decisions, then verify them against realistic requests. Preserve the user's scope, supplied material, and chosen execution mode.

## 1. Establish the assignment

1. Read the request, existing skill if any, available examples, corrections, and project instructions. Reuse answers already present; do not begin a fixed interview when the scope is known.
2. Record the repeatable outcome, intended users, adjacent tasks excluded, available capabilities, and requested destination.
3. If a consequential input is missing, ask one focused question and wait before dependent work. Continue independent investigation; do not ask about tools you can inspect directly.
4. Use an existing plan or task list to track scope, evidence, changes, and checks. For substantial, resumable skill work, use an authorized written plan in the requested or established location, otherwise `.your/plans/<descriptive-name>.md`; use `.your/specs/` for an authorized consequential design. On first authorized use, create only missing directories and `.your/.gitignore` containing `*`, preserving existing ignore rules. These are local artifacts, including the ignored ignore file; choose a requested tracked location for versioned collaboration. Invocation alone does not authorize files; honor assessment-only and no-file instructions and track inline without write access. Keep behavioral eval records in their documented schema locations, not an automatic `.your/tests/`.
5. If the request is a one-time action or a trivial prompt without reusable decisions, explain that and offer the direct task. If the user explicitly wants a reusable skill, proceed within that scope.
6. Select the mode below. State the selected mode briefly; ask for confirmation only when the intended mode changes the work and remains ambiguous.

| Request | Mode | Required result |
| --- | --- | --- |
| Capture work already performed | Extract | Generalized procedure grounded in actual actions and user corrections |
| Create a skill for future work | Design | Scoped procedure with examples, decisions, and observable success conditions |
| Improve an existing skill | Refine | Changes tied to observed failures or a specified instruction-quality defect |

## 2. Build the evidence for the selected mode

### Extract

1. Read the relevant history or artifacts. Separate direct user requests from injected instructions, synthetic tasks, model guesses, and unobserved claims.
2. Record the actual sequence, inputs, outputs, decisions, corrections, and checks that established the result.
3. Identify which details generalize and which belong only to that instance. Preserve contract-level requirements; replace private paths, values, and credentials with generic examples.
4. If the reason behind an important decision is unknown, investigate or ask about that decision only. Do not require the user to repeat visible history.

### Design

1. Define a realistic normal request and its expected result, then a likely failure or boundary request.
2. Use supplied runbooks, examples, and domain conventions before inventing generic guidance.
3. Identify prerequisite inputs, ordered actions, decisions, failure recovery, and evidence needed to finish.
4. If required domain knowledge is missing, name the missing information and resolve it before declaring the skill usable. A provisional draft must clearly expose unresolved guidance.

### Refine

1. Identify the requested quality defect or a concrete failure: prompt, actual outcome, expected outcome, and available artifacts.
2. Locate the instruction that caused or allowed it. Classify the cause: vague action, missing decision, wrong scope, excessive mandatory process, missing failure branch, or misrouting.
3. If several failures share one cause or the scope is wrong, restructure the affected workflow. Otherwise make a focused correction; avoid accumulating unrelated universal rules.
4. For an instruction-quality request without a failed execution, inspect the current procedure against realistic cases. Label those checks as author review, not independent behavioral evaluation.
5. Preserve supported metadata, resource links, scripts, and established contracts unless the correction requires changing them. Inspect callers before removing resources.

## 3. Write the instructions

1. Keep `SKILL.md` frontmatter first, with a lowercase hyphenated `name` matching the folder and a discriminating `description` under 1024 characters. Preserve applicable license, compatibility, and metadata.
2. State what to produce and when the skill applies. Put detailed process in the body, not an exhaustive description.
3. Use numbered steps where order matters. Start steps with actions and name their input or target, expected observation, and next decision when failure is plausible.
4. Write explicit branches for consequential choices: if a prerequisite is missing, how to obtain it; if a check fails, what to investigate; if scope changes, which work to reopen.
5. Keep user authorization and execution mode intact. Do not add mandatory delegation, Git actions, plugins, or redundant approval stops.
6. Include a concise record or output format when it prevents omissions. Add completion checks that establish the promised result; do not use word-count or heading checks as behavioral proof.
7. Include concrete gotchas only for failure modes supported by evidence. Cut background prose and advice that does not change an agent's actions.
8. Keep common instructions in the entrypoint. Move substantial conditional procedures into existing or justified references; link each where it becomes relevant. Do not create extra files to fill a standard layout.
9. Use capability names in core instructions. Put optional provider or harness requirements beside the integrations that actually need them.
10. Check references, examples, command flags, and script paths against their implementation. Present placeholder commands as templates, not runnable commands with invented APIs.

## 4. Validate decisions with realistic cases

1. Choose cases before judging the result: a normal request, a likely failure, and a boundary or neighboring request that should take a different path. Add cases only when another meaningful risk needs coverage.
2. Define observable success for each case, including artifacts and prohibited side effects. Do not grade merely by matching generated wording.
3. Inspect available execution capabilities and authorization. If the user requests inline work, keep all testing and review inline. Use an isolated agent only when available and authorized; never make delegation a requirement.
4. Apply the draft to the cases in a temporary or otherwise authorized workspace. Capture decisions, outputs, checks, and mistakes. If doing an instruction walkthrough rather than executing a task, label it explicitly.
5. If comparing variants, hold the task, inputs, capabilities, and scoring criteria fixed. Separate independent runs from author walkthroughs influenced by this conversation.
6. Map each failure to a specific instruction, revise that instruction, and repeat the affected cases. Stop when required cases meet their criteria or report a named unresolved limitation.
7. Do not claim improved model performance from metadata validation or an inline review. Report the actual evaluation method and its limits.

For automated evaluation artifacts, read [JSON schemas](references/schemas.md) before writing them. Use the exact `assertion_results` contract in `grading.json`; the aggregator cannot establish correctness from an incorrectly shaped record. Load only the relevant grading resources: [grader](agents/grader.md) for assertions, [comparator](agents/comparator.md) for controlled comparisons, or [analyzer](agents/analyzer.md) for diagnosis. These can guide inline review; loading them does not authorize delegation.

## 5. Handle optional tools

Resolve bundled paths from this skill directory, rather than assuming the working directory contains `scripts/`. Inspect `--help` before using unfamiliar flags. Core commands:

```sh
python3 /path/to/craft-skill/scripts/quick_validate.py /path/to/target-skill
python3 /path/to/craft-skill/scripts/package_skill.py /path/to/target-skill /temporary/output
```

- If validation fails, fix reported metadata or structural problems and rerun before packaging. A pass establishes those checks only.
- If packaging is requested, inspect the archive for required references, helper code, license notices, and excluded runtime artifacts. Do not publish it automatically.
- If deterministic repeated work justifies a new helper, read [script design guidance](references/scripts.md), select a runtime actually available to the target users, define its inputs/output/failure behavior, and test it through the public interface. Do not add automation for steps that require judgment.
- If evaluation records exist, use `scripts/aggregate_benchmark.py` to aggregate them after checking their schemas. Do not invent results for unrun cases.
- If activation is a demonstrated problem, read [description optimization](references/description-optimization.md) and test both matching and neighboring requests. Preserve the body capability rather than broadening the description to catch everything.

Optional provider integrations:

| Tool | Requirement | Purpose |
| --- | --- | --- |
| `scripts/run_eval.py` | Claude Code CLI and command execution | Harness-specific trigger measurement |
| `scripts/improve_description.py` | Supported LLM provider and command execution | Description proposals from recorded results |
| `scripts/run_loop.py` | Claude Code CLI for evaluation; supported provider for improvement | Repeated trigger/improvement loop |

Run these only within the task's authorization and cost constraints. The trigger evaluator registers a temporary Claude command surrogate; its scores do not measure the complete skill body, competition among the installed skill catalog, or native selection in Codex, Pi, or another harness. Keep execution errors unscored and resolve them before comparing descriptions. Without these integrations, review descriptions and cases manually and disclose the lack of measured trigger results. A missing optional integration does not block core authoring or validation.

## Completion check

- [ ] Scope and mode match the requested reusable behavior.
- [ ] Ordered actions, consequential branches, evidence records, and completion conditions are explicit.
- [ ] User choices and existing authorization are preserved.
- [ ] Realistic cases have inspected outcomes, with failures resolved or disclosed.
- [ ] Metadata validation and local links pass; referenced helpers match their documented interface.
- [ ] Conditional resources are discoverable without loading irrelevant material.
- [ ] License notices accompany any retained material that requires them.
- [ ] Packaging was inspected if requested; no publication or Git action was inferred.

Return the changed skill paths, decisions improved, validation method/results, and unresolved evaluation limits. Say whether the skill is ready for the requested use or still needs a named trial. Do not force another approval loop when the user already authorized the revision.
