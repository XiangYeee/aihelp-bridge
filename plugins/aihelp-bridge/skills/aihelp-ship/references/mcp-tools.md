# aihelp-ship — GitLab / Jenkins / 禅道 MCP 工具参考

**Server id**（Cursor `mcp.json`）：`aihelp-gitlab`、`aihelp-jenkins`、`aihelp-zentao`。

若使用 HTTP 回退，在工作区根目录 `aihelp-mcp.yaml` 中配置：

```yaml
aihelp-gitlab:
  server: aihelp-gitlab
  url: http://${AIHELP_MCP_HOST}:18104/mcp

aihelp-jenkins:
  server: aihelp-jenkins
  url: http://${AIHELP_MCP_HOST}:18105/mcp

aihelp-zentao:
  server: aihelp-zentao
  url: http://${AIHELP_MCP_HOST}:18106/mcp
```

调用前用 MCP 工具列表或内网 `aihelp-mcp` 仓库中 `services/*/README.md` 核对最新 schema。

---

## GitLab

### gitlab_whoami

| 字段 | 值 |
|------|-----|
| server | `aihelp-gitlab` |
| toolName | `gitlab_whoami` |
| arguments | `{}` |

用于获取当前 token 对应用户名 → `git_local.py prepare-mr-push --user`。

### gitlab_mr_list

| 字段 | 值 |
|------|-----|
| toolName | `gitlab_mr_list` |
| arguments | `project`（group/project）, `state`（如 `opened`）, 可选 `source`, `target` |

### gitlab_mr_create

| 字段 | 值 |
|------|-----|
| toolName | `gitlab_mr_create` |
| arguments | `project`, `source`, `target`, `title`, `description`（可选）, `remove_source_branch`（默认 false） |

创建前用 `mr_list` 查重。test-release 临时分支 `feature/{user}/test_MMDD` 建议传 `remove_source_branch: true`。

### gitlab_mr_merge

| 字段 | 值 |
|------|-----|
| toolName | `gitlab_mr_merge` |
| arguments | `project`, `iid`, `squash`（默认 false）, `remove_source_branch`（默认 false） |

合并失败时不要触发 Jenkins。MCP 服务端已对 406/408/409/425/429/502/503 等瞬时错误做指数退避重试（返回 `attempts`）；**Agent 不要再额外重试同一 merge 调用**。test-release 建议传 `remove_source_branch: true`。

### gitlab_project_get

| 字段 | 值 |
|------|-----|
| toolName | `gitlab_project_get` |
| arguments | `project` |

可选：校验 `project_path` 来自 `prepare-mr-push` JSON。

---

## Jenkins

### jenkins_match_job（优先）

| 字段 | 值 |
|------|-----|
| toolName | `jenkins_match_job` |
| arguments | `repository_path`（如 `Backend/Server_DotNetCore`）, 可选 `git_remote`, `limit`（默认 5） |

按 Git 仓库路径匹配 Jenkins job。返回 `best` / `candidates`，含 `job_full_name`、`build_type`（`parametrized` / `multibranch` / `freestyle`）、`scm_remote` 等。

test-release 优先用 `prepare-mr-push` JSON 的 `project_path` 作为 `repository_path`；仅构建场景可用当前仓库 remote 推断。

### jenkins_match_parameter_choices

| 字段 | 值 |
|------|-----|
| toolName | `jenkins_match_parameter_choices` |
| arguments | `job_full_name`, `parameter_name`, `input` |

将用户站点输入与 job 参数 choices 匹配。支持逗号分隔、通配符（`consumer*`）、`all` / `全部`。返回 `values`、`warnings`。

### jenkins_get_job_parameters

| 字段 | 值 |
|------|-----|
| toolName | `jenkins_get_job_parameters` |
| arguments | `job_full_name` |

读取参数定义（参数名、choices）。站点匹配优先用 `jenkins_match_parameter_choices`，本工具用于确认 branch/site 参数名。

### jenkins_get_job / jenkins_list_jobs

兜底：当 `jenkins_match_job` 无候选或需人工确认时，再用手工列举/校验 job 名。

### jenkins_trigger_build

| 字段 | 值 |
|------|-----|
| toolName | `jenkins_trigger_build` |
| arguments | `job_full_name`, `parameters`（对象，无参传 `{}`） |

按 `build_type` 触发：

| build_type | 触发方式 |
|------------|----------|
| `parametrized` | `job_full_name` = 父 job；`parameters` 含 branch、site、ACTION |
| `multibranch` | `job_full_name` = `{parent_job}/{branch}`；`parameters` = `{}` |
| `freestyle` | `job_full_name` = job；`parameters` = `{}` |

**parametrized 示例**（参数名以 job 为准）：

```json
{
  "job_full_name": "local_backend_dotnetcore_new",
  "parameters": {
    "branch": "test_0710",
    "aaa": ["elva"],
    "ACTION": "build"
  }
}
```

**multibranch 示例**（分支名在 job 路径中，无构建参数）：

```json
{
  "job_full_name": "local_backend_some_service/test_0710",
  "parameters": {}
}
```

多选站点以 job 参数定义类型为准（数组或逗号分隔）。

---

## 禅道（merge-notify 配方）

### zentao_get_story / zentao_get_bug

| 字段 | 值 |
|------|-----|
| server | `aihelp-zentao` |
| toolName | `zentao_get_story` 或 `zentao_get_bug` |
| arguments | `story_id` / `bug_id`（整数）, `include_display: true` |

标题：`data.display.basicInfo.标题`；链接：`data.display.links.viewUrl`。

### zentao_get_content

备注正文，用于辅助推断分支/站点（须用户确认）。

### zentao_search_workitems

`keyword` 为禅道编号，`match_mode: exact`。

### GitLab（merge-notify 补充）

- `gitlab_branches_list`：判断 `develop` 是否存在
- `gitlab_mr_get`：已有 MR 的 `web_url`
- 目标分支规则：**develop 优先，否则 main**

---

## 调用方式

1. **优先**：IDE `CallMcpTool`（server = `aihelp-gitlab` / `aihelp-jenkins`）。
2. **回退**：`python3 .agents/skills/_shared/scripts/mcp_call.py --server aihelp-gitlab --tool gitlab_whoami --args '{}'`

鉴权由 `mcp.json` 的 `Authorization` 头提供，skill 内不写 token。

---

## MCP 版本说明

以下能力需 **aihelp-mcp 较新版本**（GitLab `remove_source_branch` + merge 重试；Jenkins `jenkins_match_job` / `jenkins_match_parameter_choices`）。部署前用 `GetMcpTools` 核对 schema；若工具或参数缺失，可暂用手工 `jenkins_list_jobs` + `jenkins_get_job_parameters` 降级，但不要再做 Agent 层 merge 重试。
