# 配方：上线合并通知（merge-notify）

**适用**：开发分支 → `develop`/`main` 的 MR + 禅道信息 + **可复制群通知文案**。

**依赖 MCP**：`aihelp-gitlab`、`aihelp-zentao`  
**不使用**：`git_local.py`、Jenkins、`gitlab_mr_merge`（除非用户明确要求自动合并）

原独立 skill `merge-release-notify` 已并入 aihelp-ship 本配方。

## 触发示例

- 「今晚上线，帮忙合并，发群通知」
- 「禅道 21434 提 MR 整理合并链接」
- 「多个需求一起生成上线通知」

**不走本配方**：test 分支发版、Jenkins 构建 → [test-release.md](test-release.md)

## 目标

自动化「禅道 + GitLab MR 链接 → 固定格式群文案」。全文末尾加一句结尾语，默认「今晚上线，帮忙合并」，**不写 @ 任何人**。

## 输入模式

支持两种入口，**不要强迫用户逐条填表**——信息够用时直接执行。

### A. 一次性输入

用户已给出禅道号、分支、项目、已有 MR 等，直接解析并补全缺失项。

### B. 分步确认（AskQuestion）

信息不足时按顺序追问，**每轮只问当前缺口**：

1. 本次几个需求？
2. 每个需求：禅道号、项目数/环境数、源分支、是否已有 MR
3. 合并链接是否带 `/diffs`（默认带）
4. 结尾语措辞（默认「今晚上线，帮忙合并」；如「晚上上线，帮忙合并」）

## 执行清单

对每个「需求 × 项目/环境」：

```
- [ ] 1. 拉取禅道标题与链接
- [ ] 2. 确定 GitLab 项目与源分支
- [ ] 3. 确定目标分支（develop 优先）
- [ ] 4. 查询或创建 MR
- [ ] 5. 组装该需求块文案
- [ ] 6. 拼接全文 + 结尾句
```

### 1. 禅道

- Story：`zentao_get_story`（`include_display: true`）
- Bug：`zentao_get_bug`（`include_display: true`）

取用：

- **标题**：`data.display.basicInfo.标题` 或 `data.story.title` / `data.bug.title`
- **链接**：`data.display.links.viewUrl`

类型：用户明说；或先试 story 再 bug；或 `zentao_search_workitems` + `keyword` + `match_mode: exact`。

**从备注推断分支/项目**（仅辅助，须用户确认）：

- `zentao_get_content` / `display.timeline` 备注
- 分支：`分支[:：]\s*(\S+)`、`branch[:：]\s*(\S+)`
- 站点：`站点[:：]\s*(\S+)`

### 2. GitLab 目标分支

1. `gitlab_branches_list` 查是否有 `develop`
2. **有 develop → target = develop**
3. **无 develop → target = main**

### 3. MR

**已有 MR**：`gitlab_mr_get` → `web_url` + 可选 `/diffs`

**新建 MR**：

1. `gitlab_mr_list`：`state=opened`，source + target
2. 已有 opened → 复用 `web_url`
3. 否则 `gitlab_mr_create`（title 如 `{禅道号}_{标题简写}`，description 可含禅道链接）

**不自动 merge**（除非用户明确要求）。

### 4. 项目路径别名

| 别名 | project |
|------|---------|
| core / Server_DotNetCore | `Backend/Server_DotNetCore` |
| golang / bot | `Backend/aihelp_server_golang` |
| fastgpt | `ai-agent/FastGPT` |

不确定则 AskQuestion 确认 `group/project`。

## 输出模板

完整样例见 [../merge-notify-templates.md](../merge-notify-templates.md)。

### 交付

1. 简短列表：每个需求的禅道链接、MR 链接、是否新建 MR
2. **完整可复制正文**放在单独代码块，不加额外 markdown 标题
3. **不代替用户发群**

## 错误处理

| 情况 | 处理 |
|------|------|
| 禅道号不存在 | 换号或确认 story/bug |
| 源分支不存在 | `gitlab_branches_list` 列相近分支 |
| MR 创建失败 | `gitlab_mr_list` 按 source 查 opened MR |
| 多环境/多项目不全 | 追问环境标签与路径、分支 |
| 备注与用户输入冲突 | 以用户最新输入为准 |
