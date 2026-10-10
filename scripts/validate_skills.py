"""Repository CI validation. Requires PyYAML; bundled validation stays stdlib-only."""
import importlib.util
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "quick_validate", ROOT / "skills/craft-skill/scripts/quick_validate.py"
)
quick_validate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quick_validate)


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


def validate_all(root=ROOT / "skills"):
    errors = []
    folders = sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []
    if not folders:
        return [f"No skill directories found in {root}"]
    for folder in folders:
        errors.extend(f"{folder.name}: {e}" for e in quick_validate.validate(str(folder)))
        path = folder / "SKILL.md"
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            if not lines or lines[0] != "---":
                raise ValueError("Frontmatter must start with a standalone ---")
            end = lines.index("---", 1)
            fields = yaml.load("\n".join(lines[1:end]), Loader=UniqueKeyLoader)
            if not isinstance(fields, dict):
                raise ValueError("Frontmatter must be a YAML mapping")
            for name in ("name", "description"):
                if not isinstance(fields.get(name), str) or not fields[name].strip():
                    raise ValueError(f"{name} must be a nonempty string")
            if "metadata" in fields and not isinstance(fields["metadata"], dict):
                raise ValueError("metadata must be a mapping")
        except (ValueError, TypeError, yaml.YAMLError) as error:
            errors.append(f"{folder.name}: {error}")
    return errors


if __name__ == "__main__":
    problems = validate_all()
    for problem in problems:
        print(f"ERROR: {problem}", file=sys.stderr)
    if problems:
        sys.exit(1)
    print("All skill frontmatter and structure checks passed.")
