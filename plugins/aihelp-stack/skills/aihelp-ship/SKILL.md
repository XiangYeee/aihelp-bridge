---
name: aihelp-ship
description: 零配置发版与上线编排：测试发版（test 分支 + Jenkins）与正式上线通知（禅道 + develop MR + 群文案）。自然语言组合本地 git 与 GitLab/Jenkins/禅道 MCP。触发如「合并本周四开发分支构建 elva」「用 test_0709 构建」「今晚上线，帮忙合并发群通知」。
metadata:
  teams: [developer]
compatibility: |
  需要：git、python3（仅 test-release 配方）；已配置 aihelp-gitlab、aihelp-jenkins、aihelp-zentao MCP（本插件 .mcp.json，或用户 mcp.json / config.toml）。
  鉴权：环境变量或用户 MCP 配置，不在 skill 内维护 token。
---

# aihelp-ship

发版与上线 skill：**自然语言意图 → 选配方 → 原子步骤（git_local + MCP）**。

零配置：无需项目级配置文件；鉴权仅 `mcp.json`；Jenkins job 与构建类型由 MCP 推断。

## 配方路由

| 用户意图 | 配方 | 文档 |
|----------|------|------|
| 合并本周四开发分支、构建站点、test 分支发版 | **test-release** | [recipes/test-release.md](references/recipes/test-release.md) |
| 用 test_MMDD 构建、只构建不 MR | **test-release** | 同上 |
| 今晚上线、合并通知、禅道 + develop MR、发群文案 | **merge-notify** | [recipes/merge-notify.md](references/recipes/merge-notify.md) |
| 多需求/多项目上线通知 | **merge-notify** | 同上 + [merge-notify-templates.md](references/merge-notify-templates.md) |

**歧义消解**：

- 「提 MR」+ **test / 构建 / elva** → test-release
- 「提 MR」+ **禅道 / 上线 / develop / 发群** → merge-notify

## 前置条件

| 配方 | MCP | 其他 |
|------|-----|------|
| test-release | `aihelp-gitlab`、`aihelp-jenkins` | 仓库根 git；MR 路径需干净工作区 |
| merge-notify | `aihelp-gitlab`、`aihelp-zentao` | 无本地 git 要求 |

可选：`aihelp-mcp.yaml` 声明 HTTP 地址（见 [references/mcp-tools.md](references/mcp-tools.md)）。

## 全局执行原则

1. **零配置**：鉴权仅 `mcp.json`。
2. **test-release 本地 git**：只用 `scripts/git_local.py`，禁止 ad-hoc git 替代 merge/push。`--dev-branch` 仅在用户明确说出源分支名时传入，默认自动识别（含 `feature/*` 与 `fix/*`）。
3. **远程 API**：只用 MCP，禁止 curl 直连 GitLab/Jenkins/禅道。
4. **test-release 门禁**：MR merge 失败 → 不触发 Jenkins；工作区不干净 → 停止。
5. **merge-notify**：默认**不** `gitlab_mr_merge`、不代替发群；输出可复制正文。

## 原子能力

见 [references/atoms.md](references/atoms.md)。

| 层 | 用途 |
|----|------|
| `git_local.py` | 仅 test-release |
| GitLab MCP | 两配方共用 |
| Jenkins MCP | 仅 test-release |
| 禅道 MCP | 仅 merge-notify |

## MCP 工具索引

[references/mcp-tools.md](references/mcp-tools.md) — GitLab、Jenkins、禅道工具与 aihelp-mcp 待补齐项。
