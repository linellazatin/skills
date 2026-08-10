# Optimizing Skill Descriptions

> Source: https://agentskills.io/skill-creation/optimizing-descriptions.md

How to improve your skill's description so it triggers reliably on relevant prompts.

A skill only helps if it gets activated. The `description` field in your `SKILL.md` frontmatter is the primary mechanism agents use to decide whether to load a skill for a given task. An under-specified description means the skill won't trigger when it should; an over-broad description means it triggers when it shouldn't.

---

## How Skill Triggering Works

Agents use progressive disclosure to manage context. At startup, they load only the `name` and `description` of each available skill — just enough to decide when a skill might be relevant. When a user's task matches a description, the agent reads the full `SKILL.md` into context and follows its instructions.

**The description carries the entire burden of triggering.**

One important nuance: agents typically only consult skills for tasks that require knowledge or capabilities beyond what they can handle alone. A simple, one-step request like "read this PDF" may not trigger a PDF skill even if the description matches perfectly — because the agent can handle it with basic tools. Tasks that involve specialized knowledge, unfamiliar APIs, domain-specific workflows, or uncommon formats are where a well-written description makes the difference.

---

## Writing Effective Descriptions

Before testing, know what a good description looks like:

- **Use imperative phrasing.** Frame the description as an instruction: "Use this skill when..." rather than "This skill does..." The agent is deciding whether to act, so tell it when to act.
- **Focus on user intent, not implementation.** Describe what the user is trying to achieve, not the skill's internal mechanics.
- **Err on the side of being pushy.** Explicitly list contexts where the skill applies, including cases where the user doesn't name the domain directly: "even if they don't explicitly mention 'CSV' or 'analysis.'"
- **Keep it concise.** A few sentences to a short paragraph — long enough to cover the skill's scope, short enough that it doesn't bloat the agent's context. Hard limit: **1024 characters**.

---

## Designing Trigger Eval Queries

To test triggering, you need eval queries — realistic user prompts labeled with whether they should or shouldn't trigger your skill.

```json
[
  {
    "query": "I've got a spreadsheet in ~/data/q4_results.xlsx with revenue in col C and expenses in col D — can you add a profit margin column and highlight anything under 10%?",
    "should_trigger": true
  },
  {
    "query": "whats the quickest way to convert this json file to yaml",
    "should_trigger": false
  }
]
```

**Aim for about 20 queries: 8–10 that should trigger and 8–10 that shouldn't.**

### Should-Trigger Queries

Vary them along several axes:

- **Phrasing**: some formal, some casual, some with typos or abbreviations
- **Explicitness**: some name the skill's domain directly ("analyze this CSV"), others describe the need without naming it ("my boss wants a chart from this data file")
- **Detail**: mix terse prompts with context-heavy ones
- **Complexity**: vary the number of steps; include single-step tasks alongside multi-step workflows

The most useful should-trigger queries are ones where the skill would help but the connection isn't obvious from the query alone.

### Should-Not-Trigger Queries

The most valuable negative test cases are **near-misses** — queries that share keywords or concepts with your skill but actually need something different.

For a CSV analysis skill:

**Weak negatives** (too easy — obviously irrelevant):
- "Write a fibonacci function"
- "What's the weather today?"

**Strong negatives** (near-misses — test precision):
- "I need to update the formulas in my Excel budget spreadsheet" — shares "spreadsheet" and "data" but needs Excel editing, not CSV analysis
- "can you write a python script that reads a csv and uploads each row to our postgres database" — involves CSV, but the task is database ETL, not analysis

### Tips for Realism

Real user prompts contain context generic test queries lack. Include:
- File paths (`~/Downloads/report_final_v2.xlsx`)
- Personal context ("my manager asked me to...")
- Specific details (column names, company names, data values)
- Casual language, abbreviations, occasional typos

---

## Testing Whether a Description Triggers

Run each query through your agent with the skill installed and observe whether the agent invokes it. The skill triggered if the agent loaded your skill's `SKILL.md`; it didn't trigger if the agent proceeded without consulting it.

Most agent clients provide execution logs, tool call histories, or verbose output — check your client's documentation.

A query "passes" if:
- `should_trigger` is `true` and the skill was invoked, OR
- `should_trigger` is `false` and the skill was not invoked

### Running Multiple Times

Model behavior is nondeterministic — the same query might trigger the skill on one run but not the next. Run each query **multiple times** (3 is a reasonable starting point) and compute a **trigger rate**: the fraction of runs where the skill was invoked.

A should-trigger query passes if its trigger rate is above a threshold (0.5 is a reasonable default). A should-not-trigger query passes if its trigger rate is below that threshold.

With 20 queries × 3 runs = 60 invocations. Script this.

The general pattern — adapt the `check_triggered` function for your specific agent client:

