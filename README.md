# AIHelp Bridge

连接公司内网 AIHelp 开发平台（GitLab / Jenkins / ELK / DB / Apollo / 禅道等），技能说明各平台关系。

使用前提：已连接公司内网或 VPN。公网不可用。

配置方法：将下列 5 项写入本机环境变量。值不要带 `Basic` / `Bearer` / `AccessKey` 前缀。

1. `AIHELP_MCP_HOST`：MCP 网关主机名或 IP。不要写 `http://`，不要写端口。向同事或内部文档索取。
2. `AIHELP_MCP_BASIC`：account / wiki / jenkins / zentao / elk / es 的 HTTP Basic。生成：`echo -n 'user:password' | base64`，只填 Base64。
3. `AIHELP_GITLAB_MCP_TOKEN`：公司 GitLab → Preferences → Access Tokens，权限含 `api`。只填 token。
4. `JUMPSERVER_MCP_ACCESSKEY`：JumpServer 个人中心 API Key。填 `id:secret`。
5. `AIHELP_LANGFUSE_MCP_BASIC`：Langfuse MCP 的 Base64(user:password)。生成方式同第 2 项。

---

Connect an agent to AIHelp Bridge.

Skills describe how GitLab, Jenkins, ELK, DB, Apollo, account, wiki, and ZenTao relate. MCP provides access to those platforms.

Requires the **company intranet** (office network or VPN). The plugin does not work from the public internet.

Included:

- `aihelp-guide`: environment names and platform routing
- `aihelp-bug`: investigation flow
- `aihelp-ship`: test release and merge-notify copy
- MCP client config for the intranet `aihelp-mcp` gateway

Not included: `aihelp-commit`, dashboard login helpers, localhost process launch, or the MCP server processes themselves.

## Prerequisite

1. Join the company intranet or connect VPN.
2. Confirm you can reach the MCP gateway: `http://$AIHELP_MCP_HOST:18102/mcp`
3. Set the environment variables below.

## Environment variables

Export them as environment variables in your shell. Values must **not** include the HTTP scheme prefix (`Basic ` / `Bearer ` / `AccessKey `).

### `AIHELP_MCP_HOST`

Intranet hostname or IP of the AIHelp MCP gateway. No `http://`, no port.

Ask a teammate or internal docs for the gateway address used by `aihelp-mcp`.

### `AIHELP_MCP_BASIC`

HTTP Basic credential for `aihelp-account`, `aihelp-wiki`, `aihelp-jenkins`, `aihelp-zentao`, `aihelp-elk`, `aihelp-es`.

1. Get the MCP HTTP username and password from your team (this is MCP gateway auth, not a product login).
2. Encode `user:password` as Base64:

```bash
echo -n 'user:password' | base64
```

3. Paste only the Base64 string.

### `AIHELP_GITLAB_MCP_TOKEN`

GitLab Personal Access Token used by the `aihelp-gitlab` MCP (forwarded as GitLab `PRIVATE-TOKEN`).

1. Open company GitLab → Preferences → Access Tokens.
2. Create a token with `api` (needed to create and merge MRs).
3. Paste only the token string, no `Bearer ` prefix.

### `JUMPSERVER_MCP_ACCESSKEY`

JumpServer API AccessKey for the `jumpserver` MCP.

1. Open JumpServer → profile / API Key.
2. Create an AccessKey.
3. Paste `id:secret`, no `AccessKey ` prefix.

### `AIHELP_LANGFUSE_MCP_BASIC`

HTTP Basic credential for `aihelp-langfuse`.

Same encoding as `AIHELP_MCP_BASIC`: Base64 of `user:password`, no `Basic ` prefix. Ask your team for the Langfuse MCP account.

## Install

仓库：https://github.com/XiangYeee/aihelp-bridge

```bash
# Claude Code
claude plugin marketplace add XiangYeee/aihelp-bridge
claude plugin install aihelp-bridge@aihelp-bridge

# Codex
codex plugin marketplace add XiangYeee/aihelp-bridge

# Gemini CLI
# 安装时必须填写 5 项 settings。Gemini 不会读取本机环境变量。
gemini extensions install https://github.com/XiangYeee/aihelp-bridge
# 若安装时跳过了 settings：
gemini extensions config aihelp-bridge

# Grok Build
# 先加 marketplace，再按插件名安装（不要只贴仓库 URL 就结束）
grok plugin marketplace add XiangYeee/aihelp-bridge
grok plugin install aihelp-bridge --trust
# 也可直接按仓库安装：
# grok plugin install XiangYeee/aihelp-bridge --trust
```

Cursor 从 GitHub 加个人 marketplace（不要走 Team Marketplace，不要写本机环境变量）:

1. 若以前加过失败或旧版，先在 Customize → Plugins 里删掉旧插件，再重载窗口。
2. Customize → Plugins → Add marketplace，仓库填 `https://github.com/XiangYeee/aihelp-bridge`
3. 或在 Agent 聊天执行：`/add-plugin https://github.com/XiangYeee/aihelp-bridge`
4. 导入后立刻打开插件 Configure，填写 5 项：AIHELP_MCP_HOST、AIHELP_MCP_BASIC、AIHELP_GITLAB_MCP_TOKEN、JUMPSERVER_MCP_ACCESSKEY、AIHELP_LANGFUSE_MCP_BASIC
5. 值不要带 Basic / Bearer / AccessKey 前缀

Cursor 导入失败见 `docs/cursor-marketplace.md`。不要等几天，云端旧市场记录不会自己改名。

完整条款见 `使用协议.md` 与 `LICENSE`。

If you already configured the same MCP servers in user settings, those take precedence over the plugin.

## License

LicenseRef-AIHelp-Internal. AIHelp employees on the company intranet only. See `LICENSE` and `使用协议.md`.
