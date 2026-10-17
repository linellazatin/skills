---
name: craft-skill
description: Create, extract, assess, refine, validate, or package a reusable Agent Skill. Use to capture completed workflows as skills, design reusable instructions, or evaluate and improve skill triggers and procedures. Ordinary product development, code review, and readiness checks are not skill-authoring tasks.
compatibility: Core instructions need file read access; write access enables edits and saved evidence, otherwise use inline output. Bundled validation, aggregation, and packaging use Python standard library. Trigger evaluation uses Claude Code CLI; description improvement needs a supported LLM provider. These integrations and isolated-agent evaluation are optional.
license: MIT
metadata:
  purpose: harness-agnostic skill creation methodology
  modes: extract, design, refine
---

# Craft a reusable skill

Write reusable instructions that change agent decisions and verify them against realistic requests. This meta skill is not a routine engineering phase.

## Entry route

- **Inputs:** requested reusable outcome, supplied history or examples, existing skill when relevant, and authorization to assess or edit.
- **First action:** read those inputs and select a mode. Capture completed work → Extract; create future guidance → Design; assess or improve existing guidance → Refine.
- **Stop condition:** deliver the requested assessment, draft, revision, or package with evidence and limits. Missing consequential domain facts keep the affected guidance provisional.

Track inline or in an existing record by default. A requested skill file is the deliverable; an extra plan or spec is a separate artifact. Before adding one, establish both a substantial or resumable need and writing authority. Creating a skill does not automatically require a planning file.

“Assess these skills' triggers without editing” selects assessment-only Refine. “Review the app's code” belongs to code review. Reuse existing answers and preserve the user's execution mode.

## 1. Establish the assignment

1. Read the request, existing skill if any, available examples, corrections, and project instructions. Reuse answers already present; do not begin a fixed interview when the scope is known.
2. Record the repeatable outcome, intended users, adjacent tasks excluded, available capabilities, and requested destination.
3. If a consequential input is missing, ask one focused question and wait before dependent work. Continue independent investigation; do not ask about tools you can inspect directly.
4. Track scope, evidence, changes, and checks in the active same-scope plan or task list. Select any new artifact using the policy below.
5. If the request is a one-time action or a trivial prompt without reusable decisions, explain that and offer the direct task. If the user explicitly wants a reusable skill, proceed within that scope.
6. Select the mode below. State the selected mode briefly; ask for confirmation only when the intended mode changes the work and remains ambiguous.

| Request | Mode | Required result |
| --- | --- | --- |
| Capture work already performed | Extract | Generalized procedure grounded in actual actions and user corrections |
| Create a skill for future work | Design | Scoped procedure with examples, decisions, and observable success conditions |
| Assess or improve an existing skill | Refine | Findings or authorized changes tied to failures or instruction-quality defects |

### Select working artifacts

1. Use the requested or established location and naming convention first. Resume unfinished same-scope work in its existing artifact across sessions. Keep small tasks inline; a new session alone does not justify a new file.
2. Only when both artifact need and writing authority are established, use a written plan for substantial or resumable skill work; the fallback is `.your/plans/YYYY-MM-DD-<descriptive-name>.md`. An authorized consequential design uses `.your/specs/YYYY-MM-DD-<descriptive-name>.md`. Use the creation date and retain it during updates; do not automatically rename existing files or overwrite a namesake.
3. For newly authorized work after task-plan/spec closure, create a linked dated successor when persistence is warranted; preserve the closed record instead of appending another workstream. Update a living canonical spec for authorized contract changes rather than creating competing contracts. Keep active artifacts concise with actionable steps/decisions and evidence links, not transcripts. At closure record outcome, actual acceptance state, and gaps once; checked steps do not close pending required work, evidence, or acceptance.
4. On first authorized use, create only missing directories and `.your/.gitignore` containing `*`. Preserve existing ignore rules. The wildcard also ignores the ignore file; fresh checkouts need local setup again.
5. For versioned collaboration, use the requested tracked location. Do not infer migration or Git authority.
6. For assessment-only, no-file, or no-write work, track inline unless artifact writing is separately authorized. Report required persistence as pending. Keep behavioral evals in their documented schema locations; do not create `.your/tests/` by default.

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
3. If several failures share one cause or the scope is wrong, recommend restructuring the affected workflow. Otherwise identify a focused correction. Apply it only when editing is authorized; do not accumulate unrelated universal rules.
4. For an instruction-quality request without a failed execution, inspect the current procedure against realistic cases. Label those checks as author review, not independent behavioral evaluation.
5. Preserve supported metadata, resource links, scripts, and established contracts unless the correction requires changing them. Inspect callers before removing resources.

## 3. Write the instructions

