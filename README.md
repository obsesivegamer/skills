# Jeremy's AI workflow

This private repository is the source of truth for my reusable AI agent skills and global instruction files. I can clone it on a new computer and link the same skills into each coding agent I use.

TokenTracker is used to discover and download skills. Skills become part of this setup only after they are copied into this repository and recorded in the manifest.

## Supported tools

The bootstrap script installs skill links for:

- Codex at `~/.codex/skills`
- Claude Code at `~/.claude/skills`
- Gemini CLI at `~/.gemini/skills`
- OpenCode at `~/.config/opencode/skills`
- Cursor at `~/.cursor/skills`
- the shared Agent Skills location at `~/.agents/skills`

Grok Build support is planned, but its global skills location has not been confirmed. The bootstrap script does not configure it yet.

## Repository structure

```text
.
├── .agents/skills/          # Flat skill names linked to the library
├── instructions/harnesses/  # Snapshots of global agent instructions
├── library/                 # Vendored skills grouped by source
│   ├── anthropics/
│   ├── cursor/
│   ├── davidondrej/
│   ├── mattpocock/
│   ├── obra/
│   └── unconfirmed/
├── manifests/
│   └── skills.lock.json     # Source, ownership, hash, and review metadata
├── scripts/
│   ├── bootstrap            # Install skill links safely
│   ├── doctor               # Report missing or incorrect links
│   └── import-tokentracker  # Initial TokenTracker migration helper
└── tests/
```

Each canonical skill lives at `library/<provider>/<skill>/`. The corresponding entry in `.agents/skills/` is a relative symlink. This keeps skills grouped by their source in Git while presenting the flat directory layout expected by agent tools.

The files under `instructions/harnesses/` are tracked snapshots. The current bootstrap script does not replace or link live `AGENTS.md` or `CLAUDE.md` files.

## Set up a new computer

Requirements:

- Git
- Python 3
- GitHub authentication that can access this private repository

Clone the repository:

```bash
mkdir -p ~/Documents/GitHub
git clone https://github.com/obsesivegamer/skills.git ~/Documents/GitHub/skills
cd ~/Documents/GitHub/skills
```

Preview the links that bootstrap would create:

```bash
./scripts/bootstrap
```

If the preview reports no conflicts, create the links:

```bash
./scripts/bootstrap --apply
```

Bootstrap never replaces a real file or directory. It also refuses to replace an existing symlink unless you explicitly adopt existing symlinks:

```bash
./scripts/bootstrap --apply --adopt-existing-symlinks
```

Run the health check afterward:

```bash
./scripts/doctor
python3 -m unittest discover -s tests -v
```

## Add a skill

For a skill you own:

1. Add its folder under `library/<your-name>/<skill-name>/`.
2. Add a relative symlink at `.agents/skills/<skill-name>`.
3. Add its metadata and content hash to `manifests/skills.lock.json`.
4. Run `./scripts/bootstrap --apply`, `./scripts/doctor`, and the tests.

For a third-party skill, also record its repository, upstream path, revision, license, and whether you modified it. Do not mix an external tracking entry with a vendored copy. Each skill should have one ownership policy.

## TokenTracker imports

`scripts/import-tokentracker` was built for the initial migration into an empty destination. It copies downloaded skills into provider folders, creates the flat links, and writes the manifest. It stops without changing anything if a destination already exists.

Preview an import:

```bash
./scripts/import-tokentracker \
  --source ~/.tokentracker/skills/managed \
  --cache ~/.tokentracker/skills/registry.json \
  --repo "$PWD"
```

Add `--apply` only after reviewing the preview. This importer is not the upstream update command.

## Updating third-party skills

The manifest currently marks imported skills as `vendored-pending-review`. Before automating updates, each entry needs an immutable upstream revision, confirmed license, and modification status.

Until update tooling is added, review upstream changes manually and copy only the changes you want. Recompute the content hash, update the manifest, run the health check and tests, then commit the skill and manifest together.

## Safety rules

- Git is authoritative. TokenTracker is a discovery tool, not the live source.
- Run bootstrap without `--apply` first.
- Bootstrap stops on conflicts and does not replace real files or directories.
- Review third-party licenses before redistributing skills or making this repository public.
- Keep secrets and machine-specific credentials out of Git.

## Current status

- 61 skills are tracked in `manifests/skills.lock.json`.
- 366 links are installed across six skill directories on the original Mac.
- Global Codex and Claude instruction snapshots are included.
- Automated upstream synchronization and Grok Build setup remain pending.
