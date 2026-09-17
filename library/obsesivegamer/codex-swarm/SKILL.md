---
name: codex-swarm
description: >-
  Use when running a Ben Davis–style Codex swarm on Mac via cmux: coordinator
  plus workers, shared BOARD.md, doom-loop timers (~60m check / ~120m kill), or
  when babysitting a PR to green. Not for a single short Codex edit.
---

# Codex swarm

Coordinator + workers + shared message board for long-horizon Codex jobs (inspired by Ben Davis’s Astra swarm review). Runs in **cmux → Codex CLI** tabs. Do **not** invent GPT-6 Astra — use current Codex models.

## When

- Swarm / coordinator / workers / shared board / theories → verify → consensus
- Hard research needing multiple Codex threads with kill timers
- Babysit PR to green (load poteto babysit — see below)
- **Not** a one-shot Codex edit (use normal cmux Codex launch)

## Paths in this skill

| File | Role |
|------|------|
| [references/BOARD.md](references/BOARD.md) | Shared message board template |
| [references/COORDINATOR.md](references/COORDINATOR.md) | Coordinator kickoff prompt |
| [references/WORKER.md](references/WORKER.md) | Worker prompt template |
| [references/BABYSIT_PR.md](references/BABYSIT_PR.md) | Pointer to poteto babysit playbook |

**Working copy:** for a live job, copy `references/BOARD.md` into the job cwd (or `~/Documents/codex-swarm/BOARD.md`) and point every tab at that path.

## Models / reasoning

- Default **low / medium** for coordination, board updates, spawning, bounded work
- **High** for mid synthesis and Babysit PR
- **Ultra / max** only when asked or clearly needed
- Pair with usage-aware / poteto routing + TokenTracker when choosing models

## Timer policy

- **~60m:** coordinator checks workers (cmux `capture-pane` / `read-screen` + BOARD.md)
- **~120m:** kill or reassign with no useful progress; log on board. No doom loops

## cmux launch

1. `cmux list-workspaces` → workspace titled **Codex CLI** (resolve by title, not a frozen index)
2. New tabs with `--focus false`, human titles: `swarm-coordinator`, `swarm-worker-1`, …
3. cwd: job repo (or a durable swarm folder holding the live BOARD.md)
4. Start Codex (`~/.local/bin/codex` or Homebrew), paste filled COORDINATOR / WORKER prompts
5. Tell the human **workspace title + tab title + cwd** — never bare `surface:N`
6. Poll via `capture-pane` / `read-screen`; the board file is source of truth

Prefer the cmux skill in this library for CLI details.

## Babysit PR

Canonical playbook (do **not** paraphrase from videos):

`library/unconfirmed/poteto-mode/playbooks/babysit.md`

(also linked from [references/BABYSIT_PR.md](references/BABYSIT_PR.md))

Modes: `drive` / `background` / `threads-only` / `check`. **Never merge** from babysit — landing is `playbooks/shipping.md` after an explicit merge/land/ship ask.

## Phase 2 (not in this skill)

Docker Compose sandbox (gateway blocklist / judge / monitor) for web-poisoned tasks is **out of scope**. Do not scaffold unless asked.

## Anti-patterns

- Silent `codex exec` with no cmux tab
- New top-level cmux workspace per worker (tabs inside **Codex CLI**)
- Merging without explicit ship/merge request
- Assuming Astra/GPT-6 exists when the picker only shows current models
