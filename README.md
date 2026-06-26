# Codex Skill Catalog

Generate a clean Markdown and JSON catalog for local Codex-style skills, plugins, and agent workspace setup.

This is an unofficial, local-first developer utility. It scans `SKILL.md` files, extracts a readable skill index, checks for missing metadata, and optionally inspects `~/.codex/config.toml` section names without printing secret values.

## Why This Exists

Agent workflows are getting messy in a very specific way: after a few weeks, you may have custom skills, bundled plugin skills, copied prompt packs, local scripts, MCP server configs, and half-forgotten experiments. The actual question becomes:

- What skills do I have?
- Which ones have reference folders or scripts?
- Which skills are missing a clear trigger/use-case line?
- Can I generate a Markdown inventory before migrating machines or sharing my setup?
- Can I inspect the workspace without leaking tokens or auth files?

`codex-skill-catalog` is the boring but useful answer.

## Features

- Scan one or more Codex-style skill roots.
- Extract skill directory name, `SKILL.md` title, first description paragraph, trigger/use-case hint, line count, and reference-folder presence.
- Detect duplicate skill names across roots.
- Inspect config TOML section names without printing values.
- Generate a Markdown catalog for GitHub, Obsidian, or migration notes.
- Generate a standalone HTML dashboard with summary cards and searchable-by-browser tables.
- Generate JSON inventory for scripts and automation.
- Zero runtime dependencies.
- Standard-library tests.

## Quick Start

Run directly from source:

```bash
git clone https://github.com/StaryMoon/codex-skill-catalog.git
cd codex-skill-catalog
PYTHONPATH=src python -m codex_skill_catalog.cli \
  --root examples/skills \
  --config examples/config.sample.toml \
  --output examples/CODEX_SKILL_CATALOG.sample.md \
  --json examples/codex-skill-catalog.sample.json \
  --html examples/CODEX_SKILL_CATALOG.sample.html
```

Scan your real local setup:

```bash
PYTHONPATH=src python -m codex_skill_catalog.cli \
  --root ~/.codex/skills \
  --output CODEX_SKILL_CATALOG.md \
  --json codex-skill-catalog.json \
  --html codex-skill-catalog.html
```

After package install:

```bash
cscat --root ~/.codex/skills --output CODEX_SKILL_CATALOG.md --json catalog.json --html catalog.html
```

## Example Report

```markdown
# Codex Skill Catalog

## Summary

- Skill roots scanned: **1**
- Skills found: **2**
- Config path: `examples/config.sample.toml`
- Config sections detected: **2**

## Skills

| Skill | Title | References | Lines | Warnings |
| --- | --- | ---: | ---: | ---: |
| `paper-briefing` | Paper Briefing | yes | 7 | 0 |
| `repo-doctor` | Repo Doctor | no | 5 | 0 |
```

## CLI

```bash
usage: codex-skill-catalog [-h] [--root ROOT] [--config CONFIG]
                           [--output OUTPUT] [--json JSON] [--html HTML]
                           [--title TITLE] [--print]

Generate a local Markdown and JSON catalog for Codex-style skills.
```

Important flags:

- `--root`: skill root to scan. Can be passed multiple times.
- `--config`: TOML config path. Defaults to `~/.codex/config.toml`.
- `--output`: Markdown report path.
- `--json`: optional JSON inventory path.
- `--html`: optional standalone HTML dashboard path.
- `--print`: print Markdown to stdout.

## Privacy Model

The tool intentionally keeps the privacy surface small:

- It reads skill Markdown metadata.
- It lists TOML section names only.
- It does not print token values, cookies, API keys, auth files, or environment variables.
- It does not upload anything.

Still, review generated reports before publishing because local file paths may reveal usernames or workspace names.

## Good Use Cases

- Build a shareable catalog of your local agent skills.
- Audit old custom skills and find ones with unclear trigger instructions.
- Prepare a migration checklist before moving to a new machine.
- Generate an Obsidian note of your AI coding toolchain.
- Keep a lightweight snapshot of your personal agent environment in a private repo.

## Relationship To Codex

This project is unofficial and independent. It is designed around the common `SKILL.md` pattern used by local agent workflows, including Codex-style skill folders. It does not vendor or modify any OpenAI code.

## Roadmap

- [ ] Add plugin-cache scanning mode.
- [ ] Add config diff reports between two machines.
- [x] Add home-directory redaction in generated reports.
- [ ] Add GitHub Action example for private dotfiles inventory.
- [x] Add HTML report output.

## License

MIT.
