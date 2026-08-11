---
name: opencraft-skill
description: >
  Create, extract, and refine Agent Skills that work across any agent harness.
  Use this skill when the user wants to build a new skill from scratch, turn a
  workflow they just completed into a reusable skill, improve an existing skill,
  or needs guidance on skill structure, descriptions, or evals. Use it even if
  the user doesn't say "skill" explicitly — trigger when they say things like
  "let's capture this as a workflow", "make this repeatable", "how do I package
  this for other agents", or "I want my agent to always do X this way."
compatibility: >
  Works on any agent harness with file read access. File write access enables the
  working file and skill output; both degrade gracefully to inline output when
  unavailable. No executable scripts bundled. Subagent delegation improves eval
  isolation but is not required.
license: MIT
metadata:
  purpose: harness-agnostic skill creation methodology
  modes: extract, design, refine
---

# opencraft-skill

A harness-agnostic process for creating Agent Skills. Works in any agent
environment. No scripts or tooling required — only file read access.

## How to use this skill

Follow these sections in order. Each section tells you exactly what to do.
Do not skip sections or combine steps — smaller steps produce better results.

1. Set up the working file (next section).
2. Run mode selection to determine which path to follow.
3. Follow that mode's steps to produce a draft SKILL.md.
4. Run the eval loop on the draft.
5. Run description optimization.
6. Run the skill quality checklist before handing off.

## Working file

At the start of every session using this skill, do the following:

1. Ask the user: "What will we name this skill?" (lowercase, hyphens only,
   e.g. `pdf-analysis`)
2. Set SKILL_NAME = that name.
3. Check if file write access is available in the current working directory.
   - If yes: create `skill-plan-<SKILL_NAME>.md` and write the header:
     ```
     # skill-plan-<SKILL_NAME>
     ## Session started: <date>
     ## Mode: TBD
     ```
   - If no file write access: tell the user "I'll maintain the plan inline
     in our conversation instead."
4. Update the working file at the end of every major section.

## Mode selection

Ask the user exactly this question (do not rephrase):

> "Are we (1) turning something you just did into a skill,
>  (2) designing a new skill from scratch, or
>  (3) improving an existing skill based on how it's been performing?"

- If they answer 1 or indicate they just completed a workflow: go to
  **Mode 1: Extract**.
- If they answer 2 or describe something they want to build: go to
  **Mode 2: Design**.
- If they answer 3 or describe a skill that isn't working well: go to
  **Mode 3: Refine**.
- If unclear: ask "Did you just finish doing the thing this skill would do,
  do you have an existing skill to improve, or are we planning it out fresh?"
  — then route based on answer.

Write the chosen mode to the working file under `## Mode:`.

## Mode 1: Extract

Use this mode when the user just completed a workflow and wants to capture it.

### Step 1 — Read history (the what)

Read back through the current conversation. Extract and write down:
- The sequence of steps taken
- Tools or commands used
- Input formats (what did the data/files look like going in?)
- Output formats (what did the result look like?)
- Any corrections the user made ("use X instead of Y", "don't do Z")
- Context the user had to provide that the agent didn't know on its own

Do not ask the user to repeat anything already visible in the history.
Summarize — do not quote verbatim — to keep the working file concise.
Write this summary to the working file under `## History summary`.

### Step 2 — Interview for the why

Ask the user these questions **one at a time**. Wait for each answer before
asking the next. Write each answer to the working file.

1. "What were you ultimately trying to achieve? (Not the steps — the goal)"
2. "Was the approach we took the one you'd want to use every time, or did
    you make any compromises you'd rather avoid in future?"
3. "What should stay specific to this instance vs. what should generalize?
    For example, were the file names / column names / API endpoints specific
    to today, or should the skill work for any similar input?"
4. "Are there edge cases or failure modes you already know about that didn't
    come up in what we just did?"
5. "Is there anything the agent consistently gets wrong in this domain that
    the skill should explicitly call out?"

If any answer reveals a constraint or gotcha, flag it: "That sounds like a
gotcha worth putting in the skill — I'll make sure it's in the draft."

### Step 3 — Draft the SKILL.md

Using the history summary and the answers from Step 2, write a draft SKILL.md.

Rules for the draft:
- The skill body teaches the **reusable pattern**, not the specific instance.
  Replace specific file names, column names, or values with placeholders or
  instructions like "read the schema to find relevant tables".
- Include a `## Gotchas` section for every edge case or failure mode the
  user mentioned. Each gotcha is one concrete, specific bullet — not general
  advice ("handle errors appropriately" is not a gotcha).
