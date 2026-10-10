"""Extract an exact version section from CHANGELOG.md, failing closed."""
import argparse
from pathlib import Path
import re


def extract_notes(changelog, tag):
    match = re.fullmatch(
        r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
        r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
        r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?", tag
    )
    if not match or (match[4] and any(
        p.isdigit() and len(p) > 1 and p.startswith("0") for p in match[4].split(".")
    )):
        raise ValueError("Tag must be v-prefixed SemVer, such as v0.2.0 or v0.2.0-rc.1")
    version = re.escape(tag[1:])
    target = re.compile(rf"^##\s+(?:{version}|\[{version}\])(?:\s+.*)?$")
    sections = []
    active = None
    fence = None
    for line in changelog.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        inside_fence = fence is not None
        if marker:
            chars, rest = marker.groups()
            if fence is None:
                fence = chars
            elif chars[0] == fence[0] and len(chars) >= len(fence) and not rest.strip():
                fence = None
        if not inside_fence and not marker and re.match(r"^##\s+", line):
            active = None
            if target.fullmatch(line):
                active = []
                sections.append(active)
        elif active is not None:
            active.append(line)
    if len(sections) != 1:
        raise ValueError(f"Expected exactly one changelog section for {tag}; found {len(sections)}")
    notes = "\n".join(sections[0]).strip()
    if not notes:
        raise ValueError(f"Changelog section for {tag} is empty")
    return notes + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("--changelog", type=Path, default=Path("CHANGELOG.md"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        notes = extract_notes(args.changelog.read_text(encoding="utf-8"), args.tag)
    except ValueError as error:
        parser.error(str(error))
    args.output.write_text(notes, encoding="utf-8")
