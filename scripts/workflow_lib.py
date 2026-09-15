#!/usr/bin/env python3
import os
from pathlib import Path


REPO = Path(os.environ.get("AI_WORKFLOW_REPO", Path(__file__).resolve().parents[1])).expanduser()


def workflow_home():
    return Path(os.environ.get("AI_WORKFLOW_HOME", Path.home())).expanduser()


def skill_source():
    return REPO / ".agents" / "skills"


def harness_skill_dirs():
    home = workflow_home()
    return {
        "agents": home / ".agents" / "skills",
        "codex": home / ".codex" / "skills",
        "claude": home / ".claude" / "skills",
        "gemini": home / ".gemini" / "skills",
        "cursor": home / ".cursor" / "skills",
        "opencode": home / ".config" / "opencode" / "skills",
    }


def skills():
    return sorted(
        entry for entry in skill_source().iterdir()
        if entry.name != ".DS_Store" and (entry.is_dir() or entry.is_symlink())
    )


def same_link(link, expected):
    if not link.is_symlink():
        return False
    return link.resolve(strict=False) == expected.resolve(strict=False)
