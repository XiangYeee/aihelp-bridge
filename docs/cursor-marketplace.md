# Cursor 导入失败（GitHub 改名）

## 结论

不是等两天。Cursor 云端把市场记成了改名前的仓库和目录，不会自动跟着 GitHub 改名更新。

GitHub 现在：`XiangYeee/aihelp-bridge`，插件目录只保留：`plugins/aihelp-bridge`。  
Cursor 必须加这个新地址。改名前的市场记录不要再留。

若 Cursor 还在用改名前的仓库地址：旧 URL 会重定向到新仓库，但会去找已经删掉的旧插件目录，于是 `ENOENT`，看起来像「导入不了」。

界面里删市场若返回 `removeMarketplace not_found`，说明云端旧记录没删掉，再加新地址会被当成同一个市场。

## 正确处理

1. Cursor → Customize → Plugins，把不是 **AIHelp Bridge** 的旧市场/旧插件删掉。删不掉就 Reload Window 再删。
2. 再添加：`https://github.com/XiangYeee/aihelp-bridge`
3. 清单里只能看到 **AIHelp Bridge**（`plugins/aihelp-bridge`）。

不要再用改名前的 GitHub 仓库地址。

界面里如果出现两个都叫 AIHelp Bridge，是清单里曾经同时列出了两份插件、显示名又都写成 Bridge。现在只列 `aihelp-bridge`。若还看到「AIHelp Bridge（旧）」，删那条。

Cursor 个人 marketplace 第一次加成功后，经常把快照钉在旧 commit 上。只推 `main` 不够，上次能加上是因为同时打了 GitHub Release（当时 `v0.2.11`）。改 Cursor 清单后必须打新 Release，再删掉旧市场、Reload、重加。

## 本机缓存

导入失败时，清掉 `~/.cursor/plugins/marketplaces/` 和 `~/.cursor/plugins/cache/` 里与旧市场对应的目录，再 Reload。只保留 `aihelp-bridge`。

## Cursor 清单（不要再改乱）

上次能导入的布局（`1eed4aa`）：

- 根目录必须有 `.cursor-plugin/plugin.json`（GitHub 加插件只认这个）
- `.cursor-plugin/marketplace.json` 的 `source` 用完整相对路径，例如 `plugins/aihelp-bridge`，不要只写插件名，也不要加 `pluginRoot`
- `plugins/aihelp-bridge/` 里再放一份 `.cursor-plugin/plugin.json`、`mcp.json`、`skills/`

不要删根目录 `plugin.json` 只留 marketplace。也不要把 `source` 改成 `./plugins/...` 就当官方模板。

正式插件只有 `plugins/aihelp-bridge`。不要再加第二份插件目录或兼容副本。
