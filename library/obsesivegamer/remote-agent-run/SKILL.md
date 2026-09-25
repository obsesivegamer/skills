---
name: remote-agent-run
description: >-
  Offload a whole implementation to another tailnet machine (a Mac, or Windows
  running the job in WSL): verify the repo is cloned there, required env vars
  exist, Claude Code runs the requested model inside a tmux session the user can
  watch from cmux, and computer use happens only on the target. Use whenever the user asks to "kick off an agent run
  on <machine>", "move this workload to <machine>", run Claude or Opus "on my
  other computer", "over tailscale", or wants a long agent job to stop taking
  over the Mac they are using — even if they don't say "remote".
---

# Remote agent run

The user wants a long agent job to run on a different machine (the **target**) while they keep using this one (the **controller**). Three things matter to them, in order:

1. The run actually works on the target: repo, secrets, model, subagents, computer use.
2. They can watch the thread in cmux, the way they watch local runs.
3. This Mac stays theirs. No computer-use clicks, browser control, or focus stealing here.

This session is the controller. Its job is setup, launch, and light monitoring. It does not do the implementation itself, and it never uses computer-use or browser tools locally for this task, because every one of those calls interrupts the person sitting at this Mac. Talk to the target through `ssh` and to cmux through its CLI with `--no-focus`.

When anything behaves differently from what this skill expects, stop and ask. A wrong guess here either fails silently on a machine nobody is watching or grabs the user's screen. Questions are cheap by comparison.

## 1. Resolve the target

- Find the host in `tailscale status` (on this Mac the CLI may be `TAILSCALE_BE_CLI=1 /Applications/Tailscale.app/Contents/MacOS/Tailscale`) and in `~/.ssh/config`.
- The first row of `tailscale status` is this machine. **If the requested target is this machine, stop and ask** which machine they meant. The user's hostnames overlap, so this happens.
- Users often have nicknames for machines ("the server", "the old laptop"). If the request uses a name that is not a tailnet hostname or ssh alias, or uses two names for one target, confirm the mapping once and save it to memory.
- If the user names no machine, check memory for their usual offload target and confirm it in one line.
- Supported targets: a **Mac**, or **Windows running the job inside WSL**. Preflight detects which. For Windows, read [windows-wsl.md](references/windows-wsl.md) now: its commands replace the Mac ones in steps 4 and 5.

## 2. Preflight (read-only)

Run the bundled script. It only reads state and never prints secret values:

```bash
scripts/preflight.sh <ssh-host> <repo-path-on-target> <model-id> [ENV_NAME ...]
```

Resolve `scripts/` relative to this SKILL.md. Get the env var names first (see [preflight.md](references/preflight.md#finding-required-env-var-names)). The script reports: self-target guard (runs before SSH), SSH reachability, platform (Mac or Windows+WSL), desktop session, `claude` / `tmux` / `git` / `gh` presence, repo state, each env var as `set` or `MISSING`, and a one-shot model call that proves auth and model access together.

Fix each failing line using [preflight.md](references/preflight.md). Things only the user can do — enabling Remote Login, granting macOS privacy permissions, `claude /login` or `claude setup-token`, unlocking the keychain, supplying secret values — go to the user as a short numbered list. Do not attempt them. Rerun preflight until it is clean, then show the user the final checklist.

Secrets: never print, echo, or paste values. Moving a secret between machines needs the user's yes for that specific transfer.

## 3. Agree the run settings

Ask only what the conversation has not already settled, in one message:

- **Goal and acceptance criteria** for the implementation.
- **Branch**: default a new branch off the target's up-to-date default branch.
- **Permission mode** on the target. A one-pass unattended run stalls on permission prompts nobody answers. Offer the user's normal mode or auto mode; use `--dangerously-skip-permissions` only if they ask for it by name.
- **Git actions** allowed (commit/push/PR), per the user's CLAUDE.md.

## 4. Launch

1. Write the brief from [kickoff-brief.md](references/kickoff-brief.md) to `<repo>/.agent-run/<run-id>/BRIEF.md` on the target (`ssh host 'cat > …'` with a heredoc). Keep `.agent-run/` out of git by adding it to the target clone's `.git/info/exclude`, which doesn't touch tracked files.
2. Write `start.sh` next to the brief. `caffeinate` keeps the target awake for exactly as long as Claude runs:
   ```bash
   cd <repo>
   exec caffeinate -dimsu claude --model <model-id> <permission-flags> "$(cat .agent-run/<run-id>/BRIEF.md)"
   ```
3. Start it in a detached tmux session, through a login shell so Homebrew and `~/.local/bin` are on PATH:
   ```bash
   ssh <host> 'zsh -lc "tmux new-session -d -s <session> zsh -l <repo>/.agent-run/<run-id>/start.sh"'
   ```
4. Open a cmux view on the controller without stealing focus:
   ```bash
   cmux ssh <host> --name "<repo> @ <host>" --no-focus --command "tmux attach -t <session>"
   ```
   If the user has the "Remote tmux" beta enabled, `cmux ssh-tmux <host> --no-focus` mirrors the sessions natively instead. Load the `cmux` skill for any other cmux command.
5. Tell the user the cmux workspace title, the tmux session name, and how to attach by hand: `ssh -t <host> 'zsh -lc "tmux attach -t <session>"'`.

## 5. Prove it before walking away

Read the pane (`ssh <host> 'zsh -lc "tmux capture-pane -p -t <session>"' | tail -40`) and confirm:

- The header shows the requested model. If it shows another one, stop and report.
- Claude has started reading the brief, not sitting on a login, trust-folder, or permission prompt.
- The brief's first step succeeded: a computer-use screenshot on a Mac, or a browser check inside WSL on Windows. If macOS blocked it, the error names the process that needs Screen Recording / Accessibility. Tell the user exactly which process on which Mac, and wait. Granting those is theirs to do. If the session has no computer-use tool at all, ask the user how they enable it on that machine rather than guessing.

Only then report "running".

## 6. Monitor lightly

The target's run log (`.agent-run/<run-id>/LOG.md`) and the tmux pane are the source of truth. Check on request, or at long intervals if the user asked you to watch. Each check gets one line: what the agent is doing and whether it is on track. Do not type into the remote session unless the user asks; it is their thread now.

## Anti-patterns

- Using computer-use, Chrome, or the browser pane on this Mac for any part of the run.
- Launching Claude in a plain `ssh` session without tmux, so the run dies when the connection drops.
- On Windows, reporting "running" before checking that tmux survived the SSH disconnect. See [windows-wsl.md](references/windows-wsl.md#keeping-the-run-alive).
- Treating "Not logged in" over SSH as a missing account. It is usually the macOS keychain being unavailable to SSH sessions. See [preflight.md](references/preflight.md#claude-auth-over-ssh).
- Copying a whole `.env` across machines without asking.
- Declaring success from a launched process instead of a model header and a working first step.
