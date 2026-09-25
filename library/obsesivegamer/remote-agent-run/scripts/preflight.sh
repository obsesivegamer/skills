#!/usr/bin/env bash
# Read-only preflight for a remote agent run. Never prints secret values.
# Usage: preflight.sh <ssh-host> <repo-path-on-target> <model-id> [ENV_NAME ...]
set -uo pipefail

if [ $# -lt 3 ]; then
  echo "usage: $0 <ssh-host> <repo-path-on-target> <model-id> [ENV_NAME ...]" >&2
  exit 2
fi

host=$1; shift

platform_uuid() {
  ioreg -rd1 -c IOPlatformExpertDevice 2>/dev/null | awk -F'"' '/IOPlatformUUID/{print $4}'
}

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
  echo "FAIL target: $host is THIS machine (the controller). Ask the user which Mac they meant."
  exit 1
fi

if ! err=$(ssh -o BatchMode=yes -o ConnectTimeout=8 "$host" true 2>&1 </dev/null); then
  echo "FAIL ssh: $(printf '%s' "$err" | tail -1)"
  exit 1
fi
echo "ok   ssh: reachable"

remote_os=$(ssh -o BatchMode=yes "$host" </dev/null uname -s)
if [ "$remote_os" != Darwin ]; then
  echo "FAIL target: $host runs $remote_os, not macOS. This workflow needs a Mac for computer use; ask the user."
  exit 1
fi

local_uuid=$(platform_uuid)
remote_uuid=$(ssh -o BatchMode=yes "$host" </dev/null "ioreg -rd1 -c IOPlatformExpertDevice | awk -F'\"' '/IOPlatformUUID/{print \$4}'")
if [ -n "$local_uuid" ] && [ "$local_uuid" = "$remote_uuid" ]; then
  echo "FAIL target: SAME MACHINE as this controller. Ask the user which Mac they meant."
  exit 1
fi
echo "ok   target: different machine from controller"

quoted=$(printf '%q ' "$@")
ssh -o BatchMode=yes "$host" "zsh -lc 'bash -s -- $quoted'" <<'REMOTE'
repo=$1; model=$2; shift 2
ok()   { echo "ok   $*"; }
fail() { echo "FAIL $*"; }

echo "info host: $(scutil --get ComputerName 2>/dev/null || hostname), macOS $(sw_vers -productVersion 2>/dev/null)"

console=$(stat -f %Su /dev/console 2>/dev/null)
if [ -n "$console" ] && [ "$console" != root ]; then ok "gui user: $console"; else fail "gui user: nobody logged in to the desktop"; fi

for tool in claude tmux git gh; do
  if path=$(command -v "$tool"); then
    ver=$("$tool" --version 2>/dev/null | head -1)
    ok "$tool: $path ${ver}"
  else
    fail "$tool: not found on login-shell PATH"
  fi
done

if command -v gh >/dev/null; then
  if gh auth status >/dev/null 2>&1; then ok "gh auth: logged in"; else fail "gh auth: not logged in"; fi
fi

if [ -d "$repo/.git" ]; then
  cd "$repo" || exit 1
  git fetch --quiet </dev/null 2>/dev/null || echo "warn git fetch failed"
  branch=$(git rev-parse --abbrev-ref HEAD)
  dirty=$(git status --porcelain | wc -l | tr -d ' ')
  ab=$(git rev-list --left-right --count '@{upstream}...HEAD' 2>/dev/null | awk '{print "behind "$1", ahead "$2}')
  ok "repo: $repo on $branch (${ab:-no upstream}), $dirty dirty files, origin $(git remote get-url origin 2>/dev/null)"
  if git check-ignore -q .agent-run/x 2>/dev/null; then ok "repo: .agent-run/ is git-ignored"; else echo "warn repo: .agent-run/ is not git-ignored (add it to .git/info/exclude)"; fi
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
  out=$(cd "${repo:-$HOME}" 2>/dev/null; perl -e 'alarm shift; exec @ARGV' 120 \
        claude -p "Reply with exactly: preflight-ok" --model "$model" </dev/null 2>&1 | tail -3)
  if printf '%s' "$out" | grep -q preflight-ok; then
    ok "claude: auth + model $model answered"
  else
    fail "claude: model $model smoke test failed: $(printf '%s' "$out" | tr '\n' ' ' | cut -c1-200)"
  fi
fi
REMOTE
