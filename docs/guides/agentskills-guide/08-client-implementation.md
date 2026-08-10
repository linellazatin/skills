# Adding Skills Support to Your Agent

> Source: https://agentskills.io/client-implementation/adding-skills-support.md

A guide for adding Agent Skills support to an AI agent or development tool.

This guide covers the full lifecycle: discovering skills, telling the model about them, loading their content into context, and keeping that content effective over time.

The implementation details vary based on two factors:
- **Where do skills live?** A locally-running agent can scan the filesystem. A cloud-hosted or sandboxed agent needs an alternative discovery mechanism.
- **How does the model access skill content?** If the model has file-reading capabilities, it can read `SKILL.md` files directly. Otherwise, provide a dedicated tool or inject skill content programmatically.

---

## The Core Principle: Progressive Disclosure

Every skills-compatible agent follows the same three-tier loading strategy:

| Tier            | What's loaded                | When                                  | Token cost                   |
| --------------- | ---------------------------- | ------------------------------------- | ---------------------------- |
| 1. Catalog      | Name + description           | Session start                         | ~50–100 tokens per skill     |
| 2. Instructions | Full `SKILL.md` body         | When the skill is activated           | < 5000 tokens (recommended)  |
| 3. Resources    | Scripts, references, assets  | When the instructions reference them  | Varies                       |

The model sees the catalog from the start, so it knows what skills are available. When it decides a skill is relevant, it loads the full instructions. If those instructions reference supporting files, the model loads them individually as needed.

An agent with 20 installed skills doesn't pay the token cost of 20 full instruction sets upfront — only the ones actually used in a given conversation.

---

## Step 1: Discover Skills

At session startup, find all available skills and load their metadata.

### Where to Scan

Most locally-running agents scan at least two scopes:
- **Project-level** (relative to working directory): Skills specific to a project or repository
- **User-level** (relative to home directory): Skills available across all projects

Within each scope, scan both a client-specific directory and the `.agents/skills/` convention:

| Scope   | Path                                | Purpose                        |
| ------- | ----------------------------------- | ------------------------------ |
| Project | `<project>/.<your-client>/skills/`  | Your client's native location  |
| Project | `<project>/.agents/skills/`         | Cross-client interoperability  |
| User    | `~/.<your-client>/skills/`          | Your client's native location  |
| User    | `~/.agents/skills/`                 | Cross-client interoperability  |

`.agents/skills/` has emerged as a widely-adopted convention for cross-client skill sharing. Scanning it means skills installed by other compliant clients are automatically visible to yours.

> **Note**: Some implementations also scan `.claude/skills/` for pragmatic compatibility. Other additional locations include ancestor directories up to the git root (useful for monorepos), XDG config directories, and user-configured paths.

### What to Scan For

Look for **subdirectories containing a file named exactly `SKILL.md`**:

```
~/.agents/skills/
├── pdf-processing/
│   ├── SKILL.md          ← discovered
│   └── scripts/
│       └── extract.py
├── data-analysis/
│   └── SKILL.md          ← discovered
└── README.md             ← ignored (not a skill directory)
```

Practical scanning rules:
- Skip `.git/` and `node_modules/`
- Optionally respect `.gitignore`
- Set reasonable bounds (e.g., max depth 4–6 levels, max 2000 directories)

### Handling Name Collisions

When two skills share the same `name`, apply a deterministic precedence rule.

**Universal convention: project-level skills override user-level skills.**

Within the same scope, first-found or last-found is acceptable — pick one and be consistent. Log a warning when a collision occurs.

### Trust Considerations

Project-level skills come from the repository being worked on, which may be untrusted (e.g., a freshly cloned open-source project). Consider gating project-level skill loading on a trust check — only load them if the user has marked the project folder as trusted. This prevents untrusted repositories from silently injecting instructions into the agent's context.

### Cloud-Hosted and Sandboxed Agents

