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

- `intl_prerelease` 使用自身预发代码和配置环境，但数据库使用和 `aihelp`相同。
- `cn_prerelease` 使用自身预发代码和配置环境，但数据库使用和 `aihelpcn`相同。

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
