#!/usr/bin/env python3
"""Basic tests for Skill Pack CLI.

Run:
    python3 -m unittest discover -s tests -p 'test_*.py' -v
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "scripts" / "skillpack.py"


class SkillPackCliTests(unittest.TestCase):
    def run_cli(self, *args: str, env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
        proc_env = os.environ.copy()
        if env:
            proc_env.update(env)
        proc = subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=str(REPO),
            env=proc_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if check and proc.returncode != 0:
            self.fail(
                f"CLI failed: {' '.join(args)}\n"
                f"returncode={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
            )
        return proc

    def test_list_json(self) -> None:
        proc = self.run_cli("list", "--json")
        data = json.loads(proc.stdout)
        self.assertEqual(data["pack"]["name"], "metaportal-skillpack")
        names = {skill["name"] for skill in data["skills"]}
        self.assertIn("skillpack-maintainer", names)
        self.assertIn("example-skill", names)

    def test_validate_passes(self) -> None:
        proc = self.run_cli("validate")
        self.assertIn("Validation passed", proc.stdout)

    def test_personal_install_temp_home(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            proc = self.run_cli("install", "--scope", "personal", "--profile", "all", env={"HOME": str(home)})
            self.assertIn("Install completed", proc.stdout)
            target = home / ".claude" / "skills"
            self.assertTrue((target / "skillpack-maintainer" / "SKILL.md").exists())
            self.assertTrue((target / "example-skill" / "SKILL.md").exists())
            marker = target / "skillpack-maintainer" / ".skillpack-source.json"
            self.assertTrue(marker.exists())
            data = json.loads(marker.read_text())
            self.assertEqual(data["managed_by"], "skillpack")
            lock = home / ".skillpacks" / "installed" / "metaportal-skillpack.lock.json"
            self.assertTrue(lock.exists())

    def test_project_install_temp_project(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            proc = self.run_cli("install", "--scope", "project", "--project-path", str(project), "--profile", "all")
            self.assertIn("Install completed", proc.stdout)
            target = project / ".claude" / "skills"
            self.assertTrue((target / "skillpack-maintainer" / "SKILL.md").exists())
            self.assertTrue((target / "example-skill" / "SKILL.md").exists())
            lock = project / ".claude" / "skillpack.lock.json"
            self.assertTrue(lock.exists())

    def test_preserves_unmanaged_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            unmanaged = home / ".claude" / "skills" / "example-skill"
            unmanaged.mkdir(parents=True)
            (unmanaged / "SKILL.md").write_text("unmanaged local copy\n", encoding="utf-8")
            proc = self.run_cli("install", "--scope", "personal", "--profile", "all", env={"HOME": str(home)})
            self.assertIn("preserved unmanaged", proc.stdout.lower())
            self.assertEqual((unmanaged / "SKILL.md").read_text(encoding="utf-8"), "unmanaged local copy\n")
            self.assertTrue((home / ".claude" / "skills" / "skillpack-maintainer" / "SKILL.md").exists())
            lock = home / ".skillpacks" / "installed" / "metaportal-skillpack.lock.json"
            lock_data = json.loads(lock.read_text())
            self.assertIn("example-skill", lock_data["skipped_conflicts"])

    def test_status_temp_home(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            self.run_cli("install", "--scope", "personal", "--profile", "all", env={"HOME": str(home)})
            proc = self.run_cli("status", "--scope", "personal", env={"HOME": str(home)})
            self.assertIn("Managed skills", proc.stdout)
            self.assertIn("skillpack-maintainer", proc.stdout)
            self.assertIn("example-skill", proc.stdout)

    def test_package_profile(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "skillpack-all.zip"
            proc = self.run_cli("package", "--profile", "all", "--out", str(out))
            self.assertIn("Packaged 2 skill", proc.stdout)
            self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
