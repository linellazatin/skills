---
name: opencraft-skill
description: >
  Use this skill when the user wants to create, build, extract, design, write,
  package, or improve an Agent Skill, workflow skill, or reusable skill for any
  domain. Also trigger when the user says things like: "let's capture this as a
  workflow", "make this repeatable", "package this for other agents", "I want my
  agent to always do X", "turn what we just did into something reusable",
  "this skill isn't working", or "how do I write a skill". Trigger even when the
  user does not use the word "skill" directly.
compatibility: >
  Works on any agent harness with file read access. File write access enables the
  working file and skill output; both degrade gracefully to inline output when
  unavailable. Core scripts (quick_validate.py, aggregate_benchmark.py,
  package_skill.py) require Python 3 stdlib only; also runnable via `uv run`.
  run_eval.py and run_loop.py (eval step) require Claude Code CLI (`claude -p`) —
  trigger testing is harness-specific. improve_description.py works with any
  LLM provider: ANTHROPIC_API_KEY, OPENAI_API_KEY, or claude -p fallback.
  Subagent delegation improves eval isolation but is not required.
license: MIT
metadata:
  purpose: harness-agnostic skill creation methodology
  modes: extract, design, refine
---

# opencraft-skill

A harness-agnostic process for creating Agent Skills.

**Bundled scripts** (run with `python3 scripts/<name>.py --help`):
- `scripts/quick_validate.py` — spec-check frontmatter and line count
- `scripts/aggregate_benchmark.py` — aggregate `grading.json` files → `benchmark.json`
- `scripts/package_skill.py` — validate and zip a skill for distribution (stdlib only)
- Claude Code CLI only: `scripts/run_eval.py`, `scripts/run_loop.py`, `scripts/improve_description.py`

**Bundled agents** (load and delegate):
- `agents/grader.md` — grades eval assertions; writes `grading.json`
- `agents/comparator.md` — blind A/B quality judge; writes `comparison.json`
- `agents/analyzer.md` — benchmark patterns and post-hoc improvement suggestions

## How to use this skill

Follow these sections in order. Do not skip sections or combine steps.

1. Set up the working file.
2. Run mode selection.
3. Follow that mode's steps to produce a draft SKILL.md.
4. Run the eval loop.
5. Run description optimization.
6. Run the skill quality checklist.

## Working file

Do these steps before anything else:

1. Ask: "What do you want to make repeatable? Describe it in one sentence."
   Write their answer to context as SKILL_GOAL.
2. Ask: "What should we call this skill? Lowercase and hyphens only,
   e.g. `pdf-analysis`. You can change this later."
   Set SKILL_NAME = that value.
3. Check if file write access is available in the current working directory.
   - If yes: create `skill-plan-<SKILL_NAME>.md` and write:
     ```
     # skill-plan-<SKILL_NAME>
     ## Goal: <SKILL_GOAL>
     ## Session started: <date>
     ## Mode: TBD
     ```
   - If no file write access: tell the user "I'll track the plan inline in
     our conversation instead." Then maintain it as a running summary.
4. Update the working file at the end of every major section.

## Mode selection

**First, decide whether a skill is the right output at all.**

Do not build a skill if any of these are true — tell the user and stop:
- The task is a one-time action the user does not intend to repeat.
- The workflow changes so frequently that a written skill would be stale
  within a week. (Exception: build it anyway if the user says they will
  actively maintain it.)
- The task is trivial enough that a one-sentence prompt handles it every time.

If any of the above apply, say: "This might not need a skill yet — [reason].
Want to proceed anyway, or is this a one-off?"
- If they say proceed: continue to routing below.
- If they say one-off: stop here and help them complete the task directly.

**Route to a mode.** Ask:

> "Tell me what you want to build or capture."

Read their answer and route as follows — do not ask them to self-classify:

- They describe something they just finished doing, or want to capture a
  workflow from earlier in this conversation: go to **Mode 1: Extract**.
- They describe something they want to build for future use and have not done
  it yet: go to **Mode 2: Design**.
