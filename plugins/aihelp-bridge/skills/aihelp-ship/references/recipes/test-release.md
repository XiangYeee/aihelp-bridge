# 配方：测试发版（test-release）

**适用**：合并开发分支到 `test_MMDD`、提 MR、自动合并、触发 Jenkins 构建。

**依赖 MCP**：`aihelp-gitlab`、`aihelp-jenkins`  
**本地脚本**：`scripts/git_local.py`

## 触发示例

- 「合并本周四的开发分支，构建 elva」
- 「用 test_0709 构建当前服务」
- 「只提 test MR，不构建」
- 「只构建，不走 MR」

- 「把 fix/xxx 合到 test_0709 验收」

## 开发分支（dev）识别

`prepare-mr-push` **默认自动识别**源分支，**仅当用户明确说出**源分支名时才传 `--dev-branch`：

| 情况 | 行为 |
|------|------|
| 用户未指定源分支 | 不传 `--dev-branch`；脚本按当前分支或 `test_*` 上最近更新的 `feature/*` / `fix/*` 自动识别 |
| 用户明确说「用 fix/xxx」「从 feature/yyy 合并」等 | 传 `--dev-branch fix/xxx`（或对应分支名） |
| 用户只说 test 目标（如 test_0709） | 只传 `--test-branch`，**不要**猜 dev 分支 |

自动识别规则（无 `--dev-branch` 时）：

1. 当前在 `feature/*` 或 `fix/*` → 用当前分支
2. 当前在 `test_MMDD` → 取本地最近提交的 `feature/*` 或 `fix/*`
3. 其它 → 用当前分支名

## 门禁

1. 含本地 git 步骤时：必须先 `check-clean`。
2. `mr_merge` 失败 → **禁止** `trigger_build`。
3. 站点名与 Jenkins 参数不一致 → 用 `jenkins_match_parameter_choices`；仍有 `warnings` 时列出合法值并请用户确认。

## 配方 A：合并 test 分支 + 构建站点

```
1. git_local.py check-clean
2. git_local.py default-test-branch          → test_MMDD
3. MCP gitlab_whoami                         → user
4. git_local.py prepare-mr-push --user … [--test-branch …] [--dev-branch …]
   → 仅用户明确指定源分支时加 --dev-branch
   → JSON: project_path, push_branch, test_branch, dev_branch
5. MCP gitlab_mr_list(project, state=opened, source=push_branch, target=test_branch)
   → 有则复用 iid；无则 gitlab_mr_create(..., remove_source_branch=true)
6. MCP gitlab_mr_merge(project, iid, remove_source_branch=true)
   → 失败则停止，不构建；勿在 Agent 层重复重试（MCP 内置退避）
7. MCP jenkins_match_job(repository_path=project_path)
   → best.job_full_name + best.build_type
8. MCP jenkins_match_parameter_choices(job, site_param, 用户站点)
   → values；有 warnings 时提示用户
9. 按 build_type 触发 jenkins_trigger_build：
   - parametrized → {branch: test_branch, site: values, ACTION: build}
   - multibranch  → job_full_name="{parent}/{test_branch}", parameters={}
   - freestyle    → parameters={}
```

## 配方 B：指定 test 分支构建（无 MR）

```
1. MCP jenkins_match_job(repository_path=当前仓库 project_path)
   → best.job_full_name + best.build_type
2. build_type=parametrized：
   - jenkins_match_parameter_choices(job, site_param, 用户站点) → values
   - trigger_build(job, {branch: test_0709, site: values, ACTION: build})
3. build_type=multibranch：
   - trigger_build("{parent_job}/test_0709", {})
4. build_type=freestyle：
   - trigger_build(job, {})
5. match_job 无候选 → 降级 jenkins_list_jobs / jenkins_get_job 并请用户确认
6. 跳过 git / MR
```

## 配方 C：只提 MR（test → test_MMDD）

执行配方 A 步骤 1–5；不 `mr_merge`、不 Jenkins。

## 配方 D：只构建

同配方 B；无干净工作区要求（若无 git 操作）。

## git_local.py

在**仓库根目录**执行：

```bash
python3 <aihelp-ship>/scripts/git_local.py check-clean
python3 <aihelp-ship>/scripts/git_local.py default-test-branch
python3 <aihelp-ship>/scripts/git_local.py prepare-mr-push --user <gitlab用户名> [--test-branch test_MMDD] [--dev-branch feature/或fix/分支]
```

`--dev-branch`：仅用户**明确指定**源分支时使用；否则省略，走自动识别。

`prepare-mr-push` 成功末行 JSON：

```json
{"project_path":"group/repo","dev_branch":"feature/…","test_branch":"test_0710","push_branch":"feature/user/test_0710"}
```

## 交付

打印 MR URL、Jenkins queue/build URL；不询问是否打开浏览器。

## 故障

| 现象 | 处理 |
|------|------|
| 工作区不干净 | 停止；commit 或 stash |
| 本地 merge 冲突 | 脚本已 abort；解决后重跑 |
| MR merge 失败 | 不触发 Jenkins |
| MCP 未连接 | 检查 mcp.json |
