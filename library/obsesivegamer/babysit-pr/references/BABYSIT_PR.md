# Babysit PR

**Source of truth (do not invent from videos):**

`~/Documents/GitHub/skills/library/unconfirmed/poteto-mode/playbooks/babysit.md`

That is the real poteto **Babysit** playbook (modes: `drive` / `background` / `threads-only` / `check`, merge frontier, `watch-pr`, bugbot triage, no merge without explicit ship request → `playbooks/shipping.md`).

## How to use from this swarm pack

1. Open that file (or `@` poteto babysit) in the Codex / agent tab.
2. Prefer poteto babysit over any screenshot- or video-derived “Babysit PR” outline.
3. This folder’s earlier draft was a **video paraphrase** of Ben Davis’s Astra demo — **not** GitHub. Discarded in favor of the playbook above.

## Thin reminder (full rules live in babysit.md)

- Declare mode before polling.
- One babysitter; work the merge frontier only.
- Never merge from babysit — landing is Shipping.
- Order: conflicts → review threads → CI; classify flake before retrigger.
