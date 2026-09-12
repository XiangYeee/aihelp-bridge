# AIHelp 工具使用方法

## 需要工作流指导时，读取对应技能

- `aihelp-bug`：用于 bug 排查、根因分析、异常链路核查、证据闭环与排障结论输出。
- `aihelp-ship`：用于测试发版（test 分支 + localjenkins）与正式上线通知（禅道 + develop MR + 群文案）。本包不含 `aihelp-commit`；发版与构建走 ship，不要找 commit。

## MCP使用方法
- `aihelp-guide` 先做业务环境标准化，再按目标 MCP 工具要求映射成工具环境参数。
- 禁止把业务环境字符串直接原样传给 MCP；必须先完成工具环境映射。
- 同一个业务环境在不同 MCP 中，`env`、`group`、`apollo_url` 可能不同，必须分别确认。

### aihelp-elk MCP
- 查询运行日志时，使用 `aihelp-elk` MCP。
- 使用`aihelp-elk` MCP 必须确认好问题时间，按照时间区间搜索，避免返回大量噪音日志。

> #### Service -> Index 对应表
>
> 找不到对应索引时自行推断。
>
> `customer`, `customer_crm` -> `logstash_dotnet_customer`
> 
> `automatic` -> `logstash-dotnet_automatic`
> 
> `vk`, `mailapi`, `mform`, `aihelp_ticket_webserver`, `internalapi`, `applets`, `facebook`, `facebookfeed`, `twitter`, `wechatopen`, `instagram`, `lineapi`, `whatsapp`, `thirdpartycommon`, `thirdpartyinternal`, `openapi` -> `logstash-dotnet_web_ticket`
> 
> `chat_refresh`, `elvaapi_chat`, `elvaapi_default`, `taskcenter`, `taskcenteropenapi`, `app_api` -> `logstash-dotnet_web_console`
> 
> `dataflow`, `refresh`, `dialogflow`, `fileservice`, `operation`, `crm`, `portal`, `stripewebhook` -> `logstash-dotnet_web_other`
> 
> `consumer`, `consumer_chatedit`, `consumerredistickettomongo`, `consumer_wxwork`, `consumer_ai`, `consumer_thirdparty` -> `logstash-dotnet_consumer`
> 
> `autonotification`, `jobcenter`, `etlclickhouse_other`, `etlclickhouse`, `taskcenter_consumer` -> `logstash-dotnet_consumer_other`
> 
> `logstash_consumer`, `webhookpush`, `discord_webhook`, `discord_client` -> `logstash-dotnet_consumer_edge`

### aihelp-db MCP
- 做数据库查询时，使用 `aihelp-db` MCP；
- 使用 `test` 配置的环境，如果任务依赖数据库连接信息，直接通过项目`test`环境配置调用`aihelp-apollo mcp`获取配置。
- 非 `test` 配置的环境中的数据库 Apollo 值通常是环境内 DNS 或内网地址，默认当前机器不可连通，需要使用`aihelp-account mcp`获取数据库连接地址。

> `aihelp_ticket_stats_sharding`分表在`mariadb_slave`库。
>
> `bs_ticket`分表在`mysql_rpa_slave`/`mysql`库

### aihelp-account MCP
- 查询环境账号或凭据时，使用 `aihelp-account` MCP。
- 如果读取出来的账号是`姓名全拼`，密码是` 同wiki密码`，就读取环境变量`AGENT_AIHELP_BASIC_USER`和`AGENT_AIHELP_BASIC_PASS`。

> `test` -> group: `local_account`
> `aihelp` -> group: `aihelp_account`
> `intl_prerelease` -> group: `aihelp_account`
> `aihelpcn` -> group: `aihelpcn_account`
> `cn_prerelease` -> group: `aihelpcn_account`
> `aviagame` -> group: `new_aviagame_account`
> `bilibili` -> group: `blibili_account`
> `ml` -> group: `ml_aliyun_account`
> `aosu` -> group: `aosu_account`

#### ilocalize / go2global 账号规则

- ilocalize 是独立于 AIHelp 的项目体系，不使用上面的 AIHelp 环境账号组映射。
- ilocalize 国际环境相关的项目信息在 `ilocalize_account` 账号组下，不在 `aihelp_account`。
- ilocalize 只有 `local` 和 `国际` 两个环境；查询 ilocalize/go2global 的账号、项目、数据库、MongoDB、Consul 或其他环境信息时，优先从 `ilocalize_account` 查对应项，不要套用 AIHelp 国际环境账号组。

### aihelp-apollo MCP
- 查询 Apollo 配置时，使用 `aihelp-apollo` MCP。

> `test` -> `apollo_url`: 项目 `test` 配置中的 Apollo Portal；`env`: `test`
> `aihelp` -> `apollo_url`: `https://config.aihelp.net`；`env`: `pro`
> `intl_prerelease` -> `apollo_url`: `https://config.aihelp.net`；`env`: `uat`
> `aihelpcn` -> `apollo_url`: `https://config.aihelpcn.net`；`env`: `pro`
> `cn_prerelease` -> `apollo_url`: `https://config.aihelpcn.net`；`env`: `uat`
> `aviagame` ->`apollo_url`: `aihelp-account`MCP获取； `env`: `pro` 
> `bilibili` -> `apollo_url`: `aihelp-account`MCP获取；`env`: `pro`
> `ml` -> `apollo_url`: `aihelp-account`MCP获取；`env`: `pro`
> `aosu` -> `apollo_url`: `aihelp-account`MCP获取；`env`: `pro`

### aihelp-zentao MCP

- 查询禅道内容时，直接使用 `aihelp-zentao` MCP。
- 禅道需求有钉钉文档时，使用 `chrome-devtools` MCP 复用当前浏览器登录态获取文档内容。

### aihelp-gitlab MCP

- 查询 GitLab 仓库、分支、MR 或流水线时，使用 `aihelp-gitlab` MCP。

### aihelp-jenkins MCP

- 测试发版、触发 localjenkins 构建时，转到 `aihelp-ship`，不要在 guide 里直接拼 job 名。
- 测试发版使用的 Jenkins 由 `aihelp-jenkins` MCP 对接（公司内网 Jenkins）。

### aihelp-wiki MCP

- 查询 wiki 时，使用 `aihelp-wiki` MCP。

### jumpserver MCP

- 跳板机资产、执行或文件操作时，使用 `jumpserver` MCP。

### aihelp-langfuse MCP

- 查询 LLM 链路、trace 或 score 时，使用 `aihelp-langfuse` MCP。

### zabbix-mcp

- 查询监控主机、item、trigger、history 时，使用 `zabbix-mcp` MCP。
