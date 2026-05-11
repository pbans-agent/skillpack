#!/usr/bin/env python3
"""Tests for Milestone 3 features.

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
import zipfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "scripts" / "skillpack.py"


class Milestone3Tests(unittest.TestCase):
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

    # -- info command --

    def test_info_human_readable(self) -> None:
        proc = self.run_cli("info", "code-review")
        self.assertIn("Skill: code-review", proc.stdout)
        self.assertIn("Version:", proc.stdout)
        self.assertIn("Description:", proc.stdout)
        self.assertIn("Profiles:", proc.stdout)
        self.assertIn("References:", proc.stdout)
        self.assertIn("Evals:", proc.stdout)

    def test_info_json_output(self) -> None:
        proc = self.run_cli("info", "code-review", "--json")
        data = json.loads(proc.stdout)
        self.assertEqual(data["name"], "code-review")
        self.assertIn("all", data["profiles"])
        self.assertIn("coding", data["profiles"])
        self.assertTrue(data["has_references"])
        self.assertTrue(data["has_evals"])
        self.assertEqual(data["eval_count"], 3)
        self.assertIn("review-sql-injection", data["eval_ids"])

    def test_info_nonexistent_skill(self) -> None:
        proc = self.run_cli("info", "nonexistent-skill", check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("not found", proc.stderr)

    # -- eval command --

    def test_eval_single_skill(self) -> None:
        proc = self.run_cli("eval", "--skill", "code-review")
        self.assertIn("Skills with evals: 1", proc.stdout)
        self.assertIn("Total evals: 3", proc.stdout)

    def test_eval_json_output(self) -> None:
        proc = self.run_cli("eval", "--skill", "code-review", "--json")
        data = json.loads(proc.stdout)
        self.assertEqual(data["total_skills_with_evals"], 1)
        self.assertEqual(data["total_evals"], 3)
        eval_ids = [e["eval_id"] for e in data["evals"]]
        self.assertIn("review-sql-injection", eval_ids)
        # Each eval should have prompt and expected_output.
        for e in data["evals"]:
            self.assertIn("prompt", e)
            self.assertIn("expected_output", e)
            self.assertEqual(e["status"], "pending")

    def test_eval_all_skills(self) -> None:
        proc = self.run_cli("eval", "--quiet")
        self.assertIn("Eval Summary", proc.stdout)
        # Should find evals across multiple skills.
        self.assertIn("Total evals:", proc.stdout)

    def test_eval_nonexistent_skill(self) -> None:
        proc = self.run_cli("eval", "--skill", "nonexistent-skill", check=False)
        self.assertNotEqual(proc.returncode, 0)

    # -- per-skill packaging --

    def test_per_skill_package(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "skills"
            proc = self.run_cli("package", "--per-skill", "--out", str(out_dir))
            self.assertIn("Packaged", proc.stdout)
            # Should have individual zip files.
            self.assertTrue((out_dir / "code-review.zip").exists())
            self.assertTrue((out_dir / "git-workflow.zip").exists())
            self.assertTrue((out_dir / "skillpack-maintainer.zip").exists())
            # Verify zip contents are structured correctly.
            with zipfile.ZipFile(out_dir / "code-review.zip") as zf:
                names = zf.namelist()
                self.assertTrue(any("SKILL.md" in n for n in names))
                # Should have skill name as top-level directory.
                self.assertTrue(any(n.startswith("code-review/") for n in names))

    def test_single_skill_package(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "review.zip"
            proc = self.run_cli("package", "--skill", "code-review", "--out", str(out))
            self.assertIn("Packaged 1 skill", proc.stdout)
            self.assertTrue(out.exists())
            with zipfile.ZipFile(out) as zf:
                names = zf.namelist()
                self.assertTrue(any("SKILL.md" in n for n in names))

    # -- new skills exist and validate --

    def test_new_skills_in_all_profile(self) -> None:
        proc = self.run_cli("list", "--json")
        data = json.loads(proc.stdout)
        names = {s["name"] for s in data["skills"]}
        self.assertIn("project-bootstrap", names)
        self.assertIn("debug-helper", names)
        self.assertIn("docs-writer", names)
        self.assertEqual(len(data["skills"]), 7)

    def test_devops_profile(self) -> None:
        proc = self.run_cli("list", "--json")
        data = json.loads(proc.stdout)
        self.assertIn("devops", data["profiles"])

    def test_install_7_skills(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            proc = self.run_cli("install", "--scope", "personal", "--profile", "all", env={"HOME": str(home)})
            self.assertIn("7 skill(s)", proc.stdout)
            skills_dir = home / ".claude" / "skills"
            for expected in ["code-review", "debug-helper", "docs-writer", "example-skill",
                             "git-workflow", "project-bootstrap", "skillpack-maintainer"]:
                self.assertTrue((skills_dir / expected / "SKILL.md").exists(), f"missing: {expected}")

    # -- info for skill with scripts --

    def test_info_skill_with_scripts(self) -> None:
        proc = self.run_cli("info", "example-skill", "--json")
        data = json.loads(proc.stdout)
        self.assertTrue(data["has_scripts"])
        self.assertIn("hello.py", data["script_files"])
        self.assertTrue(data["has_assets"])
        self.assertTrue(data["has_references"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
