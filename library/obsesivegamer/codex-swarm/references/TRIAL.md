# First Desktop trial

Select Astra and Medium in the Desktop model controls, then send this in the project you want to use:

```text
Use $codex-swarm in Codex Desktop. Run a short trial with two native
gpt-6-astra subagents at medium reasoning. Keep yourself as coordinator.
Create a unique project-local .swarm run directory with BOARD.md and
separate worker reports. Git actions: none.

Worker 1: inspect the project's existing validation commands and run one
appropriate, non-destructive check. Report the exact command and outcome.
Worker 2: independently inspect one bounded project invariant and report
evidence. After both reports arrive, ask worker 2 to check worker 1's
evidence and record agreement or disagreement.

Check each worker at 5 minutes and interrupt at 10 minutes. Record actual
IDs and absolute deadlines. Do not create sidebar tasks or start cmux.
Keep UI access with the coordinator. Verify Browser and Mac computer-use
access using a harmless read, loading their skills first. Report missing
access without changing system permissions.

Finish with a board linking both reports, independent verification, all
workers accounted for, and PASS / ISSUES / BLOCKED. Do not claim this
short run proves unattended two-hour supervision.
```

For actual work, replace the inspection assignments with your goal and observable acceptance criteria. Start with two workers; use more only when independent work and capacity exist. Low or medium is the routine default; high is useful for difficult synthesis or review. Request xhigh, max, or ultra deliberately when supported.

The skill is available through existing symlinks. If an older task still shows the old description, start a fresh task or explicitly give it the canonical SKILL.md path and ask it to read the updated file. No reinstall is needed when links resolve.
