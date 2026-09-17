# Babysit PR

**Source of truth (do not invent from videos):**

In this repository: `library/unconfirmed/poteto-mode/playbooks/babysit.md`

On a machine with this skills repo linked: resolve via the `poteto-mode` skill / playbooks path, or:

`~/Documents/GitHub/skills/library/unconfirmed/poteto-mode/playbooks/babysit.md`

That is the real poteto **Babysit** playbook (modes: `drive` / `background` / `threads-only` / `check`, merge frontier, `watch-pr`, bugbot triage, no merge without explicit ship request → `playbooks/shipping.md`).

## Thin reminder

- Declare mode before polling.
- One babysitter; work the merge frontier only.
- Never merge from babysit — landing is Shipping.
- Order: conflicts → review threads → CI; classify flake before retrigger.
