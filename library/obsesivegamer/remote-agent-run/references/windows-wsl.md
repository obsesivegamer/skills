# Windows target (WSL + tmux)

The job runs inside WSL on the Windows machine, in tmux, so the user can watch the live thread from cmux the same way as on a Mac. SSH lands in Windows (cmd or PowerShell). Wrap every command in `wsl -e bash -lc "…"`, using double quotes because cmd does not treat single quotes as quoting.

Trade-off the user accepted: computer use does not reach the Windows desktop from WSL. UI checks happen in a browser inside WSL (headless Playwright, or a WSLg window on the target's desktop).

## One-time setup (the user does the Windows-admin parts)

1. **OpenSSH Server** (user, admin PowerShell on the target):
   ```powershell
   Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
   Start-Service sshd; Set-Service sshd -StartupType Automatic
   New-NetFirewallRule -Name sshd-tailnet -DisplayName "OpenSSH (Tailscale)" -Protocol TCP -LocalPort 22 -RemoteAddress 100.64.0.0/10 -Action Allow
   ```
   Tailscale on Windows cannot serve Tailscale SSH, so this is required.
2. **Key login.** An administrator account on Windows reads keys from `C:\ProgramData\ssh\administrators_authorized_keys`, not `~/.ssh/authorized_keys`. Ask before copying a public key. Never copy a private key.
3. **WSL** (user): `wsl --install -d Ubuntu`, then reboot and create the Linux user. Check with `ssh <host> wsl -l -v`: the distro should be the default and on version 2.
4. **Tools inside WSL** (confirm before installing): `sudo apt install -y tmux git gh`, then `curl -fsSL https://claude.ai/install.sh | bash`.
5. **Claude login inside WSL** (user): run `claude` once in `ssh -t <host> wsl` and finish login (it prints a URL to open on any device), or `claude setup-token` and put `CLAUDE_CODE_OAUTH_TOKEN` in `~/.profile`. The macOS keychain problem doesn't exist here.
6. **Repo location:** clone under the WSL home (`~/src/<repo>`), not `/mnt/c/...`. The Windows filesystem is many times slower for git and builds.

## Keeping the run alive

WSL can shut a distro down after the last `wsl.exe` client disconnects, which would kill tmux and the agent. After launching, disconnect, wait 90 seconds, and check `ssh <host> wsl -e tmux has-session -t <session>`.

If the session died:
- Ask the user before changing config. The usual fix is `%UserProfile%\.wslconfig` on the target:
  ```ini
  [wsl2]
  vmIdleTimeout=-1
  ```
  then `wsl --shutdown` and relaunch.
- If that isn't enough, a Windows scheduled task that runs `wsl -e sleep infinity` at logon keeps a client attached. The user creates it or approves it.

`caffeinate` is macOS-only. On an always-on server, check the power plan never sleeps (`powercfg /q` via SSH, read-only) and report if it does.

## Launch commands

```bash
ssh <host> "wsl -e bash -lc \"tmux new-session -d -s <session> bash -l <repo>/.agent-run/<run-id>/start.sh\""
```

`start.sh` is the same as on a Mac minus `caffeinate`:
```bash
cd <repo>
exec claude --model <model-id> <permission-flags> "$(cat .agent-run/<run-id>/BRIEF.md)"
```

Write files into WSL by piping through SSH: `ssh <host> "wsl -e bash -c \"cat > <path>\"" < localfile`.

cmux view: `cmux ssh` installs a small remote helper that has no Windows build, so open a plain workspace instead:
```bash
cmux new-workspace --name "<repo> @ <host>" --focus false --command "ssh -t <host> wsl -e tmux attach -t <session>"
```

Reading the pane: `ssh <host> wsl -e tmux capture-pane -p -t <session> | tail -40`.
