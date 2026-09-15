#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
BOOTSTRAP = REPO / "scripts" / "bootstrap"
DOCTOR = REPO / "scripts" / "doctor"
IMPORTER = REPO / "scripts" / "import-tokentracker"


class ToolingTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.home = Path(self.tempdir.name)
        self.test_repo = self.home / "workflow-repo"
        self.skills = self.test_repo / ".agents" / "skills"
        self.skills.mkdir(parents=True, exist_ok=True)
        fixture = self.test_repo / "library" / "owned" / "fixture-skill"
        fixture.mkdir(parents=True, exist_ok=True)
        (fixture / "SKILL.md").write_text(
            "---\nname: fixture-skill\ndescription: Test fixture.\n---\n",
            encoding="utf-8",
        )
        link = self.skills / "fixture-skill"
        if not link.exists() and not link.is_symlink():
            link.symlink_to(Path("../../library/owned/fixture-skill"))
        manifest_dir = self.test_repo / "manifests"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        (manifest_dir / "skills.lock.json").write_text(json.dumps({
            "schema_version": 1,
            "skills": [{
                "name": "fixture-skill",
                "ownership": "owned",
                "provider": "local",
                "path": "library/owned/fixture-skill",
            }],
        }), encoding="utf-8")

    def tearDown(self):
        self.tempdir.cleanup()

    def run_tool(self, tool, *args):
        env = os.environ.copy()
        env["AI_WORKFLOW_HOME"] = str(self.home)
        env["AI_WORKFLOW_REPO"] = str(self.test_repo)
        return subprocess.run(
            [str(tool), *args],
            cwd=REPO,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_dry_run_does_not_create_links(self):
        result = self.run_tool(BOOTSTRAP)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY-RUN", result.stdout)
        self.assertFalse((self.home / ".agents" / "skills").exists())

    def test_apply_creates_global_and_claude_links(self):
        result = self.run_tool(BOOTSTRAP, "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".agents" / "skills" / "fixture-skill").is_symlink())
        self.assertTrue((self.home / ".claude" / "skills" / "fixture-skill").is_symlink())

    def test_apply_refuses_to_replace_real_directory(self):
        conflict = self.home / ".agents" / "skills" / "fixture-skill"
        conflict.mkdir(parents=True)
        result = self.run_tool(BOOTSTRAP, "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CONFLICT", result.stdout + result.stderr)
        self.assertTrue(conflict.is_dir())
        self.assertFalse(conflict.is_symlink())

    def test_adopt_replaces_only_an_existing_symlink(self):
        existing = self.home / ".agents" / "skills" / "fixture-skill"
        existing.parent.mkdir(parents=True)
        existing.symlink_to(self.home / "old-source")
        result = self.run_tool(BOOTSTRAP, "--adopt-existing-symlinks", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = self.test_repo / "library" / "owned" / "fixture-skill"
        self.assertEqual(existing.resolve(), expected.resolve())

    def test_doctor_reports_drifted_link(self):
        target = self.home / ".agents" / "skills"
        target.mkdir(parents=True)
        (target / "fixture-skill").symlink_to(self.home / "wrong-skill")
        result = self.run_tool(DOCTOR)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DRIFT", result.stdout)

    def test_manifest_entries_resolve_to_skill_directories(self):
        manifest = json.loads((REPO / "manifests" / "skills.lock.json").read_text())
        for skill in manifest["skills"]:
            skill_path = REPO / skill["path"]
            self.assertTrue((skill_path / "SKILL.md").is_file(), skill["name"])
            self.assertIn(skill["ownership"], {"owned", "vendored", "external", "vendored-pending-review"})

    def test_importer_groups_skill_and_writes_lockfile(self):
        source = self.home / "managed"
        skill = source / "sample-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: sample-skill\ndescription: Sample.\n---\n",
            encoding="utf-8",
        )
        cache = self.home / "cache.json"
        cache.write_text(json.dumps({"skills": [{
            "name": "sample-skill",
            "repoOwner": "example",
            "repoName": "skills",
            "repoBranch": "main",
            "readmeUrl": "https://github.com/example/skills/blob/main/sample-skill/SKILL.md",
        }]}), encoding="utf-8")
        destination = self.home / "repo"

        dry_run = subprocess.run(
            [str(IMPORTER), "--source", str(source), "--cache", str(cache), "--repo", str(destination)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
        self.assertIn("DRY-RUN", dry_run.stdout)
        self.assertFalse(destination.exists())

        applied = subprocess.run(
            [str(IMPORTER), "--source", str(source), "--cache", str(cache), "--repo", str(destination), "--apply"],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(applied.returncode, 0, applied.stderr)
        imported = destination / "library" / "example" / "sample-skill"
        self.assertTrue((imported / "SKILL.md").is_file())
        self.assertEqual((destination / ".agents" / "skills" / "sample-skill").resolve(), imported.resolve())
        manifest = json.loads((destination / "manifests" / "skills.lock.json").read_text())
        self.assertEqual(manifest["skills"][0]["ownership"], "vendored-pending-review")
        self.assertEqual(manifest["skills"][0]["provider"], "example")


if __name__ == "__main__":
    unittest.main()