- If the user described a specific output format, include a template inline if
  it is short. For longer templates, write the file to `<SKILL_NAME>/assets/`
  and reference it from SKILL.md.
- If there is a multi-step sequence that must be followed in order, use a
  numbered checklist.
- Keep the body under 500 lines. If it is getting long, move detail to
  `references/` files loaded on demand.

Write the draft to `<SKILL_NAME>/SKILL.md` in the current working directory
(or show it inline if no file write access).

The file MUST open with a YAML frontmatter block. Required fields are `name`
and `description`. Include `license` if the user's project has a license.
Write it exactly:

```
---
name: <SKILL_NAME>
description: <description — imperative, starting with "Use this skill when...">
---
```

Do not omit the frontmatter. Do not place any text before the opening `---`.

Write a one-line summary of the draft to the working file under `## Draft v1`.

### Step 4 — Review draft with user

Show the user the draft (or the path to it) and ask:
"Does this capture the right pattern? A few things to check:
- Does the approach generalize, or is it too specific to what we just did?
- Are the gotchas accurate?
- Anything missing that the agent would need to know?"

Collect feedback. If changes are needed, revise and ask again.
When the user says it looks right, write `Draft approved` to the working file
and proceed to **Eval loop**.

## Mode 2: Design

Use this mode when the user wants to build a skill for something they have
not done yet, or want to systematize going forward.

### Step 1 — Solicit domain expertise

Say to the user:

> "Effective skills rely on practical experience with edge cases, failure modes, and corrections—not generic instructions.
>  It is recommended that you specify things, like you're telling a detailed story.
>
>  Do you have any of the following you can share?
>  - A runbook, checklist, or internal doc for this workflow
>  - A past example of this task done well (or badly)
>  - Known gotchas or edge cases in this domain
>  - Corrections you have had to make when an agent tried this before
>  - Any project-specific conventions (naming, file structure, API patterns)"

Wait for the user's response. Do not proceed until they answer.

- If they provide material: go to **Step 2 — Draft with material**.
- If they say they have no material or want to proceed anyway: go to
  **Step 3 — Generic baseline**.

### Step 2 — Draft with material

Read all material the user provided. Then ask these questions **one at a
time** before drafting (write each answer to the working file):

1. "What does success look like — what should the agent produce or do?"
2. "What is the most common way this goes wrong?"
3. "Are there steps that must happen in a specific order, or that are easy
    to skip by mistake?"
4. "Any tools, libraries, or commands the agent should always use (or avoid)?"
5. "What would you correct if an agent did this task but got it slightly wrong?"
6. "Are there things the agent reliably gets wrong in this domain even with no
    special guidance? Those become Gotchas entries."

Then write the draft SKILL.md following the same rules as Mode 1 Step 3:
reusable pattern, gotchas section, `assets/` for complex output templates,
checklist for ordered sequences, under 500 lines.

Write the draft to `<SKILL_NAME>/SKILL.md` (or inline if no file write access).

The file MUST open with a YAML frontmatter block. Required fields are `name`
and `description`. Include `license` if the user's project has a license:

```
---
name: <SKILL_NAME>
description: <description — imperative, starting with "Use this skill when...">
---
```

Do not omit the frontmatter. Do not place any text before the opening `---`.

Write `Draft v1 — from real material` to the working file.

### Step 3 — Generic baseline (fallback)

If the user has no material and wants to proceed anyway:

Tell the user:
> "We'll start with a concrete draft highlighting missing specific details, which must be filled before the skill is reliable."

Write the draft SKILL.md. The file MUST open with a YAML frontmatter block:

```
---
name: <SKILL_NAME>
description: <description — imperative, starting with "Use this skill when...">
---
```

Do not omit the frontmatter. Do not place any text before the opening `---`.

Mark every section that needs real expertise with:

```
<!-- [GENERIC BASELINE] Replace this with: <what is needed here> -->
```

Examples of what to put in the placeholder:
- `Replace this with: the actual error codes this API returns`
- `Replace this with: your team's naming convention for output files`
- `Replace this with: known edge cases in this data format`

Write `Draft v1 — generic baseline, N placeholders` to the working file,
where N is the count of `[GENERIC BASELINE]` markers.

### Step 4 — Review draft with user

Show the user the draft and ask:
"Does this look like the right shape? A few things to check:
- Does the approach match how you would actually do this?
- Are the `[GENERIC BASELINE]` markers in the right places?
- Anything the agent would definitely need to know that is not here?"

Collect feedback. Revise and ask again if needed.
When the user says it looks right, write `Draft approved` to the working file
and proceed to **Eval loop**.

