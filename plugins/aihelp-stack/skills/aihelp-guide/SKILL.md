---
name: aihelp-guide
description: AIHelp environment, workflow, and tool-routing skill. Trigger when the user explicitly mentions `aihelp`/`AIHelp`, asks to follow AIHelp workflow rules, or the task involves AIHelp environment normalization, local/test/localhost distinction, private deployment mapping, ELK/log investigation, DB/ClickHouse lookup, Apollo config, account/credential lookup, auth/token/OpenAPI signing, admin dashboard navigation, localhost startup, bug/root-cause investigation, ZenTao-linked AIHelp work, GitLab/Jenkins delivery, or AIHelp commit workflow. Do not trigger only because the current repository path contains `AIHelp`; do not use for ordinary code reading, implementation, refactoring, docs editing, or static review when the user does not mention AIHelp and no AIHelp environment/tool/workflow routing is needed.（AIHelp 环境、流程与工具路由技能；用户明确提到 aihelp/AIHelp、要求按 AIHelp 流程，或任务涉及环境标准化、local/test/localhost、私有化、ELK/日志、DB/ClickHouse、Apollo、账号/凭据、鉴权/token/OpenAPI、后台、本地启动、bug/根因、禅道、GitLab/Jenkins、提交时触发；不要仅因路径含 AIHelp 触发。）
---

# AIHelp Guide

本技能是 AIHelp 任务统一入口。

## 规则

- 环境规则：读取 [references/env-policy.md](references/env-policy.md)
- 工具使用规则：读取 [references/tool-use.md](references/tool-use.md)