```bash
#!/bin/bash
# Generic structure — replace check_triggered with your client's invocation + detection logic
QUERIES_FILE="${1:?Usage: $0 <queries.json>}"
SKILL_NAME="my-skill"
RUNS=3

# Returns 0 if the skill was invoked, 1 otherwise.
# Replace this function with detection logic for your agent client:
#   - Check tool call logs, verbose output, or session transcripts
#   - Look for evidence that SKILL.md was read or the skill tool was called
check_triggered() {
  local query="$1"
  # Example — Claude Code CLI (--output-format json exposes tool_use entries):
  # claude -p "$query" --output-format json 2>/dev/null \
  #   | jq -e --arg skill "$SKILL_NAME" \
  #     'any(.messages[].content[]; .type == "tool_use" and .name == "Skill" and .input.skill == $skill)' \
  #     > /dev/null 2>&1
  #
  # Example — any CLI agent with a --verbose or --trace flag:
  # your-agent --skill-dir ~/.agents/skills --verbose -p "$query" 2>&1 \
  #   | grep -q "skill:$SKILL_NAME"
  echo "Implement for your client" && return 1
}

count=$(jq length "$QUERIES_FILE")
for i in $(seq 0 $((count - 1))); do
  query=$(jq -r ".[$i].query" "$QUERIES_FILE")
  should_trigger=$(jq -r ".[$i].should_trigger" "$QUERIES_FILE")
  triggers=0

  for run in $(seq 1 $RUNS); do
    check_triggered "$query" && triggers=$((triggers + 1))
  done

  jq -n \
    --arg query "$query" \
    --argjson should_trigger "$should_trigger" \
    --argjson triggers "$triggers" \
    --argjson runs "$RUNS" \
    '{query: $query, should_trigger: $should_trigger, triggers: $triggers, runs: $runs, trigger_rate: ($triggers / $runs)}'
done | jq -s '.'
```

> **Tip**: If your agent client supports it, stop a run early once the outcome is clear — the agent either consulted the skill or started working without it. This significantly reduces time and cost.

---

## Avoiding Overfitting with Train/Validation Splits

If you optimize the description against all your queries, you risk overfitting — crafting a description that works for these specific phrasings but fails on new ones.

**Split your query set:**
- **Train set (~60%)**: the queries you use to identify failures and guide improvements
- **Validation set (~40%)**: queries you set aside and only use to check whether improvements generalize

Make sure both sets have a proportional mix of should-trigger and should-not-trigger queries. Shuffle randomly and keep the split fixed across iterations.

---

## The Optimization Loop

1. **Evaluate** the current description on both train and validation sets.
   - Train results guide changes; validation results tell you whether changes generalize.
2. **Identify failures in the train set**: which should-trigger queries didn't trigger? Which should-not-trigger queries did?
   - Only use train set failures to guide your changes.
3. **Revise the description.** Focus on generalizing:
   - Should-trigger queries failing → description too narrow. Broaden scope or add context about when the skill is useful.
   - Should-not-trigger queries false-triggering → description too broad. Add specificity about what the skill does *not* do.
   - **Avoid adding specific keywords from failed queries — that's overfitting.** Find the general category those queries represent and address that.
   - If stuck after several iterations, try a structurally different approach rather than incremental tweaks.
   - Check the description stays under the 1024-character limit (descriptions tend to grow during optimization).
4. **Repeat** steps 1–3 until all train set queries pass or you stop seeing meaningful improvement.
5. **Select the best iteration** by its validation pass rate — the best description may not be the last one you produced.

Five iterations is usually enough. If performance isn't improving, the issue may be with the queries (too easy, too hard, or poorly labeled) rather than the description.

> **Tip**: The [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) skill (Anthropic reference implementation) automates this loop end-to-end: splits the eval set, evaluates trigger rates in parallel, proposes description improvements, and generates a live HTML report. Your harness may offer equivalent tooling — check its documentation.

---

## Applying the Result

1. Update the `description` field in your `SKILL.md` frontmatter.
2. Verify the description is under the 1024-character limit.
3. Try a few prompts manually as a quick sanity check.
4. For a rigorous check, write 5–10 fresh queries (never part of the optimization process) and run them through the eval script.

### Before and After Example

```yaml
# Before
description: Process CSV files.

# After
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use this
  skill when the user has a CSV, TSV, or Excel file and wants to
  explore, transform, or visualize the data, even if they don't
  explicitly mention "CSV" or "analysis."
```

The improved description is more specific about what the skill does (summary stats, derived columns, charts, cleaning) and broader about when it applies (CSV, TSV, Excel; even without explicit keywords).

---

## Next Steps

Once your skill triggers reliably, evaluate whether it produces good outputs. See [Evaluating Skill Output Quality](05-evaluating-skills.md).
