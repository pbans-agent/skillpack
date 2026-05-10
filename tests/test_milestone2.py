#!/usr/bin/env python3
"""Tests for Milestone 2 features.

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


class Milestone2Tests(unittest.TestCase):
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

    # -- status --json --

    def test_status_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            self.run_cli("install", "--scope", "personal", "--profile", "all", env={"HOME": str(home)})
            proc = self.run_cli("status", "--scope", "personal", "--json", env={"HOME": str(home)})
            data = json.loads(proc.stdout)
            self.assertEqual(data["pack_name"], "metaportal-skillpack")
            self.assertIn("skillpack-maintainer", data["managed_skills"])
            self.assertIn("example-skill", data["managed_skills"])
            self.assertIn("installed_commit", data)
            self.assertIn("upgrade_available", data)

    # -- overwrite-unmanaged --

    def test_overwrite_unmanaged(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            # Create an unmanaged skill with the same name.
            unmanaged = home / ".claude" / "skills" / "example-skill"
            unmanaged.mkdir(parents=True)
            (unmanaged / "SKILL.md").write_text("old unmanaged content\n", encoding="utf-8")

            # Install without overwrite: should preserve.
            proc = self.run_cli("install", "--scope", "personal", "--profile", "all", env={"HOME": str(home)})
            self.assertIn("preserved unmanaged", proc.stdout.lower())
            self.assertEqual(
                (unmanaged / "SKILL.md").read_text(encoding="utf-8"),
                "old unmanaged content\n",
            )

            # Install with overwrite: should replace.
            proc = self.run_cli(
                "install", "--scope", "personal", "--profile", "all",
                "--overwrite-unmanaged", env={"HOME": str(home)},
            )
            self.assertIn("OVERWRITE", proc.stdout)
            self.assertNotEqual(
                (unmanaged / "SKILL.md").read_text(encoding="utf-8"),
                "old unmanaged content\n",
            )
            # Should now have the managed marker.
            marker = json.loads((unmanaged / ".skillpack-source.json").read_text(encoding="utf-8"))
            self.assertEqual(marker["managed_by"], "skillpack")

    # -- update no-op --

    def test_update_noop_when_no_changes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            self.run_cli("install", "--scope", "personal", "--profile", "all", env={"HOME": str(home)})
            # Update with --no-pull: same commit, should be no-op.
            proc = self.run_cli(
                "update", "--scope", "personal", "--profile", "all",
                "--no-pull", "--allow-dirty", env={"HOME": str(home)},
            )
            self.assertIn("Nothing to update", proc.stdout)

    # -- update shows diff when skill changes --

    def test_update_shows_diff_on_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            # Install initial.
            self.run_cli("install", "--scope", "personal", "--profile", "all", env={"HOME": str(home)})

            # Modify a skill in the repo to change its hash.
            skill_md = REPO / "skills" / "example-skill" / "SKILL.md"
            original = skill_md.read_text(encoding="utf-8")
            try:
                skill_md.write_text(original + "\n<!-- test modification -->\n", encoding="utf-8")

                # Update with --no-pull --allow-dirty should detect the change.
                proc = self.run_cli(
                    "update", "--scope", "personal", "--profile", "all",
                    "--no-pull", "--allow-dirty", env={"HOME": str(home)},
                )
                self.assertIn("Changed:", proc.stdout)
            finally:
                skill_md.write_text(original, encoding="utf-8")

    # -- prune-managed on update --

    def test_prune_managed_removes_stale(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            # Install with "all" profile (includes example-skill).
            self.run_cli("install", "--scope", "personal", "--profile", "all", env={"HOME": str(home)})
            self.assertTrue((home / ".claude" / "skills" / "example-skill" / "SKILL.md").exists())

            # Now update with coding profile (excludes example-skill) + prune.
            proc = self.run_cli(
                "update", "--scope", "personal", "--profile", "coding",
                "--no-pull", "--allow-dirty", "--prune-managed",
                env={"HOME": str(home)},
            )
            self.assertIn("PRUNED", proc.stdout)
            # example-skill should be gone.
            self.assertFalse((home / ".claude" / "skills" / "example-skill").exists())
            # skillpack-maintainer should still be there (in coding profile).
            self.assertTrue((home / ".claude" / "skills" / "skillpack-maintainer" / "SKILL.md").exists())

    # -- status shows upgrade available (simulated) --

    def test_status_shows_up_to_date(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            self.run_cli("install", "--scope", "personal", "--profile", "all", env={"HOME": str(home)})
            proc = self.run_cli("status", "--scope", "personal", env={"HOME": str(home)})
            # Since we just installed from current commit, should be up to date.
            self.assertIn("Up to date", proc.stdout)

    # -- status json has expected fields --

    def test_status_json_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            self.run_cli("install", "--scope", "personal", "--profile", "all", env={"HOME": str(home)})
            proc = self.run_cli("status", "--scope", "personal", "--json", env={"HOME": str(home)})
            data = json.loads(proc.stdout)
            expected_keys = [
                "pack_name", "pack_version", "repo", "current_commit",
                "scope", "target", "lock_file", "installed_profile",
                "installed_commit", "installed_at", "upgrade_available",
                "managed_skills", "unmanaged_skills",
            ]
            for key in expected_keys:
                self.assertIn(key, data, f"missing key: {key}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
