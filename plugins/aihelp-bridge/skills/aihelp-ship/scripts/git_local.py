#!/usr/bin/env python3
"""
git_local.py — aihelp-ship 本地 git 原子操作（无 GitLab/Jenkins API）。

子命令：
  check-clean
  default-test-branch
  prepare-mr-push --user <name> [--test-branch test_MMDD] [--dev-branch feature/xxx|fix/xxx]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


def run_git(cmd: list[str], check: bool = True) -> str:
    result = subprocess.run(
        ["git"] + cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        print(f"[ERROR] git {' '.join(cmd)} failed: {err}", file=sys.stderr)
        sys.exit(1)
    return (result.stdout or "").strip()


def git_ok(cmd: list[str]) -> tuple[bool, str, str]:
    result = subprocess.run(["git"] + cmd, capture_output=True, text=True)
    return result.returncode == 0, (result.stdout or "").strip(), (result.stderr or "").strip()


def require_clean_worktree() -> None:
    if subprocess.run(["git", "diff", "--quiet"]).returncode != 0:
        print("[ERROR] Working tree has unstaged changes. Please commit or stash.", file=sys.stderr)
        sys.exit(1)
    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode != 0:
        print("[ERROR] Index has staged changes. Please commit or stash.", file=sys.stderr)
        sys.exit(1)


def default_test_branch() -> str:
    """本周四 test_MMDD（周一为一周起始）。"""
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    thursday = monday + timedelta(days=3)
    return f"test_{thursday.strftime('%m%d')}"


def get_current_branch() -> str:
    return run_git(["branch", "--show-current"])


def get_remote_url(remote: str = "origin") -> str:
    return run_git(["remote", "get-url", remote])


def get_project_path() -> str | None:
    url = get_remote_url()
    m = re.search(r"@[^:]+:(.+?)(?:\.git)?$", url)
    if m:
        return m.group(1)
    m = re.search(r"//[^/]+/(.+?)(?:\.git)?$", url)
    if m:
        return m.group(1)
    return None


def branch_exists(branch: str) -> bool:
    ok, _, _ = git_ok(["show-ref", "--verify", f"refs/heads/{branch}"])
    return ok


def remote_branch_exists(remote: str, branch: str) -> bool:
    ok, _, _ = git_ok(["ls-remote", "--exit-code", "--heads", remote, branch])
    return ok


def checkout_or_create_branch(branch: str, remote: str = "origin") -> None:
    if branch_exists(branch):
        ok, _, _ = git_ok(["switch", branch])
        if not ok:
            run_git(["checkout", branch])
        if remote_branch_exists(remote, branch):
            run_git(["branch", "--set-upstream-to", f"{remote}/{branch}"])
            run_git(["pull", "--ff-only", remote, branch])
    elif remote_branch_exists(remote, branch):
        ok, _, _ = git_ok(["switch", "-c", branch, f"{remote}/{branch}"])
        if not ok:
            run_git(["checkout", "-b", branch, f"{remote}/{branch}"])
    else:
        ok, _, _ = git_ok(["switch", "-c", branch])
        if not ok:
            run_git(["checkout", "-b", branch])


def is_ancestor(ancestor: str, descendant: str) -> bool:
    ok, _, _ = git_ok(["merge-base", "--is-ancestor", ancestor, descendant])
    return ok


def merge_dev_into_test(dev_branch: str, test_branch: str) -> bool:
    if is_ancestor(dev_branch, test_branch):
        print(f"[INFO] {test_branch} already contains {dev_branch}")
        return True
    print(f"[MERGE] Merging {dev_branch} into {test_branch}...")
    ok, _, err = git_ok(
        ["merge", "--no-ff", "--no-verify", dev_branch, "-m", f"merge {dev_branch} into {test_branch}"]
    )
    if ok:
        return True
    if "conflict" in err.lower() or "merge failed" in err.lower():
        print("[ABORT] Merge conflict. Resolve manually, then re-run prepare-mr-push.", file=sys.stderr)
        subprocess.run(["git", "merge", "--abort"], capture_output=True)
    else:
        print(f"[ERROR] Merge failed: {err}", file=sys.stderr)
    return False


def push_feature_branch(push_branch: str) -> None:
    run_git(["push", "-u", "origin", f"HEAD:{push_branch}", "--force"])


def restore_dev_and_drop_local_test(dev_branch: str, test_branch: str) -> None:
    print(f"[INFO] Switching back to {dev_branch}")
    ok, _, _ = git_ok(["switch", dev_branch])
    if not ok:
        run_git(["checkout", dev_branch])
    print(f"[INFO] Deleting local branch {test_branch}")
    ok, _, err = git_ok(["branch", "-D", test_branch])
    if not ok:
        print(f"[WARN] Could not delete local {test_branch}: {err}")


def detect_dev_branch(current_branch: str, explicit_dev: str | None = None) -> str:
    """自动识别开发分支；仅当传入 explicit_dev 时使用指定分支。"""
    if explicit_dev and explicit_dev.strip():
        dev = explicit_dev.strip()
        print(f"[INFO] DEV_BRANCH={dev} (explicit)")
        if not branch_exists(dev) and not remote_branch_exists("origin", dev):
            print(f"[WARN] Branch {dev} not found locally or on origin", file=sys.stderr)
        return dev

    if current_branch.startswith("feature/") or current_branch.startswith("fix/"):
        return current_branch

    if re.match(r"^test_\d{4}$", current_branch):
        ok, stdout, _ = git_ok(
            [
                "for-each-ref",
                "--sort=-committerdate",
                "--format=%(refname:short)",
                "refs/heads/feature/",
                "refs/heads/fix/",
            ]
        )
        if ok and stdout.strip():
            branch = stdout.strip().split("\n")[0]
            print(f"[INFO] Auto-detected DEV_BRANCH={branch}")
            return branch

    return current_branch


def cmd_check_clean(_: argparse.Namespace) -> None:
    require_clean_worktree()
    print("[OK] Working tree is clean")


def cmd_default_test_branch(_: argparse.Namespace) -> None:
    print(default_test_branch())


def cmd_prepare_mr_push(args: argparse.Namespace) -> None:
    user = (args.user or "").strip()
    if not user:
        print("[ERROR] --user is required (get from MCP gitlab_whoami)", file=sys.stderr)
        sys.exit(1)

    test_branch = (args.test_branch or "").strip() or default_test_branch()
    explicit_dev = (args.dev_branch or "").strip() or None
    current = get_current_branch()
    dev_branch = detect_dev_branch(current, explicit_dev)

    if dev_branch == test_branch:
        print("[ERROR] DEV_BRANCH cannot be the same as TEST_BRANCH", file=sys.stderr)
        sys.exit(1)

    push_branch = f"feature/{user}/{test_branch}"
    project_path = get_project_path()
    if not project_path:
        print("[ERROR] Cannot detect project path from git remote", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] DEV_BRANCH={dev_branch}")
    print(f"[INFO] TEST_BRANCH={test_branch}")
    print(f"[INFO] PUSH_BRANCH={push_branch}")
    print(f"[INFO] PROJECT={project_path}")

    require_clean_worktree()
    run_git(["fetch", "origin", "--prune"])
    checkout_or_create_branch(test_branch, "origin")
    if not merge_dev_into_test(dev_branch, test_branch):
        sys.exit(1)
    push_feature_branch(push_branch)
    restore_dev_and_drop_local_test(dev_branch, test_branch)

    payload = {
        "project_path": project_path,
        "dev_branch": dev_branch,
        "test_branch": test_branch,
        "push_branch": push_branch,
    }
    print(json.dumps(payload, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="aihelp-ship local git atoms")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check-clean", help="Exit 1 if worktree is not clean")

    sub.add_parser("default-test-branch", help="Print test_MMDD for this week's Thursday")

    p_prepare = sub.add_parser("prepare-mr-push", help="Merge dev into test, push feature branch")
    p_prepare.add_argument("--user", required=True, help="GitLab username (from gitlab_whoami)")
    p_prepare.add_argument("--test-branch", default="", help="Override test branch, e.g. test_0709")
    p_prepare.add_argument(
        "--dev-branch",
        default="",
        help="Override dev/source branch (feature/* or fix/*); default auto-detect from current branch",
    )

    args = parser.parse_args()
    if args.command == "check-clean":
        cmd_check_clean(args)
    elif args.command == "default-test-branch":
        cmd_default_test_branch(args)
    elif args.command == "prepare-mr-push":
        cmd_prepare_mr_push(args)


if __name__ == "__main__":
    main()
