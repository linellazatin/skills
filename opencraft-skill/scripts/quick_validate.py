#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""
Validate a skill directory's SKILL.md for spec compliance.

Usage: python scripts/quick_validate.py <skill-dir>
Exit 0 = valid. Exit 1 = one or more errors printed to stdout.
"""
import re
import sys
from pathlib import Path


def validate(skill_dir: str) -> list[str]:
    errors = []
    path = Path(skill_dir) / "SKILL.md"

    if not path.exists():
        return [f"SKILL.md not found in {skill_dir}"]

    content = path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        errors.append("SKILL.md must begin with --- frontmatter")
        return errors

    close = content.find("\n---", 3)
    if close == -1:
        errors.append("Frontmatter closing --- not found")
        return errors

    frontmatter = content[3:close]
    body = content[close + 4:]
    # The closing --- line ends with \n; strip it so it doesn't inflate the count.
    if body.startswith("\n"):
        body = body[1:]

    # Parse frontmatter key-value pairs (handles block scalars > | >- |-)
    fields: dict[str, str] = {}
    current_key = None
    current_lines: list[str] = []
    for line in frontmatter.splitlines():
        if line and not line.startswith(" ") and not line.startswith("\t"):
            if current_key:
                fields[current_key] = " ".join(current_lines).strip()
            m = re.match(r"^(\w[\w-]*):\s*(.*)", line)
            if m:
                current_key = m.group(1)
                val = m.group(2).strip()
                current_lines = [] if val in (">", "|", ">-", "|-", "") else [val]
        elif current_key:
            current_lines.append(line.strip())
    if current_key:
        fields[current_key] = " ".join(current_lines).strip()

    # Validate name
    name = fields.get("name", "").strip("'\"")
    if not name:
        errors.append("name field is required")
    else:
        if not re.fullmatch(r"[a-z0-9]([a-z0-9-]*[a-z0-9])?", name):
            errors.append(
                f"name '{name}': only lowercase letters, numbers, hyphens; "
                "no leading or trailing hyphens"
            )
        if "--" in name:
            errors.append(f"name '{name}': consecutive hyphens not allowed")
        if len(name) > 64:
            errors.append(f"name '{name}': {len(name)} chars, max 64")
        dir_name = Path(skill_dir).resolve().name
        if name != dir_name:
            errors.append(
                f"name '{name}' does not match directory name '{dir_name}'"
            )

    # Validate description
    desc = fields.get("description", "")
    if not desc:
        errors.append("description field is required")
    else:
        if len(desc) > 1024:
            errors.append(f"description: {len(desc)} chars, max 1024")
        if re.search(r"<[A-Z_]+>", desc):
            errors.append("description contains unfilled template placeholders")

    # Validate allowed frontmatter keys
    allowed = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
    unknown = set(fields) - allowed
    if unknown:
        errors.append(f"unknown frontmatter keys: {', '.join(sorted(unknown))}")

    # Validate body length
    body_lines = len(body.splitlines())
    if body_lines > 500:
        errors.append(f"body is {body_lines} lines (max 500)")

    return errors


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/quick_validate.py <skill-dir>", file=sys.stderr)
        print("  --help    Show this message", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    errors = validate(sys.argv[1])
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        sys.exit(1)

    print("OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
