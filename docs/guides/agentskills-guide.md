# Agent Skills Guide

Local reference adapted from https://agentskills.io, with examples and implementation guidance. It is a maintained snapshot, not a guarantee of current upstream content or universal client behavior. For this repository, the selected skill's instructions and the user's current scope govern execution; examples do not authorize delegation, provider costs, file creation, or Git operations.

---

## Contents

| File | Description |
|------|-------------|
| [01-overview.md](agentskills-guide/01-overview.md) | What are Agent Skills, how they work, and why they exist |
| [02-specification.md](agentskills-guide/02-specification.md) | Complete format specification: `SKILL.md` structure, frontmatter fields, directory conventions |
| [03-quickstart.md](agentskills-guide/03-quickstart.md) | Create your first skill end-to-end with a working example |
| [04-best-practices.md](agentskills-guide/04-best-practices.md) | How to write well-scoped, effective skills — the most important guide for skill creators |
| [05-evaluating-skills.md](agentskills-guide/05-evaluating-skills.md) | Eval-driven iteration: test cases, assertions, grading, benchmarks, and the improvement loop |
| [06-optimizing-descriptions.md](agentskills-guide/06-optimizing-descriptions.md) | How to write and test `description` fields so skills trigger reliably |
| [07-using-scripts.md](agentskills-guide/07-using-scripts.md) | Bundling executable scripts: inline dependencies, agentic script design |
| [08-client-implementation.md](agentskills-guide/08-client-implementation.md) | How agent harnesses implement skills support (discovery, parsing, disclosure, activation) |

---

## Key Concepts at a Glance

### What a skill is

A directory with a `SKILL.md` file containing YAML frontmatter and Markdown instructions:

```
my-skill/
├── SKILL.md        # Required: name, description, instructions
├── scripts/        # Optional: executable code
├── references/     # Optional: documentation
└── assets/         # Optional: templates, resources
```

### Minimal `SKILL.md`

```markdown
---
name: my-skill
description: What this skill does and when to use it. Use imperative phrasing. Cover user intent keywords, even if the user won't say the domain name explicitly.
---

# My Skill

Instructions for the agent go here.
```

### How skills activate

1. **Discovery** — agent loads `name` + `description` of all skills at startup (~50–100 tokens each)
2. **Activation** — when a task matches, agent reads full `SKILL.md` into context (< 5000 tokens recommended)
3. **Execution** — agent follows instructions, loads referenced files on demand

### Frontmatter fields

| Field | Required | Limit |
|-------|----------|-------|
| `name` | Yes | 64 chars, lowercase + hyphens, must match directory name |
| `description` | Yes | 1024 chars |
| `compatibility` | No | 500 chars — environment requirements |
| `license` | No | — |
| `metadata` | No | key-value map |
| `allowed-tools` | No | space-separated, experimental |

### The description is everything for triggering

- Use imperative phrasing: "Use this skill when..."
- Describe user intent, not implementation
- Be explicit about when the skill applies, including indirect cases
- Stay under 1024 characters

### Keep `SKILL.md` lean

- Under 500 lines, under 5000 tokens
- Only include what the agent wouldn't know without the skill
- Move large reference material to `references/` and tell the agent when to load it
- Gotchas section = highest-value content for many skills

---

## For Skill Sessions

Use the relevant steps for the authorized task; this is not a mandatory pipeline for every edit:

1. **Draft** — start from real expertise, not generic LLM output
2. **Structure** — coherent scope, moderate detail, clear defaults
3. **Scripts, when needed** — self-contained, no interactive prompts, structured output, helpful `--help`
4. **Description** — imperative, intent-focused, specific enough to not over-trigger
5. **Evaluation** — choose realistic cases and observable criteria before grading. Use controlled independent runs when authorized and available; label inline walkthroughs as author review.
6. **Iterate** — feed failed assertions + human feedback + traces back into the skill
7. **Description evaluation, when activation needs investigation** — use matching and near-miss cases, fixed scoring, and authorized harness execution. Sample sizes are examples; without execution, disclose that trigger rates remain unmeasured.

---

*Source: https://agentskills.io — extracted and reformatted for agent and human use.*

---

## Skills built from this guide

| Skill | Location | Description |
|-------|----------|-------------|
| `craft-skill` | `~/.agents/skills/craft-skill/` | Harness-agnostic meta-skill for creating Agent Skills. Three modes: Extract, Design, and Refine. Bundled validation, packaging, benchmarking, and description optimization; automated trigger evaluation requires Claude Code CLI. Built using this guide as its methodology basis. |

---

## Changelog

### 2026-08-10 — Harness agnosticism fixes

After an agnosticism audit, four Claude/Anthropic-specific biases were identified and corrected:

| File | What changed |
|------|--------------|
| `05-evaluating-skills.md` | Timing tip generalized: "many harnesses expose token counts in run completion events" with Claude Code cited as one example, not the only one |
| `05-evaluating-skills.md` | `skill-creator` link labeled as "Anthropic reference implementation" with note that harness-specific equivalents may exist |
| `06-optimizing-descriptions.md` | Trigger-testing shell script restructured: Claude Code CLI moved to a commented example inside a generic `check_triggered()` stub; a second generic example (any `--verbose` CLI) added alongside it |
| `06-optimizing-descriptions.md` | `skill-creator` link labeled as "Anthropic reference implementation" with note that harness-specific equivalents may exist |

The `02-specification.md` `compatibility` field example was already neutral (`Designed for ANY agent`) — no change needed. The `08-client-implementation.md` mention of `.claude/skills/` is retained as a factual compatibility note, correctly framed as one implementation's path.
