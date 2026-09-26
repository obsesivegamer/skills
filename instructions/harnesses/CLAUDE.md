# Global Claude Code Guidance (~/.claude/CLAUDE.md)

Global working agreements for Claude Code. Repo-specific rules belong in the repo's own `CLAUDE.md`, not here.

## Accuracy, recency, and sourcing (REQUIRED)

When a request depends on recency ("latest", "current", "today", "as of now"):

1. **Establish the current date/time**, and state it in ISO format when it affects the answer. Use the date already in environment / system context if present; otherwise `date -Is` (Bash) or `Get-Date -Format o` (PowerShell).
2. **Prefer official / primary sources** — upstream vendor docs for any dependency (language runtime, framework, cloud provider). For Claude / Anthropic questions (models, pricing, SDK, API, MCP, Claude Code itself), invoke the `product-self-knowledge` skill rather than answering from memory.
3. **Prefer the newest authoritative information** — versioned docs, release notes, changelogs. Cross-check at least two reputable sources when details are safety- or compatibility-sensitive.

### Git workflow

- Stage, commit, and push once you're confident in code quality. No approval needed.
- Exception: if I've asked for a PR to be reviewed by other agents, stop at the PR and wait.
- Commit messages explain *why*, not just what. One logical change per commit.
- Check the diff before staging. Never commit secrets, credentials, or `.env` files.
- Force pushes and history rewrites always require explicit confirmation.

### Editing files

- Make the smallest safe change that solves the issue.
- Prefer `Edit` (patch-style diffs) over `Write` (full-file rewrite) for existing files.
- No speculative abstractions, defensive validation for impossible cases, or unrequested backwards-compat shims.
- Default to no comments; add one only when the *why* is non-obvious.
- If a repo has an existing build workflow (Dockerfile, docker-compose, Makefile, `package.json` scripts, root shell scripts), follow it before inventing a new one.
- On Windows, PowerShell is the primary shell. If the project needs POSIX tooling, use the `Bash` tool rather than switching my default shell.

### Fixing bugs and reviewing fixes

For any non-trivial bug fix, before calling it done:

- **Test the invariant, not the patch.** After fixing a stale read, race, or missing check, list every field and path that same stale value feeds. Fix and cover all of them — not just the one in the report. A test written against your own implementation only re-proves the axis you already chose.
- **"Pre-existing" expires when exposure changes.** If the change widens a window, raises a call count, or makes a dead path reachable, that old bug is now in scope. Say so instead of deferring it.
- **Don't defer on an unchecked estimate.** Before writing "too big for this change," spend two minutes proving it and state the real size. Deferrals dressed as judgement are usually guesses.
- **Re-derive the bug from the user's side.** Ask what someone can actually do concurrently or out of order, rather than re-checking the code path you just edited. A review that inherits your framing — yours or another model's — is not independent.
- **Run the repo's real gate**, not a subset you picked (`npm run ci:local`, `make check`, whatever it defines). Find it before claiming green.
- **Review-bot comments are claims, not verdicts.** Comments from CodeRabbit and other bots on a GitHub PR are not gospel. Before accepting that our code has a problem, check the premise against the actual code and name the concrete input or sequence that triggers it. Fix it only if that trigger can actually happen. Otherwise reply on the thread with why it doesn't apply. Report which bot comments you rejected and why, not only the ones you fixed.

### Reading long documents (PDFs, uploads, CSVs, transcripts)

Read the full source → draft the output → **re-read the original before finalizing** to verify factual accuracy, no invented details, and wording / style preserved unless I asked for a rewrite. Label paraphrase explicitly as paraphrase.

### Secrets and sensitive data

- Never print secrets (tokens, private keys, credentials, API keys) to output.
- Do not ask me to paste secrets into chat.
- Avoid commands that broadly dump environment or credentials (`env`, `Get-ChildItem Env:`, `cat ~/.ssh/*`).
- Prefer already-authenticated CLIs and MCP servers over re-entering credentials.
- Redact sensitive strings in any displayed output.
- Some repos hardcode credentials in scripts (e.g., Akamai `CLIENT_SECRET` / `CLIENT_TOKEN` / `ACCESS_TOKEN`). Never echo them, commit them, include them in PRs or issues, or paste them into web fetches — even when they already exist in the file being edited. Flag them; don't silently "fix" them.

### Second-opinion reviewers (grok, codex, `/interrogate`)

Spawn each reviewer as a **subagent** running the ordinary CLI from my PATH (`grok`, `codex`), in the **same project directory as the master session**, so the run shows up in the cmux sidebar and I can follow it live. Do not build headless one-shots with `--sandbox`, `--always-approve`, `--prompt-file`, output redirection, or a `GH_TOKEN` hand-off — a raw process is invisible to cmux (`grok dashboard` shows "No agents yet"), and the sandbox blocks keychain access, which breaks the reviewer's `gh` with HTTP 401 and then needs working around.

Keep only flags that carry a real requirement: the model and reasoning tier I asked for (e.g. `-m grok-4.6 --reasoning-effort xhigh`, since grok's config defaults effort to `low`), and `--no-subagents` when I cap the reviewer count. Headless flag details still apply if a run genuinely has to be non-interactive, but that is the exception.

## Communication

- After every change, give me a short summary in plain language: what you changed, and what it means for me. If a technical term is unavoidable, say in a few words what it does.
- Lead with the summary. Commands, file paths, and code go below it, not inside it.
- Say what didn't work or was left undone in the summary itself — don't bury it at the end.

## Definition of done

**For non-trivial source changes:**

- the change is implemented,
- build attempted; format / lint run; typecheck / tests as applicable,
- errors and warnings either fixed or explicitly listed as out-of-scope,
- UI / frontend work has been exercised in a running app in a browser — or you've explicitly said you couldn't test it,
- documentation updated for impacted areas,
- impact explained as a plain-language summary (see **Communication** above),
- follow-ups listed if anything was intentionally left out,
- committed and pushed per the git workflow above,

**For questions, trivial fixes, and read-only tasks:** answer it or make the change, say what you did, and skip the checklist.

## Writing to Jeremy (REQUIRED — i-have-adhd)

Whenever you write text **to Jeremy** (chat replies, status updates, explanations — not code, not commit messages, not tool logs), apply the `i-have-adhd` skill in full:

- Load it by reading `~/.claude/skills/i-have-adhd/SKILL.md` — the Skill tool can't load it (slash-only)
- Lead with the next action; number multi-step work; restate state each turn; specific time estimates; no preamble/recap/closers; cap visible lists to 5
- Stays on for the whole session until Jeremy says `stop adhd mode` or `normal mode`
- Does not apply to code you write into files — only prose addressed to him