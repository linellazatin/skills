# Script guidance for opencraft-skill

Load this file when the user has identified script candidates in the
Scripts (optional) section. Work through the four sections in order
for each script candidate.

## Section 1 — Confirm the type

Re-read the candidate the user described. Confirm which type it is before
proceeding. If you are unsure, ask the user one clarifying question.

**Command** — the logic already exists as a system tool or package. You
invoke it inline in SKILL.md. Nothing to write or bundle.
Good signal: you can express the full operation as one shell command with
flags. The command is stable across environments when version-pinned.
Example: `uvx ruff@0.8.0 check .`, `npx prettier@3 --write .`

**Script** — the logic does not exist yet and needs to be written. It
will run every time the relevant skill step runs, across many future uses.
Good signal: the user described a transformation, generation, or processing
step that is always the same regardless of the specific input values.
Example: a chart builder, a CSV normalizer, a report formatter.

**Validator** — the logic checks whether something is correct and blocks
the next step if it is not. It does not produce output the user sees
directly — it produces a pass/fail signal the agent acts on.
Good signal: the user said something like "before we do X, we need to make
sure Y is correct" or "we should check that the output is valid before
moving on."
Example: `scripts/validate_schema.py`, `scripts/check_required_fields.py`

If the candidate fits more than one type, ask: "Should this produce output
for the user, or just check that something is correct before the next step?"
Output for user → Script. Check before next step → Validator.

## Section 2 — Select a language

Ask the user: "What runtimes are available in your environment?"

Map their answer to a recommendation:

| Available            | Recommendation      | Inline dep syntax                               |
|----------------------|---------------------|-------------------------------------------------|
| Python + uv          | Python + PEP 723    | `# /// script` / `# dependencies = ["pkg"]`    |
| Python (no uv)       | Python + pip note   | Comment at top: `# pip install pkg`             |
| Node.js / npm        | JavaScript + npx    | No inline deps — use `npx pkg@version`          |
| Deno                 | TypeScript + Deno   | `import x from "npm:pkg@version"`               |
| Bun                  | TypeScript + Bun    | `import x from "pkg@version"` (auto-installs)   |
| Ruby                 | Ruby + bundler      | `require 'bundler/inline'; gemfile { gem 'pkg' }` |
| Bash only            | Bash                | No deps — limited to system tools               |

If unsure: use Python + PEP 723 if uv is available, Bash otherwise.

Always pin versions explicitly. "Latest" is not a version.

## Section 3 — Authoring rules

Apply all four rules while writing the script. Do not skip any.

**Rule 1 — No interactive prompts.**
All input must come from command-line flags, environment variables, or
stdin. Never use input(), getpass(), readline, or any TTY prompt.
A script that blocks on input will hang the agent indefinitely with no
error message. If a required value is missing, print an error and exit 1.

  Bad:  target = input("Enter target environment: ")
  Good: parser.add_argument("--env", required=True,
            help="Target environment: development, staging, production")

**Rule 2 — Implement --help.**
Every script must respond to --help with: a one-line description of what
the script does, all available flags with their types and defaults, and
at least one complete usage example. Keep it concise — this output enters
the agent's context window.

  Example --help output:
    Usage: scripts/process.py [OPTIONS] INPUT_FILE

    Normalize CSV columns and write cleaned output.

    Options:
      --output FILE   Write output to FILE (default: stdout)
      --drop-nulls    Drop rows with any null value (default: false)

    Example:
      scripts/process.py data.csv --output clean.csv

**Rule 3 — Structured output to stdout, diagnostics to stderr.**
Data the agent or user will consume: stdout, in JSON, CSV, or TSV.
Progress messages, warnings, debug info: stderr.
Never mix them. An agent parsing stdout must get clean structured data.

  Bad:  print(f"Processing {filename}...")   # pollutes stdout
        print(json.dumps(result))
  Good: print(f"Processing {filename}...", file=sys.stderr)
        print(json.dumps(result))

**Rule 4 — Idempotent by default.**
Running the script twice with the same inputs must produce the same result
and must not fail on the second run. Use "create if not exists", "upsert",
and "overwrite" patterns. Never assume a clean slate.

  Bad:  os.mkdir(output_dir)           # fails if dir exists
  Good: os.makedirs(output_dir, exist_ok=True)

## Section 4 — Quality checklist

Run the checklist for the script type you wrote. Fix every failure before
referencing the script from SKILL.md.

### Command checklist

- [ ] Version is pinned in the command (e.g. `ruff@0.8.0`, not `ruff`)
- [ ] Any prerequisites (runtime, package manager) are stated in SKILL.md
      near the command, e.g. "Requires Node.js 18+ and npm"
- [ ] The command is simple enough to express in one line with flags.
      If it needs conditional logic or multi-step setup — promote to Script.

### Script checklist

- [ ] Inline dependencies declared using the language's standard mechanism
      (PEP 723 block, `npm:` specifier, `bundler/inline` gemfile, etc.)
- [ ] `--help` implemented: description, all flags with defaults, one example
- [ ] No interactive prompts anywhere in the script
- [ ] Structured data written to stdout; all other output to stderr
- [ ] Exit code 0 on success, non-zero on any failure
- [ ] Distinct exit codes for distinct failure types if there are multiple
      (e.g. 1 = missing input, 2 = invalid format, 3 = network error)
- [ ] Output size is bounded — if output could be large, default to a
      summary or a row limit, and support `--output FILE` or `--limit N`
- [ ] Running the script twice with the same inputs does not fail
- [ ] Script is referenced from the correct step in SKILL.md with the
      exact command to run it, e.g.:
        ```bash
        uv run scripts/process.py --output results.json input.csv
        ```

### Validator checklist

- [ ] Exits with a non-zero code on every failure condition
- [ ] Every error message states both what failed and what was expected.
      Bad:  "Validation failed"
      Good: "Field 'customer_id' not found. Available fields: id, name, email"
- [ ] Error messages are specific enough for the agent to self-correct
      without asking the user. The agent's next action should be obvious
      from the message alone.
- [ ] The validator does not write, delete, or modify any files or state.
      It reads and checks only.
- [ ] Referenced from SKILL.md at the exact step it guards, with an
      explicit instruction for what to do on failure:
        ```bash
        uv run scripts/validate_output.py results.json
        # If this fails: read the error message, fix the issue it describes,
        # and re-run the validator before proceeding.
        ```
