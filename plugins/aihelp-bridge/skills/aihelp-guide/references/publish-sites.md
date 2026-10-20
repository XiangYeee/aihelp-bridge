# 发布站点

给出要发布的站点之前，必须用 `aihelp-wiki` 读取 page_id `12908998`：

https://wiki.aihelp.net/pages/viewpage.action?pageId=12908998

页面标题是「后端所有服务列表」。列是「项目工程 / 站点 / 更新须知」。

- 先确定改动落在哪个项目工程，再只列该工程下真正跑到这段代码的站点。不要用仓库名、Host 目录名，或「Consumer」这种合称代替站点。
- 同一工程下的站点分开发布。`Server_DotNetCore` 的 consumer 不是一个站点。回答前以该页为准核对拆分；代码里 `AIHelp.Consumer` 的 `server` 参数要对应到页上的站点，例如 `server == "ai"` 是 `consumer_ai`，`server == "hash"` 是 `consumer_hash`。
- 该行「更新须知」有内容时，发布说明里要带上。
- `Server_DotNetCore` 走 Jenkins 测试发版时，`aaa` 参数的大小写以 `aihelp-ship` 的 [dotnetcore-sites.md](../../aihelp-ship/references/dotnetcore-sites.md) 为准。wiki 上的写法可能和 Jenkins 勾选框不一致。
- 不要把整张表抄进本技能。页面会更新，每次回答前重新读。
