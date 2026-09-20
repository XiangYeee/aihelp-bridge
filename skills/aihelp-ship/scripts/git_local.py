#!/usr/bin/env python3
"""
git_local.py — aihelp-ship 本地 git 原子操作（无 GitLab/Jenkins API）。

子命令：
  check-clean
  default-test-branch
  merge-status
  prepare-mr-push --user <name> [--test-branch test_MMDD] [--dev-branch feature/xxx|fix/xxx]
  resume-mr-push  --user <name> [--test-branch test_MMDD] [--dev-branch feature/xxx|fix/xxx]

冲突策略：
  merge 冲突时不 abort、不切回开发分支；停留在本地临时分支上，exit 2 + JSON。
  Agent 可先尝试自动解决；解决不了则等人介入。完成后跑 resume-mr-push。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NEEDS_ATTENTION = 2


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
        sys.exit(EXIT_ERROR)
    return (result.stdout or "").strip()


def git_ok(cmd: list[str]) -> tuple[bool, str, str]:
    result = subprocess.run(["git"] + cmd, capture_output=True, text=True)
    return result.returncode == 0, (result.stdout or "").strip(), (result.stderr or "").strip()


def require_clean_worktree() -> None:
    if subprocess.run(["git", "diff", "--quiet"]).returncode != 0:
        print("[ERROR] Working tree has unstaged changes. Please commit or stash.", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode != 0:
        print("[ERROR] Index has staged changes. Please commit or stash.", file=sys.stderr)
        sys.exit(EXIT_ERROR)


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


def create_temporary_test_branch(user: str, test_branch: str) -> str:
    """从 origin/test 创建一次性本地合并分支，避免占用已有 test worktree。"""
    local_branch = f"aihelp-ship/{user}/{test_branch}-{time.time_ns()}"
    run_git(["switch", "-c", local_branch, f"origin/{test_branch}"])
    return local_branch


def is_ancestor(ancestor: str, descendant: str) -> bool:
    ok, _, _ = git_ok(["merge-base", "--is-ancestor", ancestor, descendant])
    return ok


def merge_in_progress() -> bool:
    git_dir = Path(run_git(["rev-parse", "--git-dir"]))
    return (git_dir / "MERGE_HEAD").exists()


def list_unmerged_files() -> list[str]:
    ok, stdout, _ = git_ok(["diff", "--name-only", "--diff-filter=U"])
    if not ok or not stdout.strip():
        return []
    return [line.strip() for line in stdout.splitlines() if line.strip()]


def has_conflict_markers(paths: list[str]) -> list[str]:
    """Return files that still contain conflict markers."""
    marked: list[str] = []
    pattern = re.compile(r"^<<<<<<< |^=======$|^>>>>>>> ", re.MULTILINE)
    for rel in paths:
        path = Path(rel)
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if pattern.search(text):
            marked.append(rel)
    return marked


def emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def conflict_payload(
    *,
    project_path: str,
    dev_branch: str,
    test_branch: str,
    push_branch: str,
    conflict_files: list[str],
) -> dict[str, Any]:
    return {
        "status": "conflict",
        "project_path": project_path,
        "dev_branch": dev_branch,
        "test_branch": test_branch,
        "push_branch": push_branch,
        "current_branch": get_current_branch(),
        "merge_in_progress": merge_in_progress(),
        "conflict_files": conflict_files,
        "hint": (
            "Merge paused on a local temporary branch (not aborted). "
            "Agent: try auto-resolve simple conflicts, report edits; "
            "if leftovers remain, wait for user. Then run resume-mr-push."
        ),
    }


def start_merge_dev_into_test(
    dev_branch: str, local_test_branch: str, test_branch: str
) -> str:
    """
    Start merge. Returns:
      'already' — test already contains dev
      'ok' — merge committed cleanly
      'conflict' — merge in progress with conflicts (NOT aborted)
      'error' — non-conflict failure
    """
    if is_ancestor(dev_branch, local_test_branch):
        print(f"[INFO] {test_branch} already contains {dev_branch}")
        return "already"

    print(f"[MERGE] Merging {dev_branch} into {test_branch}...")
    ok, stdout, err = git_ok(
        ["merge", "--no-ff", "--no-verify", dev_branch, "-m", f"merge {dev_branch} into {test_branch}"]
    )
    if ok:
        return "ok"

    combined = f"{stdout}\n{err}".lower()
    conflicts = list_unmerged_files()
    if conflicts or "conflict" in combined or merge_in_progress():
        print(
            "[PAUSE] Merge conflict — staying on the local temporary branch (not aborted). "
            "Resolve in place, then resume-mr-push.",
            file=sys.stderr,
        )
        for path in conflicts:
            print(f"[CONFLICT] {path}", file=sys.stderr)
        return "conflict"

    print(f"[ERROR] Merge failed: {err or stdout}", file=sys.stderr)
    return "error"


def complete_merge_if_needed(dev_branch: str, test_branch: str) -> None:
    """If MERGE_HEAD exists and no unmerged paths, commit the merge."""
    if not merge_in_progress():
        return

    unmerged = list_unmerged_files()
    if unmerged:
        print("[ERROR] Unmerged paths remain:", file=sys.stderr)
        for path in unmerged:
            print(f"  - {path}", file=sys.stderr)
        marked = has_conflict_markers(unmerged)
        if marked:
            print("[ERROR] Conflict markers still present in:", file=sys.stderr)
            for path in marked:
                print(f"  - {path}", file=sys.stderr)
        sys.exit(EXIT_NEEDS_ATTENTION)

    msg = f"merge {dev_branch} into {test_branch}"
    ok, _, err = git_ok(["commit", "--no-verify", "-m", msg])
    if not ok:
        # Empty commit edge case: all resolved to already-staged identical tree
        if "nothing to commit" in (err or "").lower():
            run_git(["commit", "--no-verify", "--allow-empty", "-m", msg])
        else:
            print(f"[ERROR] Failed to complete merge commit: {err}", file=sys.stderr)
            sys.exit(EXIT_ERROR)
    print("[OK] Merge commit completed")


def push_feature_branch(push_branch: str) -> None:
    run_git(["push", "-u", "origin", f"HEAD:{push_branch}", "--force"])


def restore_dev_and_drop_local_test(dev_branch: str, local_test_branch: str) -> None:
    print(f"[INFO] Switching back to {dev_branch}")
    ok, _, _ = git_ok(["switch", dev_branch])
    if not ok:
        run_git(["checkout", dev_branch])
    print(f"[INFO] Deleting local temporary branch {local_test_branch}")
    ok, _, err = git_ok(["branch", "-D", local_test_branch])
    if not ok:
        print(f"[WARN] Could not delete local temporary branch {local_test_branch}: {err}")


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


def resolve_context(args: argparse.Namespace, *, allow_dirty: bool) -> dict[str, str]:
    user = (args.user or "").strip()
    if not user:
        print("[ERROR] --user is required (get from MCP gitlab_whoami)", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    test_branch = (args.test_branch or "").strip() or default_test_branch()
    explicit_dev = (args.dev_branch or "").strip() or None
    current = get_current_branch()
    # 临时分支上的恢复流程从 MERGE_MSG / 最近 merge commit 还原开发分支。
    if (merge_in_progress() or current.startswith("aihelp-ship/")) and not explicit_dev:
        # Best-effort: MERGE_HEAD's first-parent side is test; merged branch name from MERGE_MSG
        dev_branch = _dev_from_merge_msg() or detect_dev_branch(current, None)
    else:
        dev_branch = detect_dev_branch(current, explicit_dev)

    if dev_branch == test_branch:
        print("[ERROR] DEV_BRANCH cannot be the same as TEST_BRANCH", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    push_branch = f"feature/{user}/{test_branch}"
    project_path = get_project_path()
    if not project_path:
        print("[ERROR] Cannot detect project path from git remote", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    if not allow_dirty:
        require_clean_worktree()

    return {
        "user": user,
        "dev_branch": dev_branch,
        "test_branch": test_branch,
        "push_branch": push_branch,
        "project_path": project_path,
    }


def _dev_from_merge_msg() -> str | None:
    git_dir = Path(run_git(["rev-parse", "--git-dir"]))
    msg_file = git_dir / "MERGE_MSG"
    text = ""
    if msg_file.is_file():
        try:
            text = msg_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            pass
    if not text:
        text = run_git(["log", "-1", "--format=%B"])
    m = re.search(r"merge\s+(\S+)\s+into\s+\S+", text)
    if m:
        return m.group(1)
    return None


def finish_push_and_restore(ctx: dict[str, str], local_test_branch: str) -> None:
    push_feature_branch(ctx["push_branch"])
    restore_dev_and_drop_local_test(ctx["dev_branch"], local_test_branch)
    emit_json(
        {
            "status": "ok",
            "project_path": ctx["project_path"],
            "dev_branch": ctx["dev_branch"],
            "test_branch": ctx["test_branch"],
            "push_branch": ctx["push_branch"],
        }
    )


def cmd_check_clean(_: argparse.Namespace) -> None:
    require_clean_worktree()
    print("[OK] Working tree is clean")


def cmd_default_test_branch(_: argparse.Namespace) -> None:
    print(default_test_branch())


def cmd_merge_status(_: argparse.Namespace) -> None:
    conflicts = list_unmerged_files()
    marked = has_conflict_markers(conflicts) if conflicts else []
    payload = {
        "status": "conflict" if conflicts else ("merging" if merge_in_progress() else "idle"),
        "current_branch": get_current_branch(),
        "merge_in_progress": merge_in_progress(),
        "conflict_files": conflicts,
        "files_with_markers": marked,
    }
    emit_json(payload)
    if conflicts:
        sys.exit(EXIT_NEEDS_ATTENTION)


def cmd_prepare_mr_push(args: argparse.Namespace) -> None:
    if merge_in_progress():
        print(
            "[ERROR] Merge already in progress. Resolve conflicts (or abort manually), "
            "then run resume-mr-push — do not re-run prepare-mr-push.",
            file=sys.stderr,
        )
        conflicts = list_unmerged_files()
        for path in conflicts:
            print(f"[CONFLICT] {path}", file=sys.stderr)
        sys.exit(EXIT_NEEDS_ATTENTION)

    ctx = resolve_context(args, allow_dirty=False)

    print(f"[INFO] DEV_BRANCH={ctx['dev_branch']}")
    print(f"[INFO] TEST_BRANCH={ctx['test_branch']}")
    print(f"[INFO] PUSH_BRANCH={ctx['push_branch']}")
    print(f"[INFO] PROJECT={ctx['project_path']}")

    run_git(["fetch", "origin", "--prune"])
    local_test_branch = create_temporary_test_branch(ctx["user"], ctx["test_branch"])

    result = start_merge_dev_into_test(
        ctx["dev_branch"], local_test_branch, ctx["test_branch"]
    )
    if result == "error":
        sys.exit(EXIT_ERROR)
    if result == "conflict":
        emit_json(
            conflict_payload(
                project_path=ctx["project_path"],
                dev_branch=ctx["dev_branch"],
                test_branch=ctx["test_branch"],
                push_branch=ctx["push_branch"],
                conflict_files=list_unmerged_files(),
            )
        )
        sys.exit(EXIT_NEEDS_ATTENTION)

    # already or ok
    finish_push_and_restore(ctx, local_test_branch)


def cmd_resume_mr_push(args: argparse.Namespace) -> None:
    """Continue after conflict resolution (agent or user). Stay path → push → restore."""
    ctx = resolve_context(args, allow_dirty=True)

    print(f"[INFO] DEV_BRANCH={ctx['dev_branch']}")
    print(f"[INFO] TEST_BRANCH={ctx['test_branch']}")
    print(f"[INFO] PUSH_BRANCH={ctx['push_branch']}")
    print(f"[INFO] PROJECT={ctx['project_path']}")

    current = get_current_branch()
    if not current.startswith("aihelp-ship/"):
        print(
            f"[ERROR] Current branch is {current}; expected the temporary aihelp-ship branch. "
            "Do not switch branches while resolving the merge.",
            file=sys.stderr,
        )
        sys.exit(EXIT_ERROR)

    if merge_in_progress():
        unmerged = list_unmerged_files()
        if unmerged:
            emit_json(
                conflict_payload(
                    project_path=ctx["project_path"],
                    dev_branch=ctx["dev_branch"],
                    test_branch=ctx["test_branch"],
                    push_branch=ctx["push_branch"],
                    conflict_files=unmerged,
                )
            )
            sys.exit(EXIT_NEEDS_ATTENTION)
        complete_merge_if_needed(ctx["dev_branch"], ctx["test_branch"])
    else:
        leftover = list_unmerged_files()
        if leftover:
            emit_json(
                conflict_payload(
                    project_path=ctx["project_path"],
                    dev_branch=ctx["dev_branch"],
                    test_branch=ctx["test_branch"],
                    push_branch=ctx["push_branch"],
                    conflict_files=leftover,
                )
            )
            sys.exit(EXIT_NEEDS_ATTENTION)
        print("[INFO] No merge in progress — assuming conflicts already committed")

    finish_push_and_restore(ctx, current)


def main() -> None:
    parser = argparse.ArgumentParser(description="aihelp-ship local git atoms")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check-clean", help="Exit 1 if worktree is not clean")
    sub.add_parser("default-test-branch", help="Print test_MMDD for this week's Thursday")
    sub.add_parser("merge-status", help="Print JSON merge/conflict status")

    p_prepare = sub.add_parser("prepare-mr-push", help="Merge dev into test, push feature branch")
    p_prepare.add_argument("--user", required=True, help="GitLab username (from gitlab_whoami)")
    p_prepare.add_argument("--test-branch", default="", help="Override test branch, e.g. test_0709")
    p_prepare.add_argument(
        "--dev-branch",
        default="",
        help="Override dev/source branch (feature/* or fix/*); default auto-detect from current branch",
    )

    p_resume = sub.add_parser(
        "resume-mr-push",
        help="After conflict resolve: complete merge commit if needed, push, restore",
    )
    p_resume.add_argument("--user", required=True, help="GitLab username (from gitlab_whoami)")
    p_resume.add_argument("--test-branch", default="", help="Override test branch, e.g. test_0709")
    p_resume.add_argument(
        "--dev-branch",
        default="",
        help="Override dev/source branch; default from MERGE_MSG or auto-detect",
    )

    args = parser.parse_args()
    if args.command == "check-clean":
        cmd_check_clean(args)
    elif args.command == "default-test-branch":
        cmd_default_test_branch(args)
    elif args.command == "merge-status":
        cmd_merge_status(args)
    elif args.command == "prepare-mr-push":
        cmd_prepare_mr_push(args)
    elif args.command == "resume-mr-push":
        cmd_resume_mr_push(args)


if __name__ == "__main__":
    main()