- They describe an existing skill that is misbehaving or underperforming:
  go to **Mode 3: Refine**.
- If unclear: ask "Did you just finish doing the thing this skill would do,
  do you have an existing skill that needs improvement, or are you planning
  something new?" — then route based on answer.

Confirm before proceeding: "Sounds like [mode] — [one sentence]. Does that
sound right?" Write the confirmed mode to the working file under `## Mode:`.

## Mode 1: Extract

Use when the user just completed a workflow and wants to capture it.

### Step 1 — Read history (the what)

Read the current conversation from the beginning. Extract and write down:
- The sequence of steps taken
- Capabilities used — describe them generically ("read a file", "ran a command",
  "searched the web"), not by harness-specific tool names
- Input formats (what did the data or files look like going in?)
- Output formats (what did the result look like?)
- Any corrections the user made ("use X instead of Y", "don't do Z")
- Context the user had to provide that the agent did not know on its own

Do not ask the user to repeat anything already visible in the history.
Summarize — do not quote verbatim. Write to the working file under
`## History summary`.

### Step 2 — Interview for the why

Ask these questions **one at a time**. Send ONE question. Wait for the answer.
Write it to the working file. Then send the next question. Do not batch them.

- Q1: "What were you ultimately trying to achieve? (Not the steps — the goal)"
- Q2: "Was the approach we took the one you'd want to use every time, or did
  you make any compromises you'd rather avoid in future?"
- Q3: "What should stay specific to this instance vs. what should generalize?
  Were the file names / column names / API endpoints specific to today, or
  should the skill work for any similar input?"
- Q4: "Are there edge cases or failure modes you already know about that didn't
  come up in what we just did?"
- Q5: "Is there anything the agent consistently gets wrong in this domain that
  the skill should explicitly call out?"

If any answer reveals a constraint or gotcha, flag it: "That sounds like a
gotcha — I'll put it in the draft."

### Step 3 — Draft the SKILL.md

Using the history summary and the answers from Step 2, write a draft SKILL.md.

Rules for the draft:
- Teach the **reusable pattern**, not the specific instance. Replace specific
  file names, column names, or values with placeholders.
- Include a `## Gotchas` section for every edge case or failure mode mentioned.
  Each gotcha is one concrete, specific bullet — not general advice.
- If the user described a specific output format, include a template inline if
  short. For longer templates, write to `<SKILL_NAME>/assets/` and reference
  from SKILL.md.
- If there is a multi-step sequence that must be followed in order, use a
  numbered list. Use prose for background context only.
