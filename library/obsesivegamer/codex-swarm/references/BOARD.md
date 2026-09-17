# Swarm Message Board

**Job:** _(one-line goal)_  
**Started:** _(ISO local / ET)_  
**Coordinator tab:** `Codex CLI → swarm-coordinator`  
**Board path:** ``BOARD.md` in the job cwd (or a durable path you agreed)`

---

## Status

| Field | Value |
|-------|--------|
| Phase | kickoff / researching / verifying / consensus / implementing / babysit-pr / done / blocked |
| Overall | green / yellow / red |
| Last board update | _(who + time ET)_ |
| Active workers | _(tab titles)_ |
| Blockers | _(none or list)_ |

---

## Claims / Theories

Append; never silently delete. Mark disposition when verified.

| ID | Author (tab) | Claim / theory | Confidence | Status | Notes |
|----|--------------|----------------|------------|--------|-------|
| T1 | | | low/med/high | open / verifying / supported / rejected | |

---

## Evidence

Link claims to concrete proof (paths, commands, PR URLs, test output snippets).

| ID | Related claim | Evidence | Source (tab / path) | Time ET |
|----|---------------|----------|---------------------|---------|
| E1 | T1 | | | |

---

## Open Questions

| ID | Question | Owner | Needed by | Status |
|----|----------|-------|-----------|--------|
| Q1 | | | | open / answered |

---

## Consensus

What the swarm currently agrees is true / the plan forward. Update only after verification, not vibes.

- **Agreed:**
- **Rejected / parked:**
- **Decision log:** _(timestamp — decision — why)_

---

## Next Actions

| Priority | Action | Owner (tab) | Due / timer | Done? |
|----------|--------|-------------|-------------|-------|
| 1 | | coordinator / worker-N | | |

---

## Doom-loop / Timer Notes

Hard policy (Ben Davis–style):

- **~60m check:** Coordinator must inspect each research/worker thread (cmux capture-pane + BOARD.md). Re-prompt, narrow scope, or reassign if stuck.
- **~120m kill:** If still no useful BOARD.md progress, kill/reassign that worker. No infinite ruts.
- **Anti-doom:** Prefer new angles over repeating the same failing approach. Log kills here.

| Worker tab | Started ET | Last check ET | Check (~60m) | Kill-by (~120m) | Disposition |
|------------|------------|---------------|--------------|-----------------|-------------|
| swarm-worker-1 | | | | | running / checked / killed / done |

**Kill / reassign log:**

- _(timestamp — tab — reason — replacement)_

---

## Worker Scratch (optional short notes)

Workers may paste brief status here; durable claims go in **Claims / Theories** + **Evidence**.
