# 上线合并通知 — 输出模板

生成文案时**严格对齐**行序、标点和空行。配方说明见 [recipes/merge-notify.md](recipes/merge-notify.md)。

结尾句默认「今晚上线，帮忙合并」；用户可说「晚上上线，帮忙合并」等替换，**不写 @ 任何人**。

## 单需求 · 单项目（Story）

```
21434 【B站私有化】企微账号换绑应用后支持过滤历史玩家消息 
禅道：https://pm.aihelp.net/story-view-21434.html?tid=7r60img8
合并：https://git.aihelp.net/Backend/Server_DotNetCore/-/merge_requests/18130/diffs

今晚上线，帮忙合并
```

## 单需求 · 单项目（Bug）

```
9526 【是否已解决】按钮的语言与用户设置的语言不一致，帮忙查看问题原因
禅道： https://pm.aihelp.net/bug-view-9526.html?tid=7r60img8
合并： https://git.aihelp.net/Backend/aihelp_server_golang/-/merge_requests/1747/diffs

今晚上线，帮忙合并
```

## 单需求 · 多环境

```
21752 AI质检任务需要支持负分段搜索
禅道：https://pm.aihelp.net/story-view-21752.html?tid=jp99y100
B站私有化合并：https://git.aihelp.net/Backend/Server_DotNetCore/-/merge_requests/18127/diffs
国际国内合并：https://git.aihelp.net/Backend/Server_DotNetCore/-/merge_requests/18133/diffs
今晚上线，帮忙合并
```

多环境时结尾句紧跟最后一条合并链接，**中间不再空行**。

## 多需求 · 一条消息

```
20516 AI推荐回复功能重构优化
禅道：https://pm.aihelp.net/story-view-20516.html?tid=fecri7io
合并：https://git.aihelp.net/Backend/Server_DotNetCore/-/merge_requests/18069

21608 人工 AI 助手调用 TH 助手路径调整
禅道：https://pm.aihelp.net/story-view-21608.html?tid=fecri7io
core: https://git.aihelp.net/Backend/Server_DotNetCore/-/merge_requests/18071
fastgpt: https://git.aihelp.net/ai-agent/FastGPT/-/merge_requests/196

晚上上线，帮忙合并
```

多需求时全文末尾**只保留一个**结尾句。

## 字段来源

| 输出段 | MCP 来源 |
|--------|----------|
| 首行编号 | 禅道 id |
| 首行标题 | `display.basicInfo.标题` |
| 禅道 URL | `display.links.viewUrl` |
| 合并 URL | `merge_request.web_url` + `/diffs`（可选） |
| 环境/项目前缀 | 用户输入 |
| 结尾句 | 默认「今晚上线，帮忙合并」，跟随用户措辞 |

## /diffs 规则

- 默认追加 `/diffs`
- 用户说「不要 diffs」或样例风格无 diffs 时省略