## Mode 3: Refine

Use this mode when the user has an existing skill and wants to improve it based
on observed failures, agent feedback, or eval results.

Read the existing `SKILL.md`. Ask the user three questions one at a time:

1. "What is the skill doing wrong? Describe a specific case — what prompt,
    what output, what should have happened instead."
2. "Is this a one-off failure or does it happen consistently?"
3. "Do you have eval results or execution transcripts from failed runs?"

Write answers to the working file under `## Refine inputs`. Then for each
failure, identify which instruction (or missing instruction) caused it. Common
causes: instructions too vague, instructions that don't apply to the current
task, too many options without a clear default, missing gotcha, or description
triggering on wrong prompts (route that last one to description optimization).

For each diagnosed issue, propose a specific change with before/after. Ask:
"Here is what I would change. Anything you would do differently?" Apply approved
changes, then proceed to **Eval loop** to verify improvements.

## Eval loop

Run this section after the draft is approved, before description optimization.

### Capability check

Ask the user these two questions **before** setting up any evals:

1. "Can you spawn isolated sub-tasks or subagents in this environment?
    (Yes / No / Not sure)"
2. "Do you have file write access in the current working directory?
    (Yes / No)"

- If Q1 = Yes: follow **Path A**.
- If Q1 = No or Not sure: follow **Path B**.
- Record answers in the working file under `## Eval capability`.

### Designing test cases

Before running evals on either path, write 2–3 test prompts with the user.
Each test prompt must be:
- A realistic user message — the kind of thing someone would actually type
- Specific enough to be verifiable (not "process this data")
- Varied: at least one casual phrasing, one precise phrasing, one edge case

Weak: "process my sales data" — no verifiable success criteria.
Strong: "my boss wants the top 3 months by revenue from data/sales.csv as
a bar chart" — specific, verifiable, realistic.

For each prompt, write one sentence describing what success looks like.

Ask the user: "Here are the test prompts I would use. Do these look right,
or would you add or change any?"

Save test prompts to the working file under `## Test prompts`.

### Path A — subagents available

Each run must start with a clean context — no leftover state from prior runs.
In environments with subagents, each child task starts fresh naturally.

For each test prompt, spawn two runs **in the same turn**:

Run 1 — with skill:
```
Task: <test prompt>
Skill: <path to SKILL_NAME/SKILL.md>
Save outputs to: <SKILL_NAME>-workspace/iteration-1/eval-<N>/with_skill/
```

Run 2 — without skill (baseline):
```
Task: <same test prompt>
No skill.
Save outputs to: <SKILL_NAME>-workspace/iteration-1/eval-<N>/without_skill/
```

After both complete:
1. Compare outputs side by side.
2. For each test case, write to the working file:
   - Did the with-skill output meet the success criteria? (Yes / Partially / No)
   - What was specifically better or worse vs. baseline?
   - Any instructions in the skill that seemed ignored or misapplied?
3. Ask the user: "Here are the results. Does the skill output look right?
    Anything you would change about what it produced?"

Collect feedback. Write it to `## Iteration 1 results` in the working file.

### Path B — inline fallback

Tell the user the following before proceeding (do not skip this notice):

> "Note: Without isolated subagents, the recommended approach is a fresh session —
> start a new conversation with the skill installed and run each test prompt there.
> This gives clean context and results you can trust.
>
> If your environment does not support fresh sessions, you can run inline in this
> session instead, but treat the results as directional only — full context from
> this session will influence the output."

For each test prompt:
1. If a fresh session is available: start one, install the skill, run the prompt,
   note the output, return here.
2. If running inline: read the draft SKILL.md, apply its instructions to complete
   the test prompt in this session, then show the output to the user.
3. Ask: "Does this look right? Thumbs up or down, and any notes?"

Write each result to the working file under `## Iteration 1 results`:
```
## Iteration 1
- Test prompts run: [list]
- Path used: B (fresh session / inline)
- Results: [thumbs up/down + user notes per prompt]
```

### Structured evals (optional)

For teams that want repeatable benchmarks: the Agent Skills standard defines a
structured eval format. After recording test prompts, offer to scaffold
`evals/evals.json` with `id`, `prompt`, and `expected_output` per test case. Add
`assertions` after the first round of results. Save grading to
`<SKILL_NAME>-workspace/iteration-N/eval-<id>/grading.json`.

### Reading results and iterating

After collecting results from Path A or B:

1. List every issue found — be specific. "Output was too verbose" is not
   specific. "The agent included three paragraphs of explanation before the
   result, when the skill instructs giving the result first" is specific.
