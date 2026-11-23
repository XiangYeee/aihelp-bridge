# Agents.md

给在本仓库工作的 AI 编码助手。远程 `main` 是各客户端拉取的插件源。动手前先快进 `origin/main`，本地落后时直接改会盖掉已推送的提交。

## 版本号

以根目录 `plugin.json` 的 `version` 为准。升版本时下面全部改成同一个号，改完检索 `0.4.`，这些文件里不能留下更旧的号。

- 各端 `plugin.json`：根目录、`.claude-plugin/`、`.codex-plugin/`、`.cursor-plugin/`、`.grok-plugin/`、`plugins/aihelp-bridge/.cursor-plugin/`
- 市场目录：`.claude-plugin/marketplace.json`、`.grok-plugin/marketplace.json` 里该插件的 `version`；`.cursor-plugin/marketplace.json` 的 `metadata.version`
- `gemini-extension.json`，以及 `使用协议.md` 文首「版本」

`.agents/plugins/marketplace.json` 没有 `version`，不要另写一个不同的号。

漏改市场目录时，客户端会把新包显示成降级。Grok 比较的是 `.grok-plugin/marketplace.json`，不是 `plugin.json`。`f9239a0` 只把 `plugin.json` 升到 `0.4.6`，Grok 目录仍是 `0.4.2`，于是提示 `v0.4.6 → v0.4.2`。检出的代码仍是 `0.4.6`，没有回滚。

## 推送后不会自己更新

- Grok：`grok plugin marketplace update aihelp-bridge`，再 `grok plugin update aihelp-bridge`。只更新安装目录；当前会话仍用旧技能，新开会话才生效。
- Cursor 个人市场钉住第一次导入成功的 commit。只推 `main`，已添加的市场不变。要先打 GitHub Release，再在 Customize → Plugins 删掉旧市场、Reload Window，重新添加 `https://github.com/XiangYeee/aihelp-bridge`。不要走 Team Marketplace。
- Codex 缓存同样不跟 `main` 走，要在 Codex 里更新插件。

## Cursor 清单

能导入的布局不要改回以前试过的样子：

- 保留根目录 `.cursor-plugin/plugin.json`。删掉它，GitHub 导入不认。
- `.cursor-plugin/marketplace.json` 的 `source` 只能是 `plugins/aihelp-bridge`。不要写成插件名、`pluginRoot`，或 `./plugins/aihelp-bridge`。
- `plugins/aihelp-bridge/` 里保留 `.cursor-plugin/plugin.json`、`mcp.json`、`skills/`。市场只列这一份插件。

不要恢复 `plugins/aihelp-stack` 或改名前的仓库地址。旧 URL 会重定向到本仓库，但 Cursor 云端仍按已删除的旧目录取文件，报 `ENOENT`，等几天不会自己好。界面删市场若返回 `removeMarketplace not_found`，是云端旧记录还在，再加新地址会被当成同一个市场。清单里出现两个 AIHelp Bridge，是曾经同时列了两份插件。处理步骤见 `docs/cursor-marketplace.md`。

## 配置与技能

Cursor 的 5 项凭据写在插件 Configure，不写本机环境变量。Grok、Codex、Claude 写环境变量。Gemini 在安装时填 settings，不读环境变量。Antigravity（`agy`）读取根目录 `mcp_config.json`，安装后在 `/plugin` 启用并填写 5 项变量。值不要带 `Basic` / `Bearer` / `AccessKey` 前缀。

技能有两份，一起改：`skills/<name>/` 与 `plugins/aihelp-bridge/skills/<name>/`。不要改 `~/.grok/installed-plugins/`、`~/.cursor/plugins/`、`~/.codex/plugins/`。
