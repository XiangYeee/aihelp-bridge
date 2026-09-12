# AIHelp Stack

This extension connects an agent to the AIHelp development stack.

Skills (activate by task):

- `aihelp-guide`: environment names, platform relationships, MCP routing
- `aihelp-bug`: bug investigation, evidence, graded conclusion
- `aihelp-ship`: test-release and merge-notify copy

When the user mentions AIHelp troubleshooting, logs, tickets, or environments, follow `aihelp-guide` then `aihelp-bug`.
When the user asks to build or ship to test, follow `aihelp-ship`.

MCP 须连公司内网或 VPN。Gemini CLI 不会继承 shell 里 `source ~/.aihelp-stack.env` 的变量，必须在安装时填写 extension settings，或事后执行 `gemini extensions config aihelp-stack`。值不要带 Basic / Bearer / AccessKey 前缀。

- `AIHELP_MCP_HOST`：MCP 网关主机名或 IP，不要 `http://` 和端口；向同事或内部文档索取
- `AIHELP_MCP_BASIC`：account/wiki/jenkins/zentao/elk 的 HTTP Basic，`echo -n 'user:password' | base64`
- `AIHELP_GITLAB_MCP_TOKEN`：公司 GitLab → Preferences → Access Tokens，权限含 `api`，只填 token
- `JUMPSERVER_MCP_ACCESSKEY`：JumpServer 个人中心 API Key，填 `id:secret`
- `AIHELP_LANGFUSE_MCP_BASIC`：Langfuse MCP 的 Base64(user:password)
