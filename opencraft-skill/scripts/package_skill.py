#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""
Package a skill directory into a distributable .skill file.

Validates first (via quick_validate.py), then zips the skill directory
excluding build artifacts and eval data.

Usage:
  python3 scripts/package_skill.py <skill-dir> [output-dir]
  uv run scripts/package_skill.py <skill-dir> [output-dir]

  <skill-dir>   Path to the skill directory (must contain SKILL.md)
  [output-dir]  Where to write the .skill file (default: current directory)

Exit 0 = packaged successfully. Exit 1 = validation failed or packaging error.
"""
import fnmatch
import subprocess
import sys
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {"__pycache__", "node_modules"}
EXCLUDE_ROOT_DIRS = {"evals"}
EXCLUDE_GLOBS = {"*.pyc"}
EXCLUDE_FILES = {".DS_Store"}


def should_exclude(rel_path: Path) -> bool:
    """Return True if this path should be omitted from the package."""
    parts = rel_path.parts
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    # parts[0] is the skill dir name; parts[1] (if present) is its first subdir.
    if len(parts) > 1 and parts[1] in EXCLUDE_ROOT_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if sys.argv[1:] else 1)

    skill_dir = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path.cwd()

    if not skill_dir.is_dir():
        print(f"ERROR: not a directory: {skill_dir}", file=sys.stderr)
        sys.exit(1)
    if not (skill_dir / "SKILL.md").exists():
        print(f"ERROR: SKILL.md not found in {skill_dir}", file=sys.stderr)
        sys.exit(1)

    # Validate before packaging.
    validator = Path(__file__).resolve().parent / "quick_validate.py"
    result = subprocess.run(
        [sys.executable, str(validator), str(skill_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout.strip())
        print("\nPackaging aborted — fix validation errors first.", file=sys.stderr)
        sys.exit(1)

    skill_name = skill_dir.name
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{skill_name}.skill"

    print(f"Packaging {skill_dir} -> {out_file}")
    with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(skill_dir.rglob("*")):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(skill_dir.parent)
            if should_exclude(rel):
                print(f"  skip: {rel}")
                continue
            zf.write(file_path, rel)
            print(f"  add:  {rel}")

    print(f"\nOK: {out_file} ({out_file.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
