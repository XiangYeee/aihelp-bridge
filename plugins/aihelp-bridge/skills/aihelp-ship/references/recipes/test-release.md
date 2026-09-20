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

1. 含本地 git 步骤时：必须先 `check-clean`（冲突暂停后的 `resume-mr-push` 除外）。
2. `mr_merge` 失败 → **禁止** `trigger_build`。
3. Job 先查 [jenkins-jobs.md](../jenkins-jobs.md)：`Server_DotNetCore` → `local_backend_dotnetcore_new`；`FastGPT` / AIHelp FastGPT → `local_backend_aihelp-fastgpt`（不要用 match_job 的 `best`）。`Server_DotNetCore` 站点必须是 [dotnetcore-sites.md](../dotnetcore-sites.md) 的精确拼写；其它 parametrized 仓库用 `jenkins_match_parameter_choices`。对不上 → **禁止** `trigger_build`。
4. 本地 merge 冲突 → **禁止** `git merge --abort`、**禁止**切回开发分支清场；见下方「冲突处理」。

## 配方 A：合并 test 分支 + 构建站点

```
1. git_local.py check-clean
2. git_local.py default-test-branch          → test_MMDD
3. MCP gitlab_whoami                         → user
4. git_local.py prepare-mr-push --user … [--test-branch …] [--dev-branch …]
   → 仅用户明确指定源分支时加 --dev-branch
   → exit 0 + status=ok JSON → 继续 5
   → exit 2 + status=conflict JSON → 走「冲突处理」，完成后 resume-mr-push，再继续 5
5. MCP gitlab_mr_list(project, state=opened, source=push_branch, target=test_branch)
   → 有则复用 iid；无则 gitlab_mr_create(..., remove_source_branch=true)
6. MCP gitlab_mr_merge(project, iid, remove_source_branch=true)
   → 失败则停止，不构建；勿在 Agent 层重复重试（MCP 内置退避）
7. Job：先查 [jenkins-jobs.md](../jenkins-jobs.md)
   - Server_DotNetCore → local_backend_dotnetcore_new（不要用 match_job 的 best）
   - FastGPT / AIHelp FastGPT → local_backend_aihelp-fastgpt（禁止 local_backend_fastgpt）
   - 其它仓库：MCP jenkins_match_job(repository_path=project_path)
8. 站点：Server_DotNetCore 按 [dotnetcore-sites.md](../dotnetcore-sites.md) 映射；其它 parametrized 仓库 jenkins_match_parameter_choices；FastGPT 无站点参数
   → 对不上则停止
9. 按 build_type 触发 jenkins_trigger_build：
   - Server_DotNetCore → {branch: test_branch, aaa: values, Re_clone: no}
   - 其它 parametrized → {branch: test_branch, site: values, ACTION: build}
   - multibranch  → job_full_name="{parent}/{test_branch}", parameters={}（含 FastGPT）
   - freestyle    → parameters={}
```

## 冲突处理（prepare-mr-push exit 2）

脚本从 `origin/test_MMDD` 创建了本地临时分支，并留下 **进行中的 merge**（未 abort）。后续都在该临时分支上完成；不会检出或删除本地 `test_MMDD`。

### Agent 自动解决（优先）

对每个冲突文件阅读双方改动，能安全合并的先处理：

| 宜自动处理 | 不宜自动处理（交人） |
|------------|----------------------|
| 双方在不同位置各自新增代码/方法/import | 同一逻辑互斥改写、语义冲突 |
| 无关紧要的空白/格式差异 | 删除 vs 修改同一块业务逻辑 |
| 可机械合并的列表/字典新增项 | 不确定哪边正确、需产品/业务判断 |

处理完一个文件：去掉冲突标记 → `git add <file>`。

**审计输出（必须）**：列出已自动解决的文件 + 每文件改动摘要（保留了哪边/如何合并）；若仍有残留冲突，单独列出并说明为何不能自动解。

- **全部解决** → `git_local.py resume-mr-push --user …`（同参）→ 继续配方步骤 5+；末尾再汇总「本次自动合并做了什么」。
- **仍有残留** → **停住等人**；保持在本地临时分支；不要 abort、不要切回开发分支、不要重跑 `prepare-mr-push`。

### 用户介入后继续

用户说已处理完 / 「继续」时：

```
1. git_local.py merge-status          → 确认无 conflict_files / markers
2. 若仍有冲突 → 再提示用户；勿擅自 abort
3. git_local.py resume-mr-push --user … [--test-branch …] [--dev-branch …]
   → 完成 merge commit（如需要）→ push → 切回开发分支并删本地临时分支
4. 继续配方 A 步骤 5 起（MR → merge → Jenkins）
```

## 配方 B：指定 test 分支构建（无 MR）

```
1. Job 先查 [jenkins-jobs.md](../jenkins-jobs.md)；未命中再 jenkins_match_job
   - Server_DotNetCore → local_backend_dotnetcore_new
   - FastGPT / AIHelp FastGPT → local_backend_aihelp-fastgpt
2. build_type=parametrized：
   - Server_DotNetCore：站点按 [dotnetcore-sites.md](../dotnetcore-sites.md) 映射 → {branch, aaa, Re_clone: no}
   - 其它仓库：jenkins_match_parameter_choices → {branch, site, ACTION: build}
3. build_type=multibranch（含 FastGPT）：
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
python3 <aihelp-ship>/scripts/git_local.py merge-status
python3 <aihelp-ship>/scripts/git_local.py resume-mr-push --user <gitlab用户名> [--test-branch test_MMDD] [--dev-branch feature/或fix/分支]
```

`--dev-branch`：仅用户**明确指定**源分支时使用；否则省略，走自动识别。冲突恢复时优先带上冲突 JSON 里的 `dev_branch` / `test_branch`。

`prepare-mr-push` / `resume-mr-push` 成功末行 JSON：

```json
{"status":"ok","project_path":"group/repo","dev_branch":"feature/…","test_branch":"test_0710","push_branch":"feature/user/test_0710"}
```

冲突暂停（exit 2）末行 JSON（`current_branch` 为本地临时分支）：

```json
{"status":"conflict","project_path":"group/repo","dev_branch":"feature/…","test_branch":"test_0710","push_branch":"feature/user/test_0710","current_branch":"aihelp-ship/user/test_0710-…","merge_in_progress":true,"conflict_files":["path/a.cs"],"hint":"…"}
```

## 交付

打印 MR URL、Jenkins queue/build URL；若发生过自动冲突解决，附带审计摘要。不询问是否打开浏览器。

## 故障

| 现象 | 处理 |
|------|------|
| 工作区不干净 | 停止；commit 或 stash（冲突暂停态除外） |
| 本地 merge 冲突 | **不 abort**；Agent 先自动解 → 必要时等人 → `resume-mr-push` |
| 用户处理完后继续 | `merge-status` 确认干净 → `resume-mr-push` → 续 MR/Jenkins |
| MR merge 失败 | 不触发 Jenkins |
| 站点名对不上 / `project_dir.txt whether this item exists` | 未用 [dotnetcore-sites.md](../dotnetcore-sites.md) 精确拼写（如 `jobcenter`→`JobCenter`）。改完只补未成功站点 |
| MCP 未连接 | 检查宿主 MCP 是否已连接 |
