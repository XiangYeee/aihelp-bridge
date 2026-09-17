# aihelp-ship — 原子能力目录

Agent 按意图选配方（见 `SKILL.md`），再组合下列原子。

---

## 本地 git（仅 test-release · `scripts/git_local.py`）

| 原子 | 命令 | 输出 / 副作用 |
|------|------|----------------|
| `check_clean` | `check-clean` | 不干净则 exit 1 |
| `default_test_branch` | `default-test-branch` | stdout: `test_MMDD` |
| `prepare_mr_push` | `prepare-mr-push --user U [--test-branch T] [--dev-branch D]` | merge + push；末行 JSON |

**dev 分支**：默认自动识别（`feature/*`、`fix/*`）；仅用户明确指定源分支时传 `--dev-branch`。

**`prepare_mr_push` JSON**：`project_path`, `dev_branch`, `test_branch`, `push_branch`

---

## GitLab MCP（`aihelp-gitlab` · 两配方共用）

| 原子 | 工具 | test-release | merge-notify |
|------|------|:------------:|:------------:|
| `whoami` | `gitlab_whoami` | ✅ | — |
| `branches_list` | `gitlab_branches_list` | — | ✅ 定 target |
| `project_get` | `gitlab_project_get` | 可选 | ✅ |
| `mr_find` | `gitlab_mr_list` | ✅ test 分支 | ✅ develop/main |
| `mr_get` | `gitlab_mr_get` | — | ✅ 已有 MR |
| `mr_create` | `gitlab_mr_create` | ✅ `remove_source_branch: true` | ✅ |
| `mr_merge` | `gitlab_mr_merge` | ✅ 失败不构建；`remove_source_branch: true` | 仅用户明确要求 |

**幂等**：先 `mr_find`，已有 opened MR 则复用。

**目标分支**：

- test-release → `test_MMDD`
- merge-notify → `develop` 优先，否则 `main`

---

## Jenkins MCP（仅 test-release · `aihelp-jenkins`）

| 原子 | 工具 | 说明 |
|------|------|------|
| `match_job` | `jenkins_match_job` | 用 `project_path` 匹配 job，读 `build_type` |
| `match_sites` | `jenkins_match_parameter_choices` | 用户站点输入 → 合法 choices |
| `get_parameters` | `jenkins_get_job_parameters` | 确认 branch/site 参数名（辅助） |
| `infer_job` | `jenkins_get_job` / `jenkins_list_jobs` | 仅 `match_job` 无候选时兜底 |
| `trigger_build` | `jenkins_trigger_build` | 按 `build_type` 触发（见 mcp-tools.md） |

**build_type 与触发**：

- `parametrized` → `trigger_build(parent_job, {branch, site, ACTION})`
- `multibranch` → `trigger_build("{parent}/{branch}", {})`
- `freestyle` → `trigger_build(job, {})`

---

## 禅道 MCP（仅 merge-notify · `aihelp-zentao`）

| 原子 | 工具 | 说明 |
|------|------|------|
| `story_get` | `zentao_get_story` | `include_display: true` |
| `bug_get` | `zentao_get_bug` | `include_display: true` |
| `content_get` | `zentao_get_content` | 备注推断分支（须确认） |
| `search` | `zentao_search_workitems` | `keyword` + `match_mode: exact` |

---

## 组合模板

| 用户说法 | 配方 | 原子序列（摘要） |
|----------|------|------------------|
| 合并本周四 + 构建 elva | test-release | check_clean → … → mr_merge → match_job → match_sites → trigger_build |
| 用 test_0709 构建 | test-release | match_job → match_sites → trigger_build |
| 禅道 + 上线合并通知 | merge-notify | story/bug_get → branches_list → mr_find/create → 组文案 |
| 多需求发群 | merge-notify | 每需求重复 + 模板拼接 |

---

## 门禁

**test-release**

1. 含 git 步骤 → 先 `check_clean`
2. `mr_merge` 失败 → 禁止 `trigger_build`

**merge-notify**

1. 默认不 `mr_merge`
2. 备注推断须用户确认
3. 交付可复制群文案，不代替发群