1. Keep `SKILL.md` frontmatter first, with a lowercase hyphenated `name` matching the folder and a discriminating `description` under 1024 characters. Preserve applicable license, compatibility, and metadata.
2. State what to produce and when the skill applies. Put detailed process in the body, not an exhaustive description.
3. Use numbered steps where order matters. Start steps with actions and name their input or target, expected observation, and next decision when failure is plausible.
4. Write explicit branches for consequential choices: if a prerequisite is missing, how to obtain it; if a check fails, what to investigate; if scope changes, which work to reopen.
5. Keep user authorization and execution mode intact. Do not add mandatory delegation, Git actions, plugins, or redundant approval stops.
6. Keep instructions and generated prose concise without losing context or technical detail. Use bullets for parallel items, checkboxes for tracked actions, numbered steps for required order, and connected prose for explanations. Keep paragraphs unwrapped; add headings/tables only when useful. Make output formats adaptive: omit empty or irrelevant fields, preserve required machine-readable schema fields, and separate internal inspection requirements from written deliverables.
7. Write each fact once in its authoritative location and link supporting evidence. Specs own behavior/decisions; plans own delivery/progress; notes capture new observations; handoffs summarize results and material gaps. Cut repeated summaries, routine process narration, and advice that does not change an action. Preserve constraints, exact contracts/commands, consequential decisions, acceptance, and evidence limits. Include gotchas only for supported failure modes.
8. Keep common instructions in the entrypoint. Move substantial conditional procedures into existing or justified references; link each where it becomes relevant. Do not create extra files to fill a standard layout.
9. Use capability names in core instructions. Put optional provider or harness requirements beside the integrations that actually need them.
10. Check references, examples, command flags, and script paths against their implementation. Present placeholder commands as templates, not runnable commands with invented APIs.

## 4. Validate decisions with realistic cases

1. Choose cases before judging the result: a normal request, a likely failure, and a boundary or neighboring request that should take a different path. Add cases only when another meaningful risk needs coverage.
2. Define observable success for each case, including artifacts and prohibited side effects. For prose, check retained context, decisions, technical detail, executability, and unnecessary repetition. Completion checks establish the promised result; word counts, heading counts, and matching wording do not prove behavior. Prefer the concise complete output; brevity that hides a required detail is a failure.
3. Inspect available execution capabilities and authorization. If the user requests inline work, keep all testing and review inline. Use an isolated agent only when available and authorized; never make delegation a requirement.
4. Apply the draft to the cases in a temporary or otherwise authorized workspace. Capture decisions, outputs, checks, and mistakes. If doing an instruction walkthrough rather than executing a task, label it explicitly.
5. If comparing variants, hold the task, inputs, capabilities, and scoring criteria fixed. Separate independent runs from author walkthroughs influenced by this conversation.
6. Map each failure to a specific instruction. In assessment-only work, report the correction without editing. When revision is authorized, revise and repeat affected cases. Stop when required cases meet their criteria or report a named unresolved limitation.
7. Do not claim improved model performance from metadata validation or an inline review. Report the actual evaluation method and its limits.

- Before writing automated evaluation artifacts, read [JSON schemas](references/schemas.md). Use `assertion_results` in `grading.json`; an incorrectly shaped record cannot establish correctness.
- Load only relevant guidance: [grader](agents/grader.md) for assertions, [comparator](agents/comparator.md) for controlled comparisons, or [analyzer](agents/analyzer.md) for diagnosis. These resources can guide inline review; they do not authorize delegation.

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

1. Run integrations only within authorization and cost constraints. A missing integration does not block core authoring or validation.
2. Treat trigger-evaluator results as temporary Claude command-surrogate measurements, not full-body behavior, catalog competition, or native activation in other harnesses.
3. Keep execution errors unscored. Resolve them before comparing descriptions.
4. Without integrations, review cases manually and disclose that activation remains unmeasured. For direct calls to another model, record the actual protocol and distinguish simulated routing from native activation.

## Completion check

- [ ] Scope and mode match the requested reusable behavior.
- [ ] Ordered actions, consequential branches, evidence records, and completion conditions are explicit.
- [ ] User choices and existing authorization are preserved.
- [ ] Realistic cases have inspected outcomes, with failures resolved or disclosed.
- [ ] Metadata validation and local links pass; referenced helpers match their documented interface.
- [ ] Conditional resources are discoverable without loading irrelevant material.
- [ ] License notices accompany any retained material that requires them.
- [ ] Packaging was inspected if requested; no publication or Git action was inferred.

Return findings or changes, affected paths, and a concise validation summary with material limits; link detailed evidence rather than repeating it. Omit empty report categories. For assessment-only work, state that no paths changed. Distinguish readiness for the requested use from pending model or harness trials. Do not force repeated approval for authorized revisions.
