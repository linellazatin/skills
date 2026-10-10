# Quickstart: Create Your First Skill

> Source: https://agentskills.io/skill-creation/quickstart.md

Create your first Agent Skill and see it work in VS Code (or any compatible agent).

## Prerequisites

- A skills-compatible agent installed (e.g., VS Code with GitHub Copilot, Claude Code, Cursor, Gemini CLI)
- Basic familiarity with your terminal

## Step 1: Create the Skill Directory

```bash
mkdir -p ~/.agents/skills/roll-dice
cd ~/.agents/skills/roll-dice
```

The directory name becomes the skill's `name`. Use lowercase letters, numbers, and hyphens only.

## Step 2: Write `SKILL.md`

Create `SKILL.md` inside the directory:

````markdown
---
name: roll-dice
description: Roll one or more dice and return the results. Use when the user asks to roll dice, simulate a dice roll, or generate a random number like a die.
---

# Roll Dice

Roll dice using a random number generator script.

## Usage

Run the dice roller script with the number of dice and sides:

```bash
python3 scripts/roll.py --dice 2 --sides 6
```

Default is 1 die with 6 sides if no arguments are provided.

## Output

The script prints each roll result and the total. Report these results to the user.
````

## Step 3: Add the Script

```bash
mkdir scripts
```

Create `scripts/roll.py`:

```python
#!/usr/bin/env python3
import argparse
import random

parser = argparse.ArgumentParser(description="Roll dice")
parser.add_argument("--dice", type=int, default=1, help="Number of dice")
parser.add_argument("--sides", type=int, default=6, help="Sides per die")
args = parser.parse_args()

rolls = [random.randint(1, args.sides) for _ in range(args.dice)]
for i, r in enumerate(rolls, 1):
    print(f"Die {i}: {r}")
print(f"Total: {sum(rolls)}")
```

## Step 4: Verify Structure

```
roll-dice/
├── SKILL.md
└── scripts/
    └── roll.py
```

## Step 5: Test It

Open your agent and try:

> "Roll 3d6 for me"

The agent should activate the `roll-dice` skill, run the script, and report the results.

## Next Steps

- **[Best practices](04-best-practices.md)** — How to write skills that are well-scoped and effective.
- **[Optimizing descriptions](06-optimizing-descriptions.md)** — Test and improve your skill's description so it activates on the right prompts.
- **[Specification](02-specification.md)** — The complete format reference for `SKILL.md` files.
- **Example skills**: https://github.com/anthropics/skills
