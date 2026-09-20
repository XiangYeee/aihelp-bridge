# AIHelp 环境规则

## 环境名称标准化

> `local`、`测试` 统一视为 `test`
> `aihelp`、`国际` 统一视为 `aihelp`
> `aihelpcn`、`国内` 统一视为 `aihelpcn`
> `intl_prerelease`、`国际预发`、`预发国际` 统一视为 `intl_prerelease`
> `cn_prerelease`、`国内预发`、`预发国内` 统一视为 `cn_prerelease`
> `aviagame`、`欢忻`、`欢欣` 统一视为 `aviagame`
> `bilibili`、`b站` 统一视为 `bilibili`
> `ml`、`ML私有化` 统一视为 `ml`
> `aosu`、`七人科技` 统一视为 `aosu`

## 默认环境判定

- 禅道 的 bug 或 story 未明确给环境时，默认业务环境按 `aihelp` 处理。
- 口述缺陷、本地调试未明确给环境时，默认按 `test` 处理。
- 用户说“测试接口”但没有明确说 `localhost` 时，默认按 `test` 处理。

## 预发环境

- `intl_prerelease` 配置走自身预发环境，数据库与 `aihelp` 相同；**代码对照与 `aihelp` 相同**（见下方）。
- `cn_prerelease` 配置走自身预发环境，数据库与 `aihelpcn` 相同；**代码对照与 `aihelpcn` 相同**（见下方）。

## 代码对照分支

排查或对照代码时，必须读该环境对应 ref 的远端内容，禁止用当前工作区 `feature/*` / `fix/*` 冒充环境代码。只有 `localhost` 联调，或用户明确说看当前分支 / 未上测试的 MR 时，才用工作区或用户指定的源分支，并在结论里标明。

不要为排查 `git checkout` 切走用户正在开发的分支。有本地仓时：`git fetch` 后 `git show <ref>:<path>` / `git grep <pattern> <ref>`。无本地仓时用 GitLab `/-/blob/<ref>/...`。

用户已给出分支或 tag → 用用户的。否则按环境解析：

- `test`：该仓库在 `aihelp-jenkins`（localjenkins）**最近一次成功构建**的 `branch`。job 解析同 `aihelp-ship` 的 [jenkins-jobs.md](../../aihelp-ship/references/jenkins-jobs.md)。parametrized 用 `jenkins_get_job_builds` 的 `lastSuccessfulBuild`，再 `jenkins_get_build` 读 `parameters.branch`；multibranch 用最近成功的 `{parent}/{branch}` 中的 branch。拿不到就停，不要用日历 `test_MMDD` 猜。
- `aihelp`、`aihelpcn`、`intl_prerelease`、`cn_prerelease`：默认 `develop`（仓内没有 `develop` 再用 `gitlab_project_get.default_branch`）。**仅当 develop 上的代码与问题现象明显不符**时，才查发布记录：`gitlab_tags_list`，按 `message` 过滤含「正式」、不含「B站」的 tag，按 `message` 里的日期取最新（如同日多条取列表最前），再对照该 tag 的代码。
- `bilibili`：仓内有 `release_B站` 用它，否则 `release_b`。不符时同样用 tag，`message` 含「B站」。
- `ml`：`release_ml_cn`
- `aviagame`：`release_aviagame`
- `aosu`：`release_aosu`

发布 tag 示例：`v5.7.7.0920`，`message` 为 `2026-9-20  正式`；B 站为 `v5.7.0.0920-b`，`message` 含 `B站`。

## ilocalize / go2global 环境规则

- ilocalize 是独立于 AIHelp 的项目体系，不套用 AIHelp 的 `test`、`aihelp`、`aihelpcn`、预发或私有化环境映射。
- `ilocalize`、`go2global`、`go2global-api` 只表示 ilocalize/go2global 项目体系，不归一化为 AIHelp 环境。
- ilocalize 只有 `local` 和 `国际` 两个环境。
- ilocalize 语境下的 `local` 表示 ilocalize local 环境；`国际` 表示 ilocalize 国际生产环境。
- 查询 ilocalize/go2global 环境、账号、项目、数据库、MongoDB、Consul 或配置时，按 ilocalize 独立规则处理，不要套用 AIHelp 国际环境规则。

## local、test与 localhost（本地） 的区别

- 在 AIHelp 语境中，`local` 表示测试环境，不表示本机启动的服务。
- AIHelp 各环境 WebElva/console 后台页面基地址使用对应域名下的 `/console/`，后台接口调用路径使用 `/console/api/...`，例如 `https://local.aihelp.net/console/api/store/googlereview/reviewsstatistics`；不要直接按根路径、裸 `/api` 或 `/console/<controller>` 路径猜测。
- 只有用户明确提到 `localhost` 接口、本地服务启动，或已经给出本地地址时，才按 `localhost` 处理。
- 本机启动的 `localhost` WebElva 服务例外，按实际本地服务地址调用，例如 `https://localhost:<port>/`，不要额外拼 `/console/`。
- 本机启动的 `localhost` 服务通常仍使用 `local/test` 环境配置；WebElva JWT token 从 `localhost` 登录获取或从对应 `local` 环境登录获取，一般可在两边互用。
- `test` 与 `localhost` 启动场景下，数据库连通通常优先使用项目本地 `test` 配置。
