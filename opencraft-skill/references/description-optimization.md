# Description optimization reference

Load this file when you reach the Description optimization section.
Work through all sections in order.

## The three principles

Explain these to the user before generating candidates:

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

Write 5 candidate descriptions. For each one:
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

Show all candidates to the user before moving to the test checklist.

## Manual test checklist

Generate ~20 test queries: 8–10 that should trigger and 8–10 that should not.

Model behavior is nondeterministic — the same query may trigger the skill on one
run and not the next. Run each query at least 3 times and compute a trigger rate
(fraction of runs where the skill was invoked). A should-trigger query passes if
its trigger rate is above 0.5; a should-not-trigger query passes if below 0.5.

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

Present the checklist to the user:
> "Try each of these in your agent with the skill installed and note whether the
> skill activated. Come back with the results and I will recommend the best
> candidate."

## Reading results and selecting a description

After the user reports results:
1. Tally trigger rates: which candidate performs best across the train-set queries?
2. Check the validation set: does the best train-set performer hold up?
3. If no single candidate wins cleanly, synthesize the best-performing elements
   and write a final description.
4. Tell the user which candidate you are recommending and why.
5. Update the `description` field in the frontmatter of SKILL.md.
6. Write `Description finalized` to the working file.
