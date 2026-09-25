#!/usr/bin/env bash
# Read-only preflight for a remote agent run. Never prints secret values.
# Targets: a Mac (zsh) or a Windows machine running the job inside WSL.
# Usage: preflight.sh <ssh-host> <repo-path-on-target> <model-id> [ENV_NAME ...]
set -uo pipefail

if [ $# -lt 3 ]; then
  echo "usage: $0 <ssh-host> <repo-path-on-target> <model-id> [ENV_NAME ...]" >&2
  exit 2
fi

host=$1; shift

tailscale_cli() {
  if command -v tailscale >/dev/null; then tailscale "$@"
  else TAILSCALE_BE_CLI=1 /Applications/Tailscale.app/Contents/MacOS/Tailscale "$@"
  fi
}

target_name=$(ssh -G "$host" 2>/dev/null | awk '/^hostname /{print tolower($2)}')
self_names=$(
  { hostname -s; scutil --get LocalHostName 2>/dev/null
    tailscale_cli status --json 2>/dev/null | python3 -c '
import json, sys
s = json.load(sys.stdin)["Self"]
print(s["DNSName"].split(".")[0]); print(s["DNSName"].rstrip("."))
print("\n".join(s.get("TailscaleIPs", [])))' 2>/dev/null
  } | tr '[:upper:]' '[:lower:]'
)
if [ -n "$target_name" ] && printf '%s\n' "$self_names" | grep -qxF "$target_name"; then
  echo "FAIL target: $host is THIS machine (the controller). Ask the user which machine they meant."
  exit 1
fi

sshq() { ssh -o BatchMode=yes -o ConnectTimeout=8 "$host" "$@" </dev/null; }

if ! err=$(sshq exit 0 2>&1); then
  echo "FAIL ssh: $(printf '%s' "$err" | tail -1)"
  exit 1
fi
echo "ok   ssh: reachable"

if [ "$(sshq uname -s 2>/dev/null)" = Darwin ]; then
  platform=mac
  runner='zsh -lc "bash -s"'
  remote_uuid=$(sshq "ioreg -rd1 -c IOPlatformExpertDevice | awk -F'\"' '/IOPlatformUUID/{print \$4}'")
  local_uuid=$(ioreg -rd1 -c IOPlatformExpertDevice 2>/dev/null | awk -F'"' '/IOPlatformUUID/{print $4}')
  if [ -n "$local_uuid" ] && [ "$local_uuid" = "$remote_uuid" ]; then
    echo "FAIL target: SAME MACHINE as this controller. Ask the user which machine they meant."
    exit 1
  fi
elif [ "$(sshq wsl -e uname -s 2>/dev/null | tr -d '\r')" = Linux ]; then
  platform=wsl
  runner='wsl -e bash -lc "bash -s"'
else
  echo "FAIL target: $host is neither a Mac nor Windows with WSL. Ask the user."
  exit 1
fi
echo "ok   target: $platform, different machine from controller"

# Arguments travel on stdin so they survive Windows cmd quoting.
{
  printf 'set --'; printf ' %q' "$@"; printf '\n'
  cat <<'REMOTE'
repo=$1; model=$2; shift 2
ok()   { echo "ok   $*"; }
warn() { echo "warn $*"; }
fail() { echo "FAIL $*"; }

if command -v sw_vers >/dev/null; then
  echo "info host: $(scutil --get ComputerName 2>/dev/null || hostname), macOS $(sw_vers -productVersion)"
  console=$(stat -f %Su /dev/console 2>/dev/null)
  if [ -n "$console" ] && [ "$console" != root ]; then ok "gui user: $console"; else fail "gui user: nobody logged in to the desktop"; fi
else
  . /etc/os-release 2>/dev/null
  echo "info host: $(hostname), WSL ${PRETTY_NAME:-Linux}, kernel $(uname -r)"
  query=$(command -v query.exe || echo /mnt/c/Windows/System32/query.exe)
  if "$query" user 2>/dev/null | tr -d '\r' | grep -q Active; then ok "windows desktop: a user session is active"
  else warn "windows desktop: could not confirm an active desktop session"; fi
  case "$repo" in /mnt/*) warn "repo: $repo is on the Windows filesystem; git and builds are much slower there than under ~/";; esac
fi

for tool in claude tmux git gh; do
  if path=$(command -v "$tool"); then
    if [ "$tool" = tmux ]; then ver=$(tmux -V); else ver=$("$tool" --version 2>/dev/null | head -1); fi
    ok "$tool: $path $ver"
  else
    fail "$tool: not found on login-shell PATH"
  fi
done

if command -v gh >/dev/null; then
  if gh auth status >/dev/null 2>&1; then ok "gh auth: logged in"; else fail "gh auth: not logged in"; fi
fi

if [ -d "$repo/.git" ]; then
  cd "$repo" || exit 1
  git fetch --quiet </dev/null 2>/dev/null || warn "git fetch failed"
  branch=$(git rev-parse --abbrev-ref HEAD)
  dirty=$(git status --porcelain | wc -l | tr -d ' ')
  ab=$(git rev-list --left-right --count '@{upstream}...HEAD' 2>/dev/null | awk '{print "behind "$1", ahead "$2}')
  ok "repo: $repo on $branch (${ab:-no upstream}), $dirty dirty files, origin $(git remote get-url origin 2>/dev/null)"
  if git check-ignore -q .agent-run/x 2>/dev/null; then ok "repo: .agent-run/ is git-ignored"
  else warn "repo: .agent-run/ is not git-ignored (add it to .git/info/exclude)"; fi
else
  fail "repo: $repo is not a git clone"
fi

for name in "$@"; do
  where=""
  for f in "$repo/.env" "$repo/.env.local"; do
    [ -f "$f" ] && grep -Eq "^(export[[:space:]]+)?${name}=.+" "$f" && where="${where} ${f##*/}"
  done
  [ -n "${!name-}" ] && where="${where} shell"
  if [ -n "$where" ]; then ok "env $name: set (${where# })"; else fail "env $name: MISSING"; fi
done

if command -v claude >/dev/null; then
  if command -v timeout >/dev/null; then limit="timeout 120"; else limit="perl -e alarm(shift);exec(@ARGV) 120"; fi
  out=$(cd "$repo" 2>/dev/null; $limit claude -p "Reply with exactly: preflight-ok" --model "$model" </dev/null 2>&1 | tail -3)
  if printf '%s' "$out" | grep -q preflight-ok; then
    ok "claude: auth + model $model answered"
  else
    fail "claude: model $model smoke test failed: $(printf '%s' "$out" | tr '\n' ' ' | cut -c1-200)"
  fi
fi
REMOTE
} | ssh -o BatchMode=yes "$host" "$runner"
