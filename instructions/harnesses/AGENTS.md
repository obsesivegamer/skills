# Global Codex Guidance (~/.codex/AGENTS.md)

Global working agreements for Codex CLI.

## Accuracy, recency, and sourcing (REQUIRED)

When a request depends on recency (e.g., "latest", "current", "today", "as of now"):

1. **Establish the current date/time** and state it explicitly in ISO format.
   - Preferred: `date -Is` (timestamp).

2. **Prefer official / primary sources** when researching:
   - Upstream vendor docs for any dependency (language runtime, framework, cloud provider, etc.)

3. **Prefer the most recent authoritative information**:
   - Use the newest versioned docs, release notes, or changelogs.
   - Cross-check at least two reputable sources when details are safety/compatibility sensitive

### Web search policy

- Enable and use web search only when it materially improves correctness (e.g., up-to-date APIs, recent advisories, release notes).
- Prefer official docs and primary sources; otherwise use Context7 MCP or reputable, widely-cited references.
- Record source dates (publish/release dates) when relevant.

## Default autonomy and safety

- Default to read-only exploration and analysis.
- When edits are needed, prefer **workspace-scoped** write access and keep changes inside the repo.
- When interacting with remote APIs, use read-only calls by default. Perform write operations only when the user explicitly authorizes them; preview or dry-run first when supported. Never make destructive calls to remote APIs or production data sources.

### File deletion boundary (REQUIRED)

- Never delete, trash, unlink, erase, purge, or run cleanup operations on any file or directory outside the active project workspace.
- This prohibition applies even when the user requests the deletion. Explain that the target is outside the project workspace and leave it unchanged.
- Do not evade this boundary through scripts, glob expansion, recursive commands, symlink traversal, temporary relocation, or tools that move items to Trash.
- Before deleting anything inside the project workspace, resolve and verify the exact target path. If the workspace boundary or target is uncertain, do not delete it.

### Editing files

- Make the smallest safe change that solves the issue.
- Prefer patch-style edits (small, reviewable diffs) over full-file rewrites.
- After making changes, run the project’s standard checks when feasible (format/lint, unit tests, build/typecheck).

### Reading project documents (PDFs, uploads, long text, CSVs, etc)

- Read the full document first.
- Draft the output.
- **Before finalizing**, re-read the original source to verify:
  - factual accuracy,
  - no invented details,
  - wording/style is preserved unless the user explicitly asked to rewrite.
- If paraphrasing is required, label it explicitly as a paraphrase.

### Secrets and sensitive data

- Never print secrets (tokens, private keys, credentials) to terminal output.
- Do not request users paste secrets.
- Avoid commands that might expose secrets (e.g., dumping env vars broadly, `cat ~/.ssh/*`).
- Prefer existing authenticated CLIs; redact sensitive strings in any displayed output.

## Baseline workflow

- Start every task by determining:
  1. Goal + acceptance criteria.
  2. Constraints (time, safety, scope).
  3. What must be inspected (files, commands, tests, docs).
  4. Whether the request depends on **recency** (if yes, apply the "Accuracy, recency, and sourcing" rules).
  5. If requirements are ambiguous, ask targeted clarifying questions before making irreversible changes.

## CONTINUITY.md (CONDITIONAL)

Use a single continuity file for the current workspace, `.agent/CONTINUITY.md`, when work is multi-session, multi-agent, likely to be compacted, or complex enough that a durable handoff is valuable.

- When it exists, read `.agent/CONTINUITY.md` at the start of work before acting.
- Treat it as a bounded, high-signal briefing for future contributors; do not duplicate the chat transcript or routine tool output.
- Do not create or update it for trivial, one-shot tasks unless there is a meaningful decision or state worth preserving.

### File Format

Update `.agent/CONTINUITY.md` only when there is a meaningful delta in:

  - `[PLANS]`: "Plans Log" is a guide for the next contributor as much as checklists for you.
  - `[DECISIONS]`: "Decisions Log" is used to record all decisions made.
  - `[PROGRESS]`: "Progress Log" is used to record course changes mid-implementation, documenting why and reflecting upon the implications.
  - `[DISCOVERIES]`: "Discoveries Log" records optimizer behavior, performance tradeoffs, unexpected bugs, or inverse/unapply semantics that shaped the approach. Capture short evidence snippets when useful.
  - `[OUTCOMES]`: "Outcomes Log" is used at completion of a major task or the full plan, summarizing what was achieved, what remains, and lessons learned.

### Anti-drift / anti-bloat rules

- Facts only, no transcripts, no raw logs.
- Every entry must include:
  - a date in ISO timestamp (e.g., `2026-01-13T09:42Z`)
  - a provenance tag: `[USER]`, `[CODE]`, `[TOOL]`, `[ASSUMPTION]`
  - If unknown, write `UNCONFIRMED` (never guess). If something changes, supersede it explicitly (don't silently rewrite history).
- Keep the file bounded, short and high-signal (anti-bloat). 
- If sections begin to become bloated, compress older items into milestone (`[MILESTONE]`) bullets.

## Command-line transparency (RISK-BASED)

- Before destructive, remote, privileged, expensive, or long-running commands, show the user the **full command** that will be run.
- Include the working directory when it materially affects the command.
- For multi-step workflows, show each command separately and in execution order.
- After the command finishes, summarize the result concisely and call out failures, warnings, or any command that required elevated permissions.
- Never display secrets, credentials, private keys, or tokens. If a command would expose sensitive values, explain the purpose and use a safe, redacted alternative.

## Definition of done

A task is done when:

- the requested change is implemented or the question is answered,
  - verification is provided:
  - build attempted (when source code changed),
  - linting run (when source code changed),
  - errors/warnings addressed (or explicitly listed and agreed as out-of-scope),
  - plus tests/typecheck as applicable,
- documentation is updated when behavior, setup, APIs, or operational guidance changes,
- impact is explained (what changed, where, why),
- follow-ups are listed if anything was intentionally left out.
- `.agent/CONTINUITY.md` is updated if the change materially affects goal/state/decisions.