2. For each issue, identify which instruction (or missing instruction) caused it.
   Also read execution transcripts if available — wasted steps usually mean
   instructions are too vague, don't apply to the current task, or present too
   many options without a clear default.
3. Propose a specific change to the SKILL.md for each issue. Show before/after.
4. Ask the user: "Here is what I would change. Anything you would do differently?"
5. Apply approved changes.
6. Update the working file:
   ```
   ## Iteration N
   - Issues found: [list]
   - Changes made: [before/after summary per change]
   ```
7. If changes were made, rerun the eval loop from **Designing test cases**,
   incrementing the iteration number. Use the same test prompts unless the
   user requests new ones.
8. Stop iterating when:
   - The user says they are satisfied, OR
   - All test prompts pass their success criteria, OR
   - Two consecutive iterations produce no changes.

Proceed to **Scripts (optional)**.

## Scripts (optional)

Run this section after the eval loop, before description optimization.

Ask the user:
> "Does this skill include static steps - like fixed transformations, validation checks, or commands?"

- If no: write `No scripts` to the working file and proceed to
  **Description optimization**.
- If yes: present the three categories below and ask which applies.
  A skill can have more than one type — handle each candidate in turn.

**Category definitions:**

- **Command** — a tool that already exists on the system, invoked inline
  in SKILL.md instructions. No file to write or bundle.
  Example: `uvx ruff@0.8.0 check .`

- **Script** — reusable logic that does not exist yet, bundled in `scripts/`.
  Runs every time the relevant skill step runs.
  Example: a custom data transformer, a report generator, a chart builder.

- **Validator** — a script that checks the agent's own work at a specific
  step and gates progression. Returns pass/fail with a message the agent
  acts on before continuing.
  Example: `scripts/validate_fields.py` that confirms required fields are
  present before the form-filling step runs.

Ask: "Which of these best describes what you have in mind?
      (You can name more than one.)"

For each script candidate the user names:
1. Read `references/scripts.md` in full.
2. Follow the sections in order: identify the type, select a language,
   apply the authoring rules, then run the checklist for that type.
3. Write the script to `<SKILL_NAME>/scripts/<scriptname>` and reference
   it from the relevant step in SKILL.md with the exact run command.
4. Record each script in the working file under `## Scripts`:
   ```
   ## Scripts
   - <filename>: <type> — <one-line description>
   ```

When all script candidates are handled, proceed to
**Description optimization**.

## Description optimization

The description field is what determines whether an agent activates the skill.
Run this section after the eval loop is complete.

Read `references/description-optimization.md` and follow its sections in order.

## Skill quality checklist

Run this checklist on the completed SKILL.md before telling the user the skill
is done. Fix any item that fails — do not skip items.

- [ ] SKILL.md opens with a YAML frontmatter block (the `---` delimiters are
      present and no text appears before the opening `---`)
- [ ] Frontmatter contains `name` field matching the directory name exactly
      (lowercase, hyphens only, no consecutive hyphens, no leading or trailing
      hyphens)
- [ ] Frontmatter contains `description` field
- [ ] Description uses imperative phrasing ("Use this skill when...")
- [ ] Description covers user intent keywords, not just implementation terms
- [ ] Description is under 1024 characters
- [ ] Body is under 500 lines
- [ ] Every instruction answers: "Would the agent get this wrong without this?"
      Cut any instruction where the answer is no.
- [ ] Every decision point is an explicit fork: "If X, do Y. If not X, do Z."
      No decision is left to inference.
- [ ] Gotchas section is present if the user mentioned any non-obvious failure modes
- [ ] Output format is templated if the skill produces structured output
- [ ] No instructions apply only to the specific instance used during creation —
      all instructions must generalize to future uses of the skill
- [ ] All `[GENERIC BASELINE]` markers are removed or replaced with real content
- [ ] Working file `skill-plan-<name>.md` is complete and up to date
- [ ] If scripts were added: each script has passed its per-type checklist
- [ ] If scripts were added: every script referenced from SKILL.md with exact run command
- [ ] If a Validator was added: SKILL.md has explicit "if this fails, do X" at the guarded step
- [ ] If no scripts were added: scripts/ directory does not exist
- [ ] Run `skills-ref validate <SKILL_NAME>/` if the tool is available; fix any reported errors

When all items pass, tell the user:
> "The skill is ready. It lives at `<SKILL_NAME>/SKILL.md`. Try a prompt from the test checklist to confirm
>  it activates. Now's your chance to check and test your SKILL to enhance it even further."