- Keep the body under 500 lines. Apply this split when content is long:
  **main body** = what to do and how to decide at each step.
  **references/** = why, lookup tables, checklists for sub-cases, long examples.
  Move a block to references/ when it only applies to some runs of the skill.
- Write for any agent harness. Do not name harness-specific tools. Write the
  capability instead: "read the file" not "use the Read tool"; "run a terminal
  command" not "use Bash".

Write the draft to `<SKILL_NAME>/SKILL.md` (or inline if no write access).

The file MUST open with a YAML frontmatter block. Required: `name` and
`description`. Include `license` if the user's project has one:

```
---
name: <SKILL_NAME>
description: Use this skill when...
---
```

Do not omit the frontmatter. Do not place any text before the opening `---`.

Write a one-line summary to the working file under `## Draft v1`.

### Step 4 — Review draft with user

Show the draft (or the path to it) and ask:
"Does this capture the right pattern? Check:
- Does the approach generalize, or is it too specific to what we just did?
- Are the gotchas accurate?
- Anything missing that the agent would need to know?"

Collect feedback. Revise and ask again if needed. When the user says it looks
right, write `Draft approved` to the working file and proceed to **Eval loop**.

## Mode 2: Design

Use when the user wants to build a skill for something they have not done yet.

### Step 1 — Scope the skill

Before collecting material, ask these two questions **one at a time**:

1. "What does this skill do — and what does it explicitly NOT cover? Name at
   least one adjacent task that should stay separate from this skill."
2. "Who or what will use this skill — a single person, a team, or automated
   agents running without a human in the loop?"

Write answers to the working file under `## Scope`. Then ask for material:

Ask: "Do you have anything useful to share? Runbooks, past examples, known gotchas,
corrections from when agents tried this before, or naming/API conventions."

Wait for the user's response. Do not proceed until they answer.

- If they provide material: go to **Step 2 — Draft with material**.
- If they say they have nothing: ask once more before accepting it:
  "Before we use a generic baseline — describe one time you did this task
  manually, even roughly. Even a short story gives us real gotchas."
  Wait for their answer.
  - If they provide something now: go to **Step 2 — Draft with material**.
  - If they still have nothing: go to **Step 3 — Generic baseline**.

### Step 2 — Draft with material

Read all material the user provided. Then ask these questions **one at a
time**. Send ONE question, wait for the answer, write it to the working file,
then send the next. Do not batch them.

- Q1: "What does success look like — what should the agent produce or do?"
- Q2: "What is the most common way this goes wrong?"
- Q3: "Are there steps that must happen in a specific order, or that are easy
  to skip by mistake?"
- Q4: "Any tools, libraries, or commands the agent should always use (or avoid)?"
- Q5: "What would you correct if an agent did this task but got it slightly wrong?"
- Q6: "Are there things the agent reliably gets wrong in this domain even with no
  special guidance? Those become Gotchas entries."

Write the draft following the same rules as Mode 1 Step 3.
Write to `<SKILL_NAME>/SKILL.md` (or inline if no write access).

The file MUST open with a YAML frontmatter block:

```
---
name: <SKILL_NAME>
description: Use this skill when...
---
```

Do not omit the frontmatter. Do not place any text before the opening `---`.

Write `Draft v1 — from real material` to the working file.

### Step 3 — Generic baseline (fallback)

Tell the user:
> "We'll draft a skeleton with explicit markers where real expertise is needed.
> These markers must be replaced before the skill is reliable."

Write the draft (must open with YAML frontmatter — same format as Step 2 above).

Mark every section that needs real expertise with:

```
<!-- [GENERIC BASELINE] Replace this with: <what is needed here> -->
```

Examples:
- `Replace this with: the actual error codes this API returns`
- `Replace this with: your team's naming convention for output files`
- `Replace this with: known edge cases in this data format`

Write `Draft v1 — generic baseline, N placeholders` to the working file.

### Step 4 — Review draft with user

Show the draft and ask:
"Does this look like the right shape? Check:
- Does the approach match how you would actually do this?
- Are the `[GENERIC BASELINE]` markers in the right places?
- Anything the agent would definitely need that is not here?"

Collect feedback. Revise and ask again if needed. When the user approves,
write `Draft approved` and proceed to **Eval loop**.

## Mode 3: Refine

Use when the user has an existing skill that is misbehaving or underperforming.

Ask the user these questions **one at a time**. Write answers to the working
file under `## Refine inputs`.

1. "What is the skill doing wrong? Describe a specific case — what prompt,
    what output, what should have happened instead."
2. "Is this a one-off failure or does it happen consistently?"
3. "Do you have eval results or execution transcripts from failed runs?"

**Diagnose before proposing changes.** For each failure, identify root cause:

- Instructions too vague → tighten with a concrete example or constraint
- Instructions that don't apply to this task → scope or split into a separate skill
- Too many options without a clear default → add "if unsure, do X"
- Missing gotcha → add it to the Gotchas section
- Description triggering on wrong prompts → route to description optimization

**Before patching anything, count how many failures share the same root cause.**
- If 3 or more failures share the same root cause, or if the skill's scope or
  approach appears fundamentally wrong: do NOT patch. Instead say: "These
  failures suggest restructuring — [specific change]. Want to proceed with that?"
  - If yes: treat the existing SKILL.md as source material and go to Mode 2 Step 1.
  - If no: then patch, but note the risk in the working file.
- If failures are independent: patch each one.

For each patch, show before/after. Ask: "Here is what I would change. Anything
you would do differently?" Apply approved changes, then proceed to **Eval loop**.

## Eval loop

Run after the draft is approved, before description optimization.

### Capability check

Ask these two questions **one at a time** before setting up any evals:

1. "Can you spawn isolated sub-tasks or subagents in this environment?
    (Yes / No / Not sure)"
2. "Do you have file write access in the current working directory?
    (Yes / No)"

- If Q1 = Yes: follow **Path A**.
- If Q1 = No or Not sure: follow **Path B**.

Record answers in the working file under `## Eval capability`.

### Designing test cases

Write 2–3 test prompts before running evals on either path. Each must be:
- A realistic user message — the kind of thing someone would actually type
- Specific enough to verify (not "process this data")
- Varied: at least one casual phrasing, one precise phrasing, one edge case

Weak: "process my sales data" — no verifiable success criteria.
Strong: "my boss wants the top 3 months by revenue from data/sales.csv as
a bar chart" — specific, verifiable, realistic.

If the user cannot think of test prompts, generate 3 candidates based on the
skill's goal and ask: "Do these look realistic, or would you change any?"

For each prompt, write one sentence describing what success looks like.
Ask: "Do these test prompts look right, or would you add or change any?"
Save to the working file under `## Test prompts`.

### Path A — subagents available

Each run must start with a clean context — no leftover state from prior runs.

For each test prompt, run two tasks **in the same turn**:

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
1. For each eval, load `agents/grader.md` and spawn a grader subagent with the
   assertions list and the eval's output dirs. Read `references/schemas.md` before
   writing grading.json — wrong field names cause silent failures in
   aggregate_benchmark.py. If subagents are unavailable, grade inline using the
   rules in `agents/grader.md`.
   Optional: load `agents/comparator.md` for qualitative A/B comparison; writes
   `comparison.json` alongside grading.json.
2. Run:
   ```
   python3 scripts/aggregate_benchmark.py <SKILL_NAME>-workspace/iteration-1 \
     --skill-name <SKILL_NAME>
   # or: uv run scripts/aggregate_benchmark.py ...
   ```
   This writes `benchmark.json` with pass rates, tokens, and the skill delta.
3. Ask: "Here are the results. Does the skill output look right? Anything you
   would change about what it produced?"

Collect feedback. Write it to `## Iteration 1 results` in the working file.

### Path B — inline fallback

Tell the user (do not skip this notice):

> "Without isolated subagents, the recommended approach is a fresh session —
> start a new conversation with the skill installed and run each test prompt
> there. This gives clean context and results you can trust.
>
> If a fresh session is not available, we can run inline here instead, but
> treat those results as directional only — the full context of this session
> will influence the output."

For each test prompt:
1. If a fresh session is available: start one, install the skill, run the
   prompt, note the output, return here.
2. If running inline: read the draft SKILL.md, apply its instructions to
   complete the test prompt, then show the output to the user.
3. Ask: "Does this look right? Thumbs up or down, and any notes?"

Write results to the working file under `## Iteration 1 results` with: prompts
run, path used (B — fresh session or inline), and thumbs up/down + notes per
prompt.

### Reading results and iterating

After collecting results from Path A or B:

1. List every issue found — be specific. "Output was too verbose" is not
   specific. "The agent included three paragraphs before the result, when
   the skill instructs giving the result first" is specific.
2. For each issue, identify which instruction (or missing instruction) caused it.
3. Propose a specific change for each issue. Show before/after.
4. Ask: "Here is what I would change. Anything you would do differently?"
5. Apply approved changes.
6. Update the working file:
   ```
   ## Iteration N
   - Issues found: [list]
   - Changes made: [before/after summary per change]
   ```
7. If changes were made, rerun from **Designing test cases**, incrementing N.
   Use the same test prompts unless the user requests new ones.
8. Stop iterating when:
   - The user says they are satisfied, OR
   - All test prompts pass their success criteria, OR
   - Two consecutive iterations produce no changes.

Proceed to **Scripts (optional)**.

## Scripts (optional)

Run after the eval loop, before description optimization.

Ask:
> "Does this skill include static steps — like fixed transformations, validation
> checks, or commands that run the same way every time?"

- If no: write `No scripts` to the working file and proceed to
  **Description optimization**.
- If yes: **stop and read `references/scripts.md` in full before continuing.**
  It defines three types (Command, Script, Validator) and authoring rules.

Ask: "Which type best describes what you have in mind? (Name more than one
if needed.)" Then for each candidate, follow `references/scripts.md` in order:
confirm type, select language, apply authoring rules, run the per-type checklist.

Write the script to `<SKILL_NAME>/scripts/<scriptname>`. Reference it from the
relevant step in SKILL.md with the exact run command. Record in the working file:
```
## Scripts
- <filename>: <type> — <one-line description>
```

Proceed to **Description optimization**.

## Description optimization

Run after the eval loop is complete.

**If Claude Code CLI available** (`claude -p "hi" --output-format text` exits 0):
```
python3 scripts/run_loop.py --skill-path <SKILL_NAME>/ \
  --eval-set <evals.json> --model <model> \
  --holdout 0.4 --max-iterations 5 --verbose
```
Apply the best description, then skip to **Skill quality checklist**.
**If no Claude Code but LLM API available** (ANTHROPIC_API_KEY or OPENAI_API_KEY set):
Read `references/description-optimization.md` for manual testing. After each round, run
`python3 scripts/improve_description.py --eval-results <failures.json> --skill-path
<SKILL_NAME>/ --model <model>` to rewrite the description. Apply and repeat (up to 5×).
**Otherwise:** read and follow `references/description-optimization.md` in full.

## Packaging

Run `python3 scripts/package_skill.py <SKILL_NAME>/ [output-dir]` to produce a
distributable `<SKILL_NAME>.skill` file (excludes evals/, build artifacts; stdlib only).

## Skill quality checklist

Run this on the completed SKILL.md before telling the user the skill is done.
Fix every failing item — do not skip any.

- [ ] SKILL.md opens with a YAML frontmatter block (`---` delimiters present,
      no text before the opening `---`)
- [ ] `name` field present, matches directory name exactly (lowercase, hyphens
      only, no consecutive hyphens, no leading or trailing hyphens)
- [ ] `description` field present
- [ ] Description starts with "Use this skill when..." (imperative, user-intent)
- [ ] Description covers user intent keywords, not just implementation terms
- [ ] Description is under 1024 characters
- [ ] Body is under 500 lines
- [ ] No instruction names a harness-specific tool — only capabilities described
- [ ] Every instruction answers: "Would the agent get this wrong without this?"
      Cut any instruction where the answer is no.
- [ ] Every decision point is an explicit fork: "If X, do Y. If not X, do Z."
      No decision left to inference.
- [ ] Gotchas section present if any non-obvious failure modes were mentioned
- [ ] Output format templated if the skill produces structured output
- [ ] No instructions apply only to the specific instance used during creation
- [ ] All `[GENERIC BASELINE]` markers removed or replaced with real content
- [ ] Working file `skill-plan-<name>.md` is complete and up to date
- [ ] If scripts were added: each has passed its per-type checklist
- [ ] If scripts were added: each referenced from SKILL.md with exact run command
- [ ] If a Validator was added: SKILL.md has explicit "if this fails, do X"
- [ ] If no scripts were added: `scripts/` directory does not exist
- [ ] Run `python3 scripts/quick_validate.py <SKILL_NAME>/` (or `uv run`); fix every reported error
- [ ] If distributing: run `python3 scripts/package_skill.py <SKILL_NAME>/`; must exit 0

When all items pass, tell the user:
> "The skill is ready. It lives at `<SKILL_NAME>/SKILL.md`. Try a prompt from
> the test checklist to confirm it activates. One final test before calling
> it done."
