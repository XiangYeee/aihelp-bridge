# 上线合并通知 — 输出模板

生成文案时**严格对齐**行序、标点和空行。配方说明见 [recipes/merge-notify.md](recipes/merge-notify.md)。

结尾句默认「今晚上线，帮忙合并」；用户可说「晚上上线，帮忙合并」等替换，**不写 @ 任何人**。

## 单需求 · 单项目（Story）

```
12345 【示例】单项目需求标题
禅道：<zentao_view_url>
合并：<gitlab_mr_url>/diffs

今晚上线，帮忙合并
```

## 单需求 · 单项目（Bug）

```
9526 【示例】单项目缺陷标题
禅道： <zentao_view_url>
合并： <gitlab_mr_url>/diffs

今晚上线，帮忙合并
```

## 单需求 · 多环境

```
21752 【示例】多环境需求标题
禅道：<zentao_view_url>
B站私有化合并：<gitlab_mr_url_a>/diffs
国际国内合并：<gitlab_mr_url_b>/diffs
今晚上线，帮忙合并
```

多环境时结尾句紧跟最后一条合并链接，**中间不再空行**。

## 多需求 · 一条消息

```
20516 【示例】需求 A 标题
禅道：<zentao_view_url_a>
合并：<gitlab_mr_url_a>

21608 【示例】需求 B 标题
禅道：<zentao_view_url_b>
core: <gitlab_mr_url_b>
fastgpt: <gitlab_mr_url_c>

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
