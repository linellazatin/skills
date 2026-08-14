# openlines-skills

Custom [Agent Skills](https://agentskills.io) by Lines. Harness-agnostic — skills in this repo work across Claude Code, Pi, Cursor, Copilot, Gemini CLI, and any other client that follows the Agent Skills open standard.

Two design goals drive every skill here:

1. **Single source, any harness.** No tool-specific names or platform assumptions. The same skill file runs wherever the standard is supported.
2. **Resilient across model sizes.** Skills are hardened for smaller-parameter models that may struggle with instruction following — explicit one-at-a-time question formats, prescriptive decision forks, no vague "handle this appropriately" language.

## Skills

| Skill | Description |
|-------|-------------|
| [opencraft-skill](opencraft-skill/SKILL.md) | Meta skill for creating Agent Skills. Three modes: **Extract** (capture from conversation history), **Design** (build from scratch), **Refine** (improve an existing skill). Includes a bundled eval and description-optimization pipeline. |

## What are Agent Skills?

Agent Skills are plain Markdown files (`SKILL.md`) that give AI agents reusable, specialized behavior. A skill lives in a named directory and is loaded by the agent when a task matches its description.

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── agents/           # Optional: subagent instruction files
├── scripts/          # Optional: executable helpers
├── references/       # Optional: reference docs loaded on demand
└── assets/           # Optional: templates, resources
```

The format is an open standard. Full spec and guides are in [`docs/guides/`](docs/guides/).

## Using these skills

1. Copy the skill directory (e.g. `opencraft-skill/`) into your agent's skills directory.
   - Claude Code / Pi / most harnesses: `~/.agents/skills/`
   - Check your harness docs for the exact path.
2. Start a session. The skill activates automatically when a task matches its description.

### Bundled tooling tiers

Skills in this repo may include two tiers of tooling:

**Tier 1 — stdlib Python 3, runs anywhere:**
- `scripts/quick_validate.py` — spec-check a skill before shipping it
- `scripts/aggregate_benchmark.py` — aggregate eval results into a benchmark report
- `scripts/package_skill.py` — zip a skill into a distributable `.skill` file

**Tier 2 — LLM provider required:**
- `scripts/run_eval.py` — automated trigger-rate measurement *(Claude Code CLI only)*
- `scripts/improve_description.py` — LLM-driven description rewriting *(any provider)*
- `scripts/run_loop.py` — full 60/40 train/test optimization loop *(any provider)*

Provider detection for `improve_description.py`: `ANTHROPIC_API_KEY` → `OPENAI_API_KEY` → `claude -p` fallback.
`run_eval.py` and `run_loop.py` (eval step) require Claude Code CLI — trigger testing is harness-specific.

## Reference

- [`docs/guides/agentskills-guide.md`](docs/guides/agentskills-guide.md) — full guide (overview, spec, quickstart, best practices, evals, description optimization, scripts, client implementation)
- [agentskills.io](https://agentskills.io) — upstream standard

## License

MIT
