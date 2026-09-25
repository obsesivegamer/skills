# Kickoff brief template

Fill every `<…>`. This is the first message the remote Claude session receives, so it has to stand alone: the remote agent has none of this conversation.

```markdown
# Agent run <run-id>

You are running on <target-host>, a Mac dedicated to this job. The user is watching this thread from another machine through cmux and is not at this Mac's keyboard.

## Goal
<one paragraph: what to build or fix, and why>

## Done means
- <acceptance criterion>
- <acceptance criterion>
- The repo's real check passes: <command, e.g. `npm run ci:local`>

## Setup already verified
- Repo: <absolute path>, branch `<branch>` created from `<base>` at <sha>
- Env vars present: <names only>
- Model: <model-id>

## How to work
- Do the whole implementation in this session, in one pass. Use as many subagents as the work benefits from; give parallel workers disjoint files.
- You have full computer use on this Mac. Use it for anything that needs a real UI (running the app, checking it in a browser). Nobody else is using this screen.
- First step: take one computer-use screenshot to confirm access. If it fails, or you have no computer-use tool, write the exact error to LOG.md and stop. Do not work around it.
- Git: <allowed actions, e.g. commit and push to `<branch>`, open a PR, never merge>.
- If something blocks you that needs a human (a login, a permission dialog, a missing secret, an ambiguous requirement), write the question at the top of LOG.md and in this thread, then continue with any work that doesn't depend on it.

## Progress log
Append a timestamped line to `<repo>/.agent-run/<run-id>/LOG.md` at each milestone: started, plan ready, each major piece done, checks green, PR opened, finished or blocked. The controller reads this file.
```