- **Project-level skills**: often the easiest case — if the agent operates on a cloned repo, project-level skills travel with the code.
- **User-level / organization-level skills**: don't exist in the sandbox. Provision from an external source — clone a config repo, accept skill URLs through settings, or let users upload skill directories through a web UI.
- **Built-in skills**: package as static assets within the deployment artifact.

---

## Step 2: Parse `SKILL.md` Files

### Frontmatter Extraction

A `SKILL.md` file has two parts: YAML frontmatter between `---` delimiters, and a markdown body after the closing delimiter.

To parse:
1. Find the opening `---` at the start of the file and the closing `---` after it
2. Parse the YAML block between them — extract `name` and `description` (required), plus any optional fields
3. Everything after the closing `---`, trimmed, is the body content

### Handling Malformed YAML

Skills authored for other clients may contain technically invalid YAML that their parsers happen to accept. The most common issue: unquoted values containing colons:

```yaml
# Technically invalid YAML
description: Use this skill when: the user asks about PDFs
```

Consider a fallback that wraps such values in quotes or converts them to YAML block scalars before retrying. This improves cross-client compatibility at minimal cost.

### Lenient Validation

Warn on issues but still load the skill when possible:
- Name doesn't match parent directory → warn, load anyway
- Name exceeds 64 characters → warn, load anyway
- Description is missing or empty → **skip the skill** (essential for disclosure), log the error
- YAML is completely unparseable → **skip the skill**, log the error

Record diagnostics so they can be surfaced to the user, but don't block skill loading on cosmetic issues.

### What to Store

At minimum, each skill record needs:

| Field       | Description                            |
| ----------- | -------------------------------------- |
| `name`      | From frontmatter                       |
| `description` | From frontmatter                     |
| `location`  | Absolute path to the `SKILL.md` file   |

Store in an in-memory map keyed by `name` for fast lookup during activation.

You can also store the **body** at discovery time, or read it from `location` at activation time. Storing it makes activation faster; reading at activation time uses less memory and picks up changes to skill files between activations.

The skill's **base directory** (parent of `location`) is needed to resolve relative paths — derive it from `location` when needed.

---

## Step 3: Disclose Available Skills to the Model

Tell the model what skills exist without loading their full content. This is tier 1 of progressive disclosure.

### Building the Skill Catalog

Include `name`, `description`, and optionally `location` for each discovered skill. XML, JSON, or a bulleted list all work:

```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extract PDF text, fill forms, merge files. Use when handling PDFs.</description>
    <location>/home/user/.agents/skills/pdf-processing/SKILL.md</location>
  </skill>
  <skill>
    <name>data-analysis</name>
    <description>Analyze datasets, generate charts, and create summary reports.</description>
    <location>/home/user/project/.agents/skills/data-analysis/SKILL.md</location>
  </skill>
</available_skills>
```

The `location` field enables file-read activation and gives the model a base path for resolving relative references in the skill body (like `scripts/evaluate.py`). Each skill adds roughly 50–100 tokens to the catalog.

### Where to Place the Catalog

**System prompt section**: Add the catalog as a labeled section in the system prompt, preceded by brief instructions on how to use skills. Simplest approach, broadly compatible.

**Tool description**: Embed the catalog in the description of a dedicated skill-activation tool. Cleaner when you have a dedicated activation tool.

### Behavioral Instructions

Include a short instruction block telling the model how and when to use skills.

**If the model activates skills by reading files:**
```
The following skills provide specialized instructions for specific tasks.
When a task matches a skill's description, use your file-read tool to load
the SKILL.md at the listed location before proceeding.
When a skill references relative paths, resolve them against the skill's
directory (the parent of SKILL.md) and use absolute paths in tool calls.
```

**If the model activates skills via a dedicated tool:**
```
The following skills provide specialized instructions for specific tasks.
When a task matches a skill's description, call the activate_skill tool
with the skill's name to load its full instructions.
```

### Filtering

**Hide filtered skills entirely** from the catalog rather than listing them and blocking at activation time. Common reasons to filter:
- The user has disabled the skill in settings
- A permission system denies access
- The skill has opted out of model-driven activation

