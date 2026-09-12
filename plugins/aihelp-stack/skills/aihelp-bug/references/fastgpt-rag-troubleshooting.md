# FastGPT/gpt-rag 客诉回复排查流程

当 AIHelp bug 涉及 FastGPT、gpt-rag、AI 回复错误、AI-bad case、机器人回复不准、客诉回复命中错误、需要对比 FastGPT 节点明细时，使用本流程。

## 目标

- 用客诉事实定位玩家原话、AI 实际回复和发生时间。
- 从日志中找到真正调用 FastGPT gpt-rag 的那条请求。
- 将同一请求重放为 `detail=true`，拿到 FastGPT 节点执行结果。
- 对照 FastGPT 项目 `main` 分支最新 gpt-rag 模板，判断问题归属：问题重写、实体召回、知识检索、回答生成、润色、缓存或上游入参。

## 客诉库查询规则

1. 数据库连接从 account 平台获取：
   - group：`aihelp_account`
   - title：`mysql_rpa_slave`
2. 客诉表固定查 `bs_ticket`，按租户分库：
   - `accountId = 2`：查 `aihelp_ticket_2.bs_ticket`
   - `accountId = 79`：查 `aihelp_ticket_79.bs_ticket`
   - 其他租户：查 `aihelp_ticket_other.bs_ticket`
3. 用户给的 id 不一定是客诉短 id，也可能是完整 `ticketId`。查询条件必须兼容：
   - `id = ?`
   - `ticketId = ?`
   - 已知 `gameId` 时必须一起过滤。
4. 从 `bs_ticket` 至少确认：
   - `ticketId`
   - `id`，即短 id
   - `gameId`
   - `accountId`
   - `content`
   - `playerContent`
   - `createTime`
   - `replyTime`

## 日志定位规则

1. 优先按 `ticketId`、短 id、`gameId`、玩家原话、`replyTime/createTime` 在 ELK 中收缩时间窗口。
2. 先查入口和上游链路：
   - `logstash-dotnet_web_ticket*`
   - 重点 service：`aihelp_ticket_webserver`、`internalapi`
   - 常见路径：`/internalapi/chat/aigc`
3. 再查消费侧真实 FastGPT 调用：
   - `logstash-dotnet_consumer*`
   - 重点 service：`consumer`、`consumer_hash`
   - 关键类：`AigcAppService`
   - 关键日志：`POST:http://ai-gateway.aihelp.dns:8000/gpt/api/v1/chat/completions`
4. 必须区分以下几类调用，不要把非目标调用当作 gpt-rag 根因：
   - `moduleType=15` 的分类调用
   - `moduleType=27` 的摘要/处理历史调用
   - 真正的 `aIhelpAppType=gpt-rag` 调用
5. 找到真实 gpt-rag 调用后，重放请求必须和日志中的原始请求保持一致：
   - header 使用日志中的 `AIHELP-TEAM-ID`、`AIHELP-APP-ID`，其他必要 header 按日志保留。
   - body 使用日志中的完整原始 body，包括 `appId`、`messages`、`variables`、`toggles`、`intentDescription`、`datasets`、`ticketId`、`language` 等所有字段。
   - 不要自行重组、删减或补默认值；只允许在重放时把 `detail` 从 `false` 改为 `true`。

## FastGPT detail 重放

1. 使用实际日志中的 `AIHELP-APP-ID` 和 `AIHELP-TEAM-ID` 作为请求 header。
2. 请求地址：
   - `https://fastgpt.aihelp.net/api/v1/chat/completions`
3. 不使用 `Authorization: Bearer ...` 作为本流程默认鉴权方式。
4. body 基于实际日志原始请求，只改：
   - `detail: true`
5. 其他字段默认保持日志原值，尤其是：
   - `messages`
   - `appId`
   - `mergeText`
   - `variables`
   - `datasets`
   - `toggles`
6. 保存完整原始响应，用于查看 `responseData` 中的节点明细。

## FastGPT 项目对照

在本机 FastGPT 仓库只读查看 `origin/main` 最新模板，不要为了排查切换用户工作区分支。

常用路径：

- `/Users/bk/Work/AIHelp/FastGPT`
- `projects/app/data/app-template/gpt-rag/v*.json`
- `projects/app/src/pages/api/v1/chat/completions.ts`
- `projects/app/src/pages/api/aihelp/chat/query-item.ts`

重点对照节点：

- 问题重写与实体提取
- 实体召回
- 知识库检索
- 缓存命中
- 回答生成
- 答案润色
- JSON 格式化

判断问题时必须以 `detail=true` 的实际节点输出为准，例如：

- 原始玩家问题是否被重写偏移。
- 检索 query 是否保留玩家真实意图。
- `quoteList` 命中的知识是否与问题匹配。
- 回答节点看到的问题是否已经不同于原始问题。
- 润色节点是否只是改写表达，还是引入新事实。
- 上游 `intentDescription`、`toggles` 是否被流程使用或忽略。

## 桌面证据文件规范

当用户要求“把日志和重放结果存到桌面”时，必须生成两个清晰命名的 `.txt` 文件，不要合并成一个 Markdown 文件。

推荐命名：

1. `bug{bugId}_{ticketShortId或ticketId}_fastgpt原始日志.txt`
2. `bug{bugId}_{ticketShortId或ticketId}_fastgpt_detail_true原始结果.txt`

文件内容要求：

1. `fastgpt原始日志.txt` 只保存实际命中的 FastGPT 原始日志。
2. `fastgpt_detail_true原始结果.txt` 只保存 `detail=true` 重放原始结果。

不要写分析、摘要、排查规则、请求说明、结论、标题或额外表格。

如果日志原文很长，不要手动改写字段含义；只保存原文。敏感 webhook、邮箱、手机号等数据如出现在待测试数据中，先向用户确认再使用。

## 结论输出

最终排查结论仍遵守 `aihelp-bug` 的输出格式：

1. `根因`
2. `证据链`

证据链应包含：

- 客诉库中的玩家原话和 AI 实际回复。
- ELK 中真实 FastGPT gpt-rag 调用。
- `detail=true` 中关键节点输出。
- FastGPT gpt-rag 模板中的对应节点配置或链路。
