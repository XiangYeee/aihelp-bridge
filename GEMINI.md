# AIHelp Bridge

This extension connects an agent to AIHelp Bridge.

Skills (activate by task):

- `aihelp-guide`: environment names, platform relationships, MCP routing
- `aihelp-bug`: bug investigation, evidence, graded conclusion
- `aihelp-ship`: test-release and merge-notify copy

When the user mentions AIHelp troubleshooting, logs, tickets, or environments, follow `aihelp-guide` then `aihelp-bug`.
When the user asks to build or ship to test, follow `aihelp-ship`.

MCP 须连公司内网或 VPN。Gemini CLI 不会读取本机环境变量，必须在安装时填写 extension settings，或事后执行 `gemini extensions config aihelp-bridge`。值不要带 Basic / Bearer / AccessKey 前缀。

- `AIHELP_MCP_HOST`：MCP 网关主机名或 IP，不要 `http://` 和端口；向同事或内部文档索取
- `AIHELP_MCP_USER`：account/wiki/jenkins/zentao/elk 的 HTTP 用户名
- `AIHELP_MCP_PASS`：上述服务的 HTTP 密码，填明文，不要 Base64
- `AIHELP_GITLAB_MCP_TOKEN`：公司 GitLab → Preferences → Access Tokens，权限含 `api`，只填 token
- `JUMPSERVER_MCP_ACCESSKEY`：JumpServer 个人中心 API Key，填 `id:secret`
- `AIHELP_LANGFUSE_MCP_USER`：Langfuse MCP 用户名
- `AIHELP_LANGFUSE_MCP_PASS`：Langfuse MCP 密码，填明文，不要 Base64
