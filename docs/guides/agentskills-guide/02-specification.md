# Agent Skills Specification

> Source: https://agentskills.io/specification.md

The complete format specification for Agent Skills.

## Directory Structure

A skill is a directory containing, at minimum, a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

## `SKILL.md` Format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Frontmatter Fields

| Field           | Required | Constraints                                                                                                        |
| --------------- | -------- | ------------------------------------------------------------------------------------------------------------------ |
| `name`          | Yes      | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen.              |
| `description`   | Yes      | Max 1024 characters. Non-empty. Describes what the skill does and when to use it.                                  |
| `license`       | No       | License name or reference to a bundled license file.                                                               |
| `compatibility` | No       | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.).  |
| `metadata`      | No       | Arbitrary key-value mapping for additional metadata (a map from string keys to string values).                     |
| `allowed-tools` | No       | Space-separated string of pre-approved tools the skill may use. (Experimental)                                     |

### Minimal Example

```markdown
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

### Example with Optional Fields

```markdown
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

---

### `name` Field Rules

- Must be 1–64 characters
- Only lowercase alphanumeric characters (`a-z`, `0-9`) and hyphens (`-`)
- Must not start or end with a hyphen
- Must not contain consecutive hyphens (`--`)
- **Must match the parent directory name**

**Valid:**
```yaml
name: pdf-processing
name: data-analysis
name: code-review
```

**Invalid:**
```yaml
name: PDF-Processing    # uppercase not allowed
name: -pdf              # cannot start with hyphen
name: pdf--processing   # consecutive hyphens not allowed
```

---

### `description` Field Rules

- Must be 1–1024 characters
- Should describe both **what** the skill does and **when** to use it
- Should include specific keywords that help agents identify relevant tasks

**Good:**
```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

**Poor:**
```yaml
description: Helps with PDFs.
```

---

### `compatibility` Field

- Must be 1–500 characters if provided
- Only include if the skill has specific environment requirements
- Can indicate intended product, required packages, network access needs, etc.

```yaml
compatibility: Designed for ANY agent
compatibility: Requires git, docker, jq, and access to the internet
compatibility: Requires Python 3.14+ and uv
```

Most skills do not need this field.

---

### `metadata` Field

- A map from string keys to string values
- Clients can use this for additional properties not defined by the spec
- Use reasonably unique key names to avoid conflicts

```yaml
metadata:
  author: example-org
  version: "1.0"
```

---

### `allowed-tools` Field

- Space-separated string of pre-approved tools
- Experimental — support varies between agent implementations

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

---

## Body Content

The Markdown body after the frontmatter contains the skill instructions. There are no format restrictions — write whatever helps agents perform the task effectively.

Recommended sections:
- Step-by-step instructions
- Examples of inputs and outputs
- Common edge cases

The agent loads the entire body once it activates the skill. For long skills, split content into referenced files.

---

## Optional Directories

### `scripts/`

Executable code that agents can run. Scripts should:
- Be self-contained or clearly document dependencies
- Include helpful error messages
- Handle edge cases gracefully

Supported languages depend on the agent. Common options: Python, Bash, JavaScript.

### `references/`

Additional documentation agents can read on demand:
- `REFERENCE.md` — detailed technical reference
- `FORMS.md` — form templates or structured data formats
- Domain-specific files (`finance.md`, `legal.md`, etc.)

Keep individual reference files focused — agents load these on demand, so smaller files mean less context use.

### `assets/`

Static resources:
- Templates (document, configuration)
- Images (diagrams, examples)
- Data files (lookup tables, schemas)

---

## Progressive Disclosure

Agents load skills progressively — more detail only as needed:

1. **Metadata** (~100 tokens): `name` and `description` loaded at startup for all skills
2. **Instructions** (< 5000 tokens recommended): full `SKILL.md` body loaded on activation
3. **Resources** (as needed): files in `scripts/`, `references/`, `assets/` loaded only when required

**Keep `SKILL.md` under 500 lines.** Move detailed reference material to separate files.

---

## File References

Use relative paths from the skill root:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains.

---

## Validation

Use the `skills-ref` reference library to validate:

```bash
skills-ref validate ./my-skill
```

Checks that `SKILL.md` frontmatter is valid and follows all naming conventions.

- Tool: https://github.com/agentskills/agentskills/tree/main/skills-ref
