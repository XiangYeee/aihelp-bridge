#!/usr/bin/env python3
"""git_local.py 的隔离回归测试。"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("git_local.py")


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, text=True, capture_output=True
    )


class PrepareMrPushTests(unittest.TestCase):
    def test_uses_temporary_branch_when_test_branch_is_checked_out_elsewhere(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            remote = root / "remote.git"
            repo = root / "repo"
            holder = root / "test-holder"
            bin_dir = root / "bin"

            git(root, "init", "--bare", str(remote))
            git(root, "init", str(repo))
            git(repo, "config", "user.name", "Test User")
            git(repo, "config", "user.email", "test@example.com")
            (repo / "base.txt").write_text("base\n", encoding="utf-8")
            git(repo, "add", "base.txt")
            git(repo, "commit", "-m", "base")
            git(repo, "branch", "-M", "test_0903")
            git(repo, "remote", "add", "origin", str(remote))
            git(repo, "push", "-u", "origin", "test_0903")
            git(repo, "switch", "-c", "feature/demo")
            (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
            git(repo, "add", "feature.txt")
            git(repo, "commit", "-m", "feature")
            git(repo, "worktree", "add", str(holder), "test_0903")
            bin_dir.mkdir()
            git_wrapper = bin_dir / "git"
            git_wrapper.write_text(
                "#!/bin/sh\n"
                "if [ \"$1\" = remote ] && [ \"$2\" = get-url ] && [ \"$3\" = origin ]; then\n"
                "  printf '%s\\n' 'git@example.test:Backend/Test.git'\n"
                "  exit 0\n"
                "fi\n"
                f"exec {shutil.which('git')} \"$@\"\n",
                encoding="utf-8",
            )
            git_wrapper.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "prepare-mr-push",
                    "--user",
                    "tester",
                    "--test-branch",
                    "test_0903",
                    "--dev-branch",
                    "feature/demo",
                ],
                cwd=repo,
                text=True,
                capture_output=True,
                env=env,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(git(repo, "branch", "--show-current").stdout.strip(), "feature/demo")
            self.assertEqual(git(holder, "branch", "--show-current").stdout.strip(), "test_0903")
            self.assertEqual(
                git(repo, "branch", "--list", "aihelp-ship/*").stdout.strip(), ""
            )
            self.assertIn(
                "refs/heads/feature/tester/test_0903",
                git(repo, "ls-remote", "--heads", "origin", "feature/tester/test_0903").stdout,
            )


if __name__ == "__main__":
    unittest.main()
