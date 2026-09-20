# Jenkins Job 固化映射

`jenkins_match_job` 对下列仓库常误匹配。**先查本表，命中则不要用 `best`。**

| Git 仓库 | 口语 / 显示名 | Job | build_type | 站点 |
|---|---|---|---|---|
| `Backend/Server_DotNetCore` | core / Server_DotNetCore | `local_backend_dotnetcore_new` | parametrized | [dotnetcore-sites.md](dotnetcore-sites.md) |
| `ai-agent/FastGPT` | FastGPT / **AIHelp FastGPT** | `local_backend_aihelp-fastgpt` | multibranch | 无；触发 `{job}/{test_branch}` |

未列入本表的仓库再走 `jenkins_match_job`。

## FastGPT

- **只用** `local_backend_aihelp-fastgpt`（Jenkins 显示名 `AIHelp FastGPT`）。
- **禁止** `local_backend_fastgpt`（旧 docker-compose 参数化 job，常与上者同分）。
- **禁止** `local_backend_aihelp-fastgpt-deps`（依赖构建，不是业务发版）。
- 触发：`jenkins_trigger_build("local_backend_aihelp-fastgpt/{test_branch}", {})`。