### When No Skills Are Available

If no skills are discovered, omit the catalog and behavioral instructions entirely. Don't show an empty `<available_skills/>` block — this would confuse the model.

---

## Step 4: Activate Skills

When the model or user selects a skill, deliver the full instructions into the conversation context. This is tier 2 of progressive disclosure.

### Model-Driven Activation

Most implementations rely on the model's own judgment. Two implementation patterns:

**File-read activation**: The model calls its standard file-read tool with the `SKILL.md` path from the catalog. No special infrastructure needed — simplest approach when the model has file access.

**Dedicated tool activation**: Register a tool (e.g., `activate_skill`) that takes a skill name and returns the content. Required when the model can't read files directly; optional but useful otherwise. Advantages:
- Control what content is returned (e.g., strip or preserve YAML frontmatter)
- Wrap content in structured tags for context management
- List bundled resources alongside instructions
- Enforce permissions or prompt for user consent
- Track activation for analytics

> **Tip**: If you use a dedicated activation tool, constrain the `name` parameter to the set of valid skill names (e.g., as an enum). This prevents the model from hallucinating nonexistent skill names. If no skills are available, don't register the tool at all.

### User-Explicit Activation

Users should also be able to activate skills directly. The most common pattern: a **slash command or mention syntax** (`/skill-name` or `$skill-name`) that the harness intercepts. The harness handles the lookup and injection — the model receives skill content without needing to take an activation action.

An autocomplete widget listing available skills as the user types can also make this discoverable.

### What the Model Receives

**Full file**: The model sees the entire `SKILL.md` including YAML frontmatter. Natural outcome with file-read activation.

**Body only (frontmatter stripped)**: The harness parses and removes the YAML frontmatter, returning only the markdown instructions. Most dedicated activation tools take this approach.

Both work in practice.

### Structured Wrapping

If you use a dedicated activation tool, consider wrapping skill content in identifying tags:

```xml
<skill_content name="pdf-processing">
# PDF Processing

## When to use this skill
Use this skill when the user needs to work with PDF files...

[rest of SKILL.md body]

Skill directory: /home/user/.agents/skills/pdf-processing
Relative paths in this skill are relative to the skill directory.

<skill_resources>
  <file>scripts/extract.py</file>
  <file>scripts/merge.py</file>
  <file>references/pdf-spec-summary.md</file>
</skill_resources>
</skill_content>
```

Benefits:
- Model can clearly distinguish skill instructions from other conversation content
- Harness can identify skill content during context compaction
- Bundled resources are surfaced to the model without being eagerly loaded

### Listing Bundled Resources

When a dedicated activation tool returns skill content, enumerate supporting files in the skill directory — but **do not eagerly read them**. The model loads specific files on demand when the skill's instructions reference them.

For large skill directories, cap the listing and note it may be incomplete.

### Permission Allowlisting

If your agent has a permission system that gates file access, **allowlist skill directories** so the model can read bundled resources without triggering user confirmation prompts on every file access.

---

## Step 5: Manage Skill Context Over Time

Once skill instructions are in the conversation context, keep them effective for the duration of the session.

### Protect Skill Content from Context Compaction

If your agent truncates or summarizes older messages when the context window fills up, **exempt skill content from pruning**. Skill instructions are durable behavioral guidance — losing them mid-conversation silently degrades performance without any visible error.

Common approaches:
- Flag skill tool outputs as protected so the pruning algorithm skips them
- Use structured tags from Step 4 to identify skill content and preserve it during compaction

### Deduplicate Activations

Track which skills have been activated in the current session. If the model or user attempts to load a skill already in context, skip re-injection to avoid the same instructions appearing multiple times.

### Subagent Delegation (Optional)

An advanced pattern supported by some clients: instead of injecting skill instructions into the main conversation, run the skill in a **separate subagent session**. The subagent receives the skill instructions, performs the task, and returns a summary to the main conversation.

Useful when a skill's workflow is complex enough to benefit from a dedicated, focused session.
