---
name: babysit-pr
description: Drive a pull request or stack of PRs to merge-ready (conflicts, review threads, and CI). Owns the merge frontier without merging. Use for "babysit", "babysit pr", "get it green", "address bugbot comments", "check on PR", or "merge-ready".
---

# Babysit PR

Drive a pull request or stack of PRs to merge-ready. You own the **merge frontier** (the lowest unmerged PR in a stack). Clear one PR at a time, and stop where the human's call begins.

> [!IMPORTANT]
> **Never merge from babysit.** Babysitting ends at merge-ready. Landing or merging a PR/stack belongs to [Shipping](references/shipping.md). Do not run merge commands (`gh pr merge`, `origin pr merge`) unless the user explicitly commands you to merge, land, or ship.

---

## Core Non-Negotiables

1. **One babysitter per stack.** Check that no other process or agent is actively working the stack.
2. **Work the merge frontier only.** The lowest unmerged PR is the only PR that matters until it merges. Upstack review threads may be read and batched, but never fixed at the cost of restarting frontier checks. If you find yourself working upstack while the frontier is red or pending, stop and return to the frontier.
3. **Never mutate stack topology.** Do not perform base retargets, rebases, stack-wide submits, or force-pushes from inside babysit. Fix on the owning branch. If a rebase is required due to upstream drift or conflicts, report it to the user and halt. The only sanctioned branch creation: if a fix's owning PR has already merged, create a new PR on top of the remaining stack rather than rewriting merged history.
4. **Order of operations:**
   1. **Conflicts** (report and stop immediately; do not run CI to look busy).
   2. **Review threads** (batch with code fixes).
   3. **CI** (classify before retriggering).
   Batch every known fix into a single push wave.
5. **Declare mode before polling.** Always establish and state your execution mode before querying forge status.

---

## Modes

- **`drive`** (default): Runs the active loop until the frontier is merge-ready. Use for "babysit this", "get it green", "bring to merge-ready".
- **`background`**: Triages and reports without blocking; appropriate when another implementation plan is actively executing.
- **`threads-only`**: Addresses review comments and touches nothing else. Use for "address the bugbot comments", "fix PR feedback".
- **`check`**: Performs a single status pass and reports findings. Use for "check on PR #X", "is it green?". Default for small or docs-only PRs.

---

## Forge Resolution

1. **Default forge:** GitHub CLI (`gh`).
2. **Alternative forge:** If `command -v origin` succeeds and Origin resolves the repository, use `origin pr ...` commands.
3. **Never require Graphite (`gt`).**

---

## Workflow & Commands

### 1. Resolve PR & Current State

```bash
# GitHub CLI
gh pr view <pr> --json number,title,url,headRefName,baseRefName,mergeable,reviewDecision,statusCheckRollup

# Origin CLI (if active)
origin pr view <pr> --checks --comments
origin pr thread list <pr>
```

### 2. Check for Conflicts

If the PR has merge conflicts:
- Identify the conflicting branch.
- Identify potential upstream callers/callees affected by the drift.
- Report the required rebase to the human operator and **stop**. Do not proceed to CI fixes.

### 3. Review Threads & Bugbot Triage

Treat review comments and automated review bot (Bugbot) comments skeptically per [Bugbot Triage](references/bugbot-triage.md). Do not churn code simply to quiet a bot.

- **`fix`**: Comment identifies real correctness, security, data loss, auth, migration, or concurrency bug. Implement the fix with a red-first test on the lowest owning PR.
- **`dismiss`**: Comment matches a documented noisy pattern (e.g., intentional UI redesign, false-positive rule, local duplication during refactor). Reply on the thread with concrete disproof and resolve.
- **`ask`**: Novel, high-severity, data/security-related, or ambiguous. Ask the human.

#### Thread Reply Commands

```bash
# GitHub review comment reply
gh api --method POST "repos/<owner>/<repo>/pulls/<pr>/comments/<comment-id>/replies" \
  --raw-field body="<reply-text>"

# Origin thread reply
origin pr thread reply <thread-id> <pr> --body-file <reply-file>
```

### 4. CI Classification & Retriggering

Never retrigger failed CI jobs blindly.

1. **Classify first:**
   - **Infrastructure / Flake:** Transient network timeout or runner drop. Eligible for **at most one** fresh workflow re-run (not repeated job retries). If it fails a second time with the same error, it is not flake.
   - **Stale base:** Check if failure occurs in code untouched by this PR:
     ```bash
     git merge-base --is-ancestor <base-branch> HEAD
     ```
     If base is stale, report the rebase requirement.
   - **PR defect:** Inspect failure logs directly:
     ```bash
     gh run view <run-id> --log-failed
     ```
     Fix the underlying defect in the owning PR.

2. **Watch status:**
   ```bash
   gh pr checks <pr> --watch --fail-fast
   # Or using poteto watch-pr script when available:
   # scripts/watch-pr/watch-pr
   ```

---

## Subagents & Antigravity Policy

When running under Antigravity:
- **Never use Cursor tools or the Cursor CLI.**
- Spawn worker subagents using `invoke_subagent`.
- **Model routing:**
  - Judgment, subtle design, and complex bugbot triage: `Claude Opus 4.6 (Thinking)` (`claude-4.6-opus-max-thinking` or `pro`).
  - Code generation, mechanical bug fixes, test runs, and CLI checks: `Gemini 3.8 Flash High` (`flash`).
- Maintain oversight of all subagent diffs; review every patch before pushing.

---

## Stop Conditions

Stop `drive` mode when:
1. **GitHub:** Frontier PR status reaches `READY` (single/stack mode) or `WAITING` with reason `merge-queue` (queued mode).
2. **Origin:** Frontier reports mergeable with green checks and zero unresolved blocker threads.
3. **Human Line:** Reached an owner approval requirement, conflict requiring manual rebase, or merge authorization boundary.

---

## Output / Response Format

Always structure your report with:
1. **Mode:** Declared mode (`drive`, `background`, `threads-only`, `check`).
2. **Frontier:** PR number, branch, and active forge status.
3. **Checks & Watcher Table:** Status of all required checks (Pass / Pending / Fail).
4. **Triage Summary:** What was fixed vs. dismissed with concrete justifications.
5. **Next Actions:** Pending runs or specific decisions requiring human input.
