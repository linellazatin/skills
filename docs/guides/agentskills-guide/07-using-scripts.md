# Using Scripts in Skills

> Source: https://agentskills.io/skill-creation/using-scripts.md

How to run commands and bundle executable scripts in your skills.

Skills can instruct agents to run shell commands and bundle reusable scripts in a `scripts/` directory. This guide covers one-off commands, self-contained scripts with their own dependencies, and how to design script interfaces for agentic use.

---

## One-Off Commands

When an existing package already does what you need, reference it directly in `SKILL.md` — no `scripts/` directory needed. Many ecosystems provide tools that auto-resolve dependencies at runtime.

### Python — `uvx`

[uvx](https://docs.astral.sh/uv/guides/tools/) runs Python packages in isolated environments with aggressive caching. Ships with [uv](https://docs.astral.sh/uv/).

```bash
uvx ruff@0.8.0 check .
uvx black@24.10.0 .
```

Fast, caches aggressively — repeat runs are near-instant. Requires a separate install (not bundled with Python).

### Python — `pipx`

[pipx](https://pipx.pypa.io/) runs Python packages in isolated environments. Available via OS package managers (`apt install pipx`, `brew install pipx`).

```bash
pipx run 'black==24.10.0' .
pipx run 'ruff==0.8.0' check .
```

### JavaScript — `npx`

Runs npm packages, downloading on demand. Ships with npm (which ships with Node.js).

```bash
npx eslint@9 --fix .
npx create-vite@6 my-app
```

### JavaScript — `bunx`

Bun's equivalent of `npx`. Ships with [Bun](https://bun.sh/).

```bash
bunx eslint@9 --fix .
bunx create-vite@6 my-app
```

Only appropriate when the user's environment has Bun rather than Node.js.

### Deno — `deno run`

Runs scripts directly from URLs or specifiers.

```bash
deno run npm:create-vite@6 my-app
deno run --allow-read npm:eslint@9 -- --fix .
```

Permission flags (`--allow-read`, etc.) required for filesystem/network access.

### Go — `go run`

Compiles and runs Go packages directly. Built into the `go` command.

```bash
go run golang.org/x/tools/cmd/goimports@v0.28.0 .
go run github.com/golangci/golangci-lint/cmd/golangci-lint@v1.62.0 run
```

### Tips for One-Off Commands

- **Pin versions** (`npx eslint@9.0.0`) so the command behaves the same over time.
- **State prerequisites** in `SKILL.md` ("Requires Node.js 18+") rather than assuming the environment has them. For runtime-level requirements, use the `compatibility` frontmatter field.
- **Move complex commands into scripts.** When a command grows complex enough that it's hard to get right on the first try, a tested script in `scripts/` is more reliable.

---

## Referencing Scripts from `SKILL.md`

Use **relative paths from the skill directory root** to reference bundled files. The agent resolves these automatically.

List available scripts in `SKILL.md` so the agent knows they exist:

```markdown
## Available scripts

- **`scripts/validate.sh`** — Validates configuration files
- **`scripts/process.py`** — Processes input data
```

Then instruct the agent to run them:

```markdown
## Workflow

1. Run the validation script:
   ```bash
   bash scripts/validate.sh "$INPUT_FILE"
   ```

2. Process the results:
   ```bash
   python3 scripts/process.py --input results.json
   ```
```

> **Note**: Script execution paths (in code blocks) are relative to the **skill directory root**, because the agent runs commands from there. The same relative-path convention works in support files like `references/*.md`.

---

## Self-Contained Scripts

Bundle scripts in `scripts/` that declare their own dependencies inline. The agent runs them with a single command — no separate manifest file or install step required.

### Python (PEP 723)

[PEP 723](https://peps.python.org/pep-0723/) defines inline script metadata. Declare dependencies in a TOML block inside `# ///` markers:

```python
# scripts/extract.py
# /// script
# dependencies = [
#   "beautifulsoup4",
# ]
# ///

from bs4 import BeautifulSoup

html = '<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>'
print(BeautifulSoup(html, "html.parser").select_one("p.info").get_text())
```

Run with uv (recommended):

```bash
uv run scripts/extract.py
```

`uv run` creates an isolated environment, installs dependencies, and runs the script. `pipx run` also supports PEP 723.

- Pin versions with PEP 508 specifiers: `"beautifulsoup4>=4.12,<5"`
- Use `requires-python` to constrain Python version
- Use `uv lock --script` for a lockfile and full reproducibility

### Deno

`npm:` and `jsr:` import specifiers make every Deno script self-contained by default:

```typescript
// scripts/extract.ts
#!/usr/bin/env -S deno run

import * as cheerio from "npm:cheerio@1.0.0";

const html = `<html><body><p class="info">Test</p></body></html>`;
const $ = cheerio.load(html);
console.log($("p.info").text());
```

```bash
deno run scripts/extract.ts
```

- `npm:` for npm packages, `jsr:` for Deno-native packages
- Version specifiers: `@1.0.0` (exact), `@^1.0.0` (compatible)
- Dependencies cached globally; use `--reload` to force re-fetch
- Packages with native addons (node-gyp) may not work

### Bun

Bun auto-installs missing packages at runtime when no `node_modules` directory is found:

```typescript
// scripts/extract.ts
#!/usr/bin/env bun

import * as cheerio from "cheerio@1.0.0";

const html = `<html><body><p class="info">Test</p></body></html>`;
const $ = cheerio.load(html);
console.log($("p.info").text());
```

```bash
bun run scripts/extract.ts
```

- No `package.json` or `node_modules` needed; TypeScript works natively
- If a `node_modules` directory exists anywhere up the tree, auto-install is disabled

### Ruby

Bundler ships with Ruby since 2.6. Use `bundler/inline` to declare gems directly:

```ruby
# scripts/extract.rb
require 'bundler/inline'

gemfile do
  source 'https://rubygems.org'
  gem 'nokogiri'
end

html = '<html><body><p class="info">Test</p></body></html>'
doc = Nokogiri::HTML(html)
puts doc.at_css('p.info').text
```

```bash
ruby scripts/extract.rb
```

- Pin versions explicitly (`gem 'nokogiri', '~> 1.16'`) — there is no lockfile
- An existing `Gemfile` or `BUNDLE_GEMFILE` env var can interfere

---

## Designing Scripts for Agentic Use

When an agent runs your script, it reads stdout and stderr to decide what to do next. These design choices make scripts dramatically easier for agents to use.

### Avoid Interactive Prompts

**This is a hard requirement.** Agents operate in non-interactive shells — they cannot respond to TTY prompts, password dialogs, or confirmation menus. A script that blocks on interactive input will hang indefinitely.

Accept all input via command-line flags, environment variables, or stdin:

```
# Bad: hangs waiting for input
$ python scripts/deploy.py
Target environment: _

# Good: clear error with guidance
$ python scripts/deploy.py
Error: --env is required. Options: development, staging, production.
Usage: python scripts/deploy.py --env staging --tag v1.2.3
```

### Document Usage with `--help`

`--help` output is the primary way an agent learns your script's interface. Include a brief description, available flags, and usage examples:

```
Usage: scripts/process.py [OPTIONS] INPUT_FILE

Process input data and produce a summary report.

Options:
  --format FORMAT    Output format: json, csv, table (default: json)
  --output FILE      Write output to FILE instead of stdout
  --verbose          Print progress to stderr

Examples:
  scripts/process.py data.csv
  scripts/process.py --format csv --output report.csv data.csv
```

Keep it concise — the output enters the agent's context window.

### Write Helpful Error Messages

An opaque "Error: invalid input" wastes a turn. Say what went wrong, what was expected, and what to try:

```
Error: --format must be one of: json, csv, table.
       Received: "xml"
```

### Use Structured Output

Prefer structured formats — JSON, CSV, TSV — over free-form text. They can be consumed by both the agent and standard tools (`jq`, `cut`, `awk`), making your script composable in pipelines.

```
# Whitespace-aligned — hard to parse programmatically
NAME          STATUS    CREATED
my-service    running   2025-01-15

# Structured — unambiguous
{"name": "my-service", "status": "running", "created": "2025-01-15"}
```

**Separate data from diagnostics**: send structured data to stdout and progress messages/warnings to stderr. This lets the agent capture clean, parseable output while still having access to diagnostic information.

### Further Considerations

- **Idempotency.** Agents may retry commands. "Create if not exists" is safer than "create and fail on duplicate."
- **Input constraints.** Reject ambiguous input with a clear error rather than guessing. Use enums and closed sets where possible.
- **Dry-run support.** For destructive or stateful operations, a `--dry-run` flag lets the agent preview what will happen.
- **Meaningful exit codes.** Use distinct exit codes for different failure types (not found, invalid arguments, auth failure) and document them in your `--help` output.
- **Safe defaults.** Consider whether destructive operations should require explicit confirmation flags (`--confirm`, `--force`).
- **Predictable output size.** Many agent harnesses truncate tool output beyond a threshold (e.g., 10–30K characters). If your script might produce large output, default to a summary or a reasonable limit, and support flags like `--offset` for pagination. Alternatively, require agents to pass an `--output` flag specifying an output file, or `-` to explicitly opt in to stdout.
