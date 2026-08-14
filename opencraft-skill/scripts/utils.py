"""Shared utilities for opencraft-skill automation scripts (Tier 2)."""

from pathlib import Path


def parse_skill_md(skill_path: Path) -> tuple:
    """Parse SKILL.md and return (name, description, full_content).

    Handles YAML block scalars (>, |, >-, |-) in the description field.
    Raises ValueError if frontmatter is missing or malformed.
    """
    content = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md is missing opening frontmatter delimiter (---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md is missing closing frontmatter delimiter (---)")

    name = ""
    description = ""
    fm_lines = lines[1:end_idx]
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip("'\"")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-", ""):
                cont = []
                i += 1
                while i < len(fm_lines) and (
                    fm_lines[i].startswith("  ") or fm_lines[i].startswith("\t")
                ):
                    cont.append(fm_lines[i].strip())
                    i += 1
                description = " ".join(cont)
                continue
            else:
                description = value.strip("'\"")
        i += 1

    return name, description, content
