---
name: codex-swarm
description: >-
  Run a Ben Davis-style coordinator and worker swarm in Codex Desktop on Mac,
  with shared evidence, independent verification, and deadlines. Use for swarm
  requests and long parallel jobs; use cmux only when explicitly requested.
---

# Codex swarm

Run a coordinator with native subagents in the current Codex Desktop task. The coordinator delegates, checks evidence, and keeps workers moving. It owns the board; workers own separate reports. Use the model the user requests, after checking the session's available models.

## Desktop start

1. Read [COORDINATOR.md](references/COORDINATOR.md). Record the goal, acceptance criteria, absolute project path, allowed Git actions, model, reasoning, and time budget.
2. Create a unique run directory inside the active project, such as `.swarm/<run-id>/`. Copy [BOARD.md](references/BOARD.md) there. Set one absolute board path for everyone.
3. Delegate independent work using the session's native subagent tools. Start with two workers, within the available concurrency limit. Use [WORKER.md](references/WORKER.md) for assignments. The coordinator retains integration work while workers run.
4. Workers write only their assigned report and assigned implementation files. The coordinator alone edits the board. Pass evidence between workers for independent verification before accepting a claim.
5. Use bounded waits and real timestamps to check deadlines while the coordinator runs. End with evidence, unresolved issues, and all workers accounted for.

For a first run, use [TRIAL.md](references/TRIAL.md). No cmux installation is required for Desktop mode.

Native subagents and sidebar tasks are different. Create separate sidebar tasks only when the user explicitly requests new tasks. Then use the app's project discovery, task creation, messaging, and wait tools, and record each returned task ID. Do not promise a hard stop unless that execution mode exposes a supported interrupt operation. Native subagents have an interrupt tool in this session; sidebar task messaging is not equivalent to interrupting execution.

## Shared files and computer use

- The coordinator writes `BOARD.md`; each worker writes `workers/<worker-name>.md`. Workers send urgent updates through native messages. Reports include timestamped claims, commands or artifact paths, uncertainty, and next actions.
- Give implementation workers disjoint file ownership. Native subagents share the working directory; spawning does not create an isolated worktree. Serialize overlapping changes or deliberately provision worktrees when needed.
- Assign one Mac UI operator at a time on the board. Release the assignment before handing control to another worker. Browser tabs should also have explicit owners.
- Load the Browser or Computer Use skill before using it. Confirm capabilities with a harmless read. Each worker must check its own tool availability; do not assume it inherits every desktop capability.
- Verify the actual output through the browser or target app when the task involves UI. A code review alone is not visual verification. Report blocked access honestly.

## When

- Swarm / coordinator / workers / shared board / theories → verify → consensus
- Hard research needing multiple Codex threads with kill timers
- Babysit PR to green (load poteto babysit — see below)
- **Not** a one-shot Codex edit; use the current task normally.

## Paths in this skill

| File | Role |
|------|------|
| [references/BOARD.md](references/BOARD.md) | Shared message board template |
| [references/COORDINATOR.md](references/COORDINATOR.md) | Coordinator kickoff prompt |
| [references/WORKER.md](references/WORKER.md) | Worker prompt template |
| [references/BABYSIT_PR.md](references/BABYSIT_PR.md) | Pointer to poteto babysit playbook |

**Working copy:** keep run artifacts inside the active project and point every worker at the same absolute board path.

## Models / reasoning

- For the user's Astra workflow, select `gpt-6-astra` when exposed by the session. If unavailable, report that before substituting another model.
- Default **low / medium** for coordination, board updates, spawning, bounded work
- **High** for mid synthesis and Babysit PR
- **Ultra / max** only when asked or clearly needed
- Set worker model and reasoning through supported spawn options. Full-history forks can inherit the parent settings; use a bounded or fresh context when the tool requires it for overrides. Record the actual request, not just prose saying which model to use.

## Timer policy

- Record each worker's start, check deadline, and stop deadline as absolute ISO timestamps.
- **60m:** inspect status and evidence, then narrow or redirect a stuck worker.
- **120m:** interrupt the worker at the deadline, preserve its partial report, and reassess before starting a replacement with a fresh budget.
- A useful new result does not silently reset the deadline. Record any explicit extension and why it is justified.
- These are active-coordinator deadlines, not an OS watchdog. Sleep, suspension, or a stopped coordinator can delay enforcement. Do not claim unattended enforcement from prompt text alone. Scheduled follow-ups require the app's automation tool and are not hard real-time timers.
- A short trial can use shorter, explicitly recorded deadlines.

## cmux launch

Only use this route when the user explicitly requests cmux. Load the cmux skill and verify its current commands. Keep the same board ownership, report files, and UI ownership rules.

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

- Silently substituting CLI processes for the requested Desktop workflow
- In cmux mode, creating a top-level workspace per worker instead of tabs inside **Codex CLI**
- Merging without explicit ship/merge request
- Selecting a model without checking the session's available model IDs
