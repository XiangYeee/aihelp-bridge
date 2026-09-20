# Server_DotNetCore 发布站点

`Backend/Server_DotNetCore` **只用** `local_backend_dotnetcore_new`。`jenkins_match_job` 常误匹配到别的 job，不要用它的 `best`。

参数：`branch` = 测试分支；`aaa` = 站点（逗号分隔）；`Re_clone` = `no`。`aaa` 是 `PT_CHECKBOX`，MCP 读不到 choices，以本名单为准。

站点名**大小写敏感**，必须用下表原样拼写。用户口语（`jobcenter`、`OpenAPI`、Host 目录）先忽略大小写对表，命中则改回表内写法；对不上就停，列出本表，不要猜、不要自行改大小写。

```
elva
JobCenter
consumer
consumer_hash
consumer_ai
consumer_chatedit
consumer_wxwork
consumer_wecom
ConsumerRedisTicketToMongo
customer
internalapi
mailapi
automatic
fileservice
openapi
wechatopen
sdkapi
crm
mform
portal
app_api
autonotification
lineapi
aihelp_ticket_webserver
dataflow
discord
thirdpartycommon
thirdpartyinternal
etlclickhouse
etlclickhouse_other
logstash_consumer
consumer_actorclient
aihelp_actorhost
```

易错：`jobcenter` → `JobCenter`；`openapi` 保持小写。写错会失败：`Please check project_dir.txt whether this item exists!!!!!`
