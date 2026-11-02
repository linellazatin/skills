# Use scc for repository measurements

These examples were checked with scc 4.1.0. Inspect the installed `--version` and `--help`; older releases may lack configuration controls or history reports. Do not assume development README options exist in the installed release.

## Availability and installation

Scc is a standalone executable, not an indexing service. Prebuilt executables do not require a Go toolchain or Python environment. Basic scans read current files; optional history reports perform additional analysis whose cost depends on the commit window and repository. No background server or MCP setup is needed.

Check an existing installation:

```sh
scc --version
scc --help
```

If missing, continue static inspection and omit measurements. Offer the appropriate installation instructions, but execute them only with separate authorization. For macOS with Homebrew:

```sh
brew install scc
```

Alternatively, select the correct OS/architecture from [official releases](https://github.com/boyter/scc/releases), verify any published checksum, and place the executable on an authorized executable path. Prebuilt installation needs no Go compiler; building from source does. See [upstream installation guidance](https://github.com/boyter/scc#install) for other environments. Do not install into the inspected project or modify shell configuration automatically.

## Choose a reproducible scope

Run from the established root; `.` below means that root. The examples disable automatic scc configuration with `--no-config` and emit only to stdout. Inspect `.sccconfig` and environment-selected configuration as data if relevant; reproduce intentional measurement settings through verified CLI flags and disclose them. Do not silently load settings that change filters or output destinations.

If required controls are unsupported, inspect the installed version's defaults/configuration and construct a supported, side-effect-bounded invocation, or omit the affected measurement. Do not simply remove a safety control and run blindly. Avoid `--output`, `--report`, output-file redirection, and file-producing `--format-multi` without writing authorization.

Normal scans respect `.gitignore`, `.ignore`, and `.sccignore`; they are not equivalent to `git ls-files`. Relevant untracked files can be counted, and tracked-but-ignored content can be absent. Hidden files may be included. Inspect workspace boundaries, nested ignore rules, submodules, and symlinks before claiming complete coverage; do not enable traversal outside the requested root automatically.

## Summary and per-file evidence

```sh
# Language-level summary without cost estimates or processed-byte totals
scc --no-config --no-cocomo --no-size .

# Per-file output, sorted by code within the rendered groups
scc --no-config --no-cocomo --no-size --by-file --sort code .

# Structured per-file counts for grouping and interpretation
scc --no-config --by-file --format json .
```

Use JSON, not the rendered table, for programmatic aggregation. In the checked version, the normal JSON output is a language-summary array; with `--by-file`, its `Files` entries include `Location`, `Code`, `Comment`, `Blank`, and `Complexity`. History JSON is a different report object. Verify the actual schema before processing it. Table paths may be truncated; use file locations from structured output for references. For a global largest-file list, flatten and sort the file records rather than treating grouped table output as globally ranked.

Adapt exclusions to the actual repository, not a universal list. This example excludes known dependency/build trees and heuristically generated files:

```sh
scc --no-config --by-file --format json --exclude-dir vendor,dist --no-gen .
```

In 4.1.0, explicit `--exclude-dir` values are added to the built-in `.git`, `.hg`, and `.svn` exclusions. Confirm installed behavior before relying on that rule. Do not exclude a first-party directory just because its name appears in an example. If useful, inspect generated/vendor content separately rather than silently treating it as nonexistent.

## Interpret the counts

- `Lines`, `Blank`, `Comment`, and `Code` are physical-line classifications under scc's rules, not executable statements or semantic importance. Language categories can include Markdown, configuration, and license content classified as code; keep those separate from production source in your interpretation.
- The checked version excludes several lockfiles by default, including `package-lock.json` and `Cargo.lock`; still read relevant lockfiles for dependency questions. Unsupported languages and binary files can be absent from counts; enumerate unknown content separately, or use a verified supported option such as `--count-unsupported` and disclose the change.
- Generated/minified detection is heuristic and optional. `--no-gen` enables generated detection and removes detected files; ordinary scans do not promise to exclude all generated/minified content. Inspect candidates and markers before relying on a filtered total.
- Duplicate files count by default; `--no-duplicates` changes that policy. Compare revisions/tools only with matching scope and duplicate/filter definitions. Physical newline counts from `wc -l` are not a substitute for source-code counts.
- Complexity is a file-level lexical estimate based on language-specific branch/loop patterns, not a parsed control-flow graph. Use it to select files for reading, cautiously within the same language; do not rank languages or declare defects from the score.
- If asked for a source-comment ratio, select the source-file population first and state the definition, for example `Comment / (Code + Comment)`. Exclude blank lines under that definition, report an undefined ratio when the denominator is zero, and do not mix standalone documentation into the numerator without disclosure. File counts do not establish test coverage.

## Requested history analysis

Run these only for a requested maintenance/history investigation. From the repository root, choose a bounded window; 50 commits below is an example, not a required analytical horizon:

```sh
scc --no-config --hotspots --depth 50 .
scc --no-config --coupling --depth 50 .

# Structured history evidence when needed
scc --no-config --hotspots --depth 50 --format json .
scc --no-config --coupling --depth 50 --format json .
```

Use separate invocations for hotspots and coupling. In 4.1.0, `--depth` defaults to 1000 and `0` requests all available history; avoid an unbounded walk by default. Inspect output warnings/errors and actual `window` fields, not just the requested depth. State HEAD/revision and available history; shallow or missing objects limit evidence, and a non-Git directory cannot provide these reports. Do not fetch missing history automatically.

**History is a different population:** reports analyze commits reachable from HEAD and committed content, not uncommitted edits or untracked files. In the checked implementation, history uses committed `.ignore`/`.sccignore` rules and does not share all working-tree scan filters. Do not assume `--exclude-dir`, extension filters, or generated-file exclusions carry over. Inspect/filter returned paths to the requested area and disclose that analytical restriction separately; it does not necessarily reduce the history walk's cost. Tracked content can remain in history even when now gitignored.

Hotspots combine HEAD complexity with change frequency in the window. Coupling identifies files that changed together; expected source/test or manifest/lockfile pairs can explain it. In 4.1.0, coupling omits pairs with fewer than two shared changes and excludes commits touching more than 30 classified files from pair counting, while retaining individual file totals. Its degree is `shared / (commitsA + commitsB - shared)`, not a directional probability. Inspect these rules before interpreting missing pairs or percentages. Neither report proves defects or runtime dependencies. Read the candidate source and representative changes before drawing conclusions; do not reproduce contributor identities when irrelevant.

The checked 4.1.0 report path reads Git objects directly and prints to stdout unless file output is explicitly selected; it does not require executing project code. For another tool/version, inspect behavior before treating it as read-only. If side effects cannot be bounded, retain source-only triage and state the limitation. Any supplementary Git commands must also avoid optional locks/index refresh, filesystem-monitor hooks, external diff, and text-conversion execution.

## References and evidence limits

- [scc documentation](https://github.com/boyter/scc): installation, counting, output formats, and complexity limitations.
- [Checked 4.1.0 source](https://github.com/boyter/scc/tree/v4.1.0): `config.go` defines default-filter merging; `processor/history.go`, `history_ignore.go`, `history_hotspots.go`, and `history_coupling.go` define the inspected history behavior.

These instructions and command probes do not establish cross-platform performance, native skill activation, or model instruction-following. Missing tools or unavailable history leave those observations absent, not evidence that the repository is defective.
