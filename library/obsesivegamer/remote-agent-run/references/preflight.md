# Preflight fixes

One section per preflight line. Anything marked **user** is theirs to do; give them the exact step and wait.

For a Windows target, the SSH, tools, login, and computer-use fixes are in [windows-wsl.md](windows-wsl.md) instead. The repo and env var sections below apply to both.

## Self-target guard

`SAME MACHINE`: the ssh host resolves to this Mac. Stop and ask which machine they meant. Do not "fix" it by picking another host yourself.

## SSH reachability

- `Permission denied` / timeout: **user** enables System Settings → General → Sharing → Remote Login on the target. The Mac App Store / standalone Tailscale app cannot act as a Tailscale SSH server, so plain SSH over the tailnet IP or MagicDNS name is the normal route.
- Host key prompt: run `ssh <host> true` once interactively in a terminal the user can see, or ask them to.
- Key not accepted: check `ssh -G <host>` for the identity in use; ask before copying any key.

## GUI user

`console user: root` or `loginwindow` means nobody is logged in to the desktop. Computer use needs a logged-in GUI session. **User** logs in on the target (Screen Sharing over the tailnet works).

## Tools

- `claude` missing or old: install/update on the target with the official installer (`curl -fsSL https://claude.ai/install.sh | bash`) or `claude update`. Confirm before installing anything.
- `tmux` missing: `brew install tmux` (confirm first).
- `gh` not authenticated: **user** runs `gh auth login` on the target, or you use HTTPS with their existing credential helper. Do not forward tokens from this Mac.

## Repo

- Missing: clone on the target with its own credentials, e.g. `ssh <host> 'zsh -lc "gh repo clone <owner/repo> <path>"'`.
- Present: `git fetch`, then report branch, ahead/behind, and dirty files. **Never reset, stash, or overwrite** uncommitted work on the target; ask.
- Also check the user's skills repo on the target if their workflow depends on it (`./scripts/doctor` in its clone), so the remote agent has the same skills and CLAUDE.md.

## Finding required env var names

Collect names only, from whichever of these the repo has:

- `.env.example`, `.env.sample`, `.env.template`
- `docker-compose*.yml` `environment:` / `${VAR}` entries
- CI workflows (`${{ secrets.X }}`, `env:` blocks)
- Code references: `process.env.X`, `os.environ["X"]`, `os.getenv("X")`, `ENV["X"]`
- README setup sections

Drop names that are obviously CI-only or have defaults in code. Show the user the final list if it's not obvious.

## Missing env vars

Offer, per var or per group:

1. **User** sets it on the target (shell profile or the repo's `.env`).
2. Copy from this Mac's `.env` over the tailnet, with a yes for that transfer: extract only the needed keys into a temp file in the scratchpad, `scp` it, `chmod 600` on the target, delete the local temp file. Never print the values.

Also check the variables Claude Code itself needs. With a subscription login, none. With API billing, `ANTHROPIC_API_KEY` on the target.

## Claude auth over SSH

`Not logged in` / `Invalid API key` from the model smoke test, when the user is logged in at the target's desktop, is usually the login keychain being locked for SSH sessions. Options for the **user**:

1. Run `claude setup-token` on the target and put the resulting `CLAUDE_CODE_OAUTH_TOKEN` in the target's shell profile (they type it; you never see it).
2. Run `security unlock-keychain ~/Library/Keychains/login.keychain-db` in the SSH session before launching (they type the password).

## Model smoke test

- `model not found` / `invalid model`: the target's `claude` is older than the model, or the account can't use it. Update `claude`, rerun. If still failing, report; do not substitute a different model silently.
- Timeout: network or first-run prompts. Attach and look (`ssh <host> -t 'zsh -lc claude'`) with the user watching.

## Computer use on the target

Checked after launch, because macOS privacy permissions attach to the process tree that runs Claude. If the brief's first screenshot fails:

1. Read the error for the process name macOS blocked.
2. **User** grants Screen Recording and Accessibility to that app on the target (System Settings → Privacy & Security), then restarts the session.
3. If processes started over SSH can't get the grant, the fallback is that the **user** starts the tmux session once from a terminal on the target's desktop (Screen Sharing is fine). The cmux view on this Mac still attaches to it the same way.

Confirm with the user before switching approaches.
