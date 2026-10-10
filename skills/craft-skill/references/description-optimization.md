# Description optimization reference

Read this file when activation or neighboring-task misrouting needs investigation. Use recorded failures to decide what to change; do not run an optimization loop for every skill edit.

## The three principles

Apply these criteria when generating candidates:

1. **Imperative phrasing.** The description should read as an instruction:
   "Use this skill when..." not "This skill does...". The agent is deciding
   whether to act — tell it when to act. The description serves as the skill's
   gateway, so this is very important.

2. **User intent, not implementation.** Describe what the user is trying to
   achieve, not how the skill works internally. The agent matches the description
   against what the user asked for, not against the skill's steps.

3. **Near-miss negatives.** The description must be specific enough to avoid
   triggering on adjacent tasks that share keywords. Think about what queries
   share your keywords but need something different — the description should
   exclude those without naming them explicitly.

## Generate candidates

Start with the current description and a small number of materially different candidates. For each one:
- Write the description (under 1024 characters)
- Write one sentence of rationale: what triggering problem this version solves

Format:
```
Candidate 1:
[description text]
Rationale: [one sentence]

Candidate 2:
[description text]
Rationale: [one sentence]
```

Record candidates and their intended improvement. Continue already authorized refinement; request a user decision only when a candidate changes the intended scope.

## Manual test checklist

Choose realistic matching requests and near-misses that exercise the scope boundary. Use enough cases to cover the observed failure and meaningful phrasing variations; a larger measured study can use roughly balanced matching and non-matching sets.

If authorized harness execution is available, repeat cases and record invocation outcomes. Fix the repetition count and acceptance threshold before comparing candidates; report rates and sample sizes. If execution is unavailable, inspect the intended routing manually and label it an instruction review, not a measured trigger rate.

Rules:
- Write them as realistic user messages, not abstract descriptions.
  Bad: "Extract text from PDF". Good: "hey can you pull out all the tables
  from this quarterly report pdf, it's in ~/Downloads/Q4-report.pdf"
- Should-trigger queries: vary phrasing, formality, and explicitness. Include
  at least one where the user does not name the skill's domain directly.
- Should-not-trigger queries: near-misses only — queries sharing keywords but
  needing something different. Weak: "write a fibonacci function" (no overlap).
  Strong: a query that shares domain terms but needs a different skill or a
  simpler response. Do not use obviously irrelevant queries.

To avoid overfitting the description to specific phrasings, split your queries:
use ~60% as the train set to identify failures and guide revisions, and hold
~40% as a validation set to check whether improvements generalize. Only use
train-set failures to drive changes. A description that wins on the train set
but drops on the validation set is overfit — revise more broadly.

Run authorized cases directly where possible. If only the user can access the target harness, provide the exact prompts and requested observations, complete other available checks, and record the host evaluation as pending.

## Reading results and selecting a description

After actual results are available:
1. Tally trigger rates: which candidate performs best across the train-set queries?
2. Check the validation set: does the best train-set performer hold up?
3. If no single candidate wins cleanly, synthesize the best-performing elements
   and write a final description.
4. Tell the user which candidate you are recommending and why.
5. Update the `description` field in the frontmatter of SKILL.md.
6. Record the chosen description, evidence, and limits in the existing task record. If only manual inspection was possible, state that activation performance remains unmeasured.
