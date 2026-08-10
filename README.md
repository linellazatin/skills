# openlines-skills

Custom [Agent Skills](https://agentskills.io) by Lines. Harness-agnostic — skills in this repo work across Claude Code, Pi, Cursor, Copilot, Gemini CLI, and any other client that supports the Agent Skills standard. Ideal if you're working on multiple agent harnesses, and would like to consolidated a single version of your skill that may work across platforms and harnesses - which is my main goal. Another goal is that I'm trying to optimize instruction-based skill processes to also work with smaller parameter LLMs, making your skill be as 'resilient as possible', even though no specific agent harness is coupled to it.

## Skills

| Skill | Description |
|-------|-------------|
| [opencraft-skill](opencraft-skill/SKILL.md) | Create, extract, and refine Agent Skills that work across any agent harness. Spec-driven, two modes: extract from history or design from scratch. |

## What are Agent Skills?

Agent Skills are plain Markdown files (`SKILL.md`) that give AI agents reusable, specialized behavior. A skill lives in a named directory and is loaded by the agent when a task matches its description.

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable helpers
├── references/       # Optional: reference docs
└── assets/           # Optional: templates, resources
```

The format is an open standard. Full spec and guides are in [`docs/guides/`](docs/guides/).

## Using these skills

1. Copy the skill directory (e.g. `opencraft-skill/`) into your agent's skills directory.
   - Pi / Claude Code / most harnesses: `~/.agents/skills/`
   - Check your harness docs for the exact path.
2. Start a session. The skill activates automatically when a task matches its description.

## Reference

- [`docs/guides/agentskills-guide.md`](docs/guides/agentskills-guide.md) — full guide (overview, spec, quickstart, best practices, evals, description optimization, scripts, client implementation)
- [agentskills.io](https://agentskills.io) — upstream standard

## License

MIT
