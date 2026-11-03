# 小说热榜 — 客户端任务清单

> 本页记录首轮客户端实现与首次部署。追加的起点修复、七猫移除及共享测试任务由[服务端任务 5](../server/tasks.md)统一跟踪，结果见[来源修复记录](../server/source-fix.md)。

基于 design.md，当前任务为 Android、iOS、Desktop 客户端 v0.1.0；已有初始化与 macOS 历史验证保留在末尾。沿用 `quality_gate=off`。实现阶段按技能要求不自动提交；用户随后明确要求“提交下”，本次在 `main` 创建本地提交，不推送或切换分支。本地地址、IDE 和构建文件继续忽略。

## 执行顺序

1. ✅ 已完成 — 模型、URL 与网络契约。
2. ✅ 已完成 — 三端引擎、设置和请求状态机（依赖 1）。
3. ✅ 已完成 — 共享自适应 UI 与平台入口（依赖 2）。
4. ✅ 已完成 — 普通测试、桌面联调与运行文档（依赖 3）。
5. ✅ 已完成 — 追加云接口隔离部署、云端 API 链路与默认地址配置。

## 任务 1：数据与依赖 `✅ 已完成`

- ✅ 1.1 修改 `gradle/libs.versions.toml`、根 `build.gradle.kts`、`composeApp/build.gradle.kts`：Serialization 插件、Ktor 3.3.2 / Coroutines 1.10.2 / Serialization 1.9.0 / Datetime 0.7.1；commonTest、desktopTest 依赖。
- ✅ 1.2 新增 `composeApp/src/commonMain/kotlin/com/novelrank/app/model/Models.kt`：`@Serializable` DTO 字段依 design；`data class Selection(sourceId,categoryId,boardId)`。
- ✅ 1.3 新增 `data/ServiceAddress.kt`、`data/SettingsStore.kt`：`normalizeServiceAddress(input,allowHttp):String`、`isWebUrl(url):Boolean`、`SettingsStore.load/save` 和 `ClientEnvironment`。
- ✅ 1.4 新增 `data/RankRepository.kt`、`data/HttpRankRepository.kt`：`suspend catalog(baseUrl)` / `suspend ranking(baseUrl,selection,refresh)` / `close()`，校验响应身份、错误分类、取消传播与 50 秒预算。

## 任务 2：状态与平台 `✅ 已完成`

- ✅ 2.1 新增 `presentation/RankState.kt`：合法组合选择、当前榜单过滤，`RankUiState`。
- ✅ 2.2 新增 `presentation/RankPresenter.kt`：`start/selectSource/selectCategory/selectBoard/refresh/search/saveAddress/close`；请求取消和身份防护、存储失败、同榜刷新保留旧数据。
- ✅ 2.3 新增 `presentation/Display.kt`：原始业务状态文案、时间格式与来源缺失文案。
- ✅ 2.4 新增各端 `data/PlatformClient.kt`、`data/PlatformSettings.kt`：OkHttp/Darwin/CIO、SharedPreferences/NSUserDefaults/Preferences；expect/actual 网络构造。

## 任务 3：UI 与入口 `✅ 已完成`

- ✅ 3.1 新增 `ui/RankTheme.kt`、`ui/RankScreen.kt`：宽屏侧栏、窄屏横向来源、滚动前十列表；纯状态与回调便于 UI 测试。
- ✅ 3.2 新增 `ui/components/{SourceSelector,RankingFilters,BookCard,StatusPanel,SettingsDialog}.kt`：选择、搜索、状态、来源跳转、服务设置。
- ✅ 3.3 修改 `App.kt`：注入环境、创建 Repository/Presenter、绑定状态、管理 Compose 生命周期及外部链接失败提示。
- ✅ 3.4 修改 Android `MainActivity.kt`、`androidApp/build.gradle.kts`、main Manifest，新增 debug Manifest；注入设置，INTERNET 与仅 Debug 明文许可。
- ✅ 3.5 修改 `MainViewController.kt`、Swift `ContentView.swift`、Info.plist、Xcode project.pbxproj；新增 Info-Debug.plist，Debug ATS/局域网说明和 Release HTTPS 区分。
- ✅ 3.6 修改 desktop `main.kt`：环境注入与窗口尺寸。

## 任务 4：验证与交付 `✅ 已完成`

- ✅ 4.1 新增 commonTest 下 `ServiceAddressTest.kt`、`HttpRankRepositoryTest.kt`、`RankPresenterTest.kt`、`SelectionTest.kt`、`DisplayTest.kt` 及合成测试数据。覆盖 URL、400/422/500、非法响应、取消/快速切换、地址重置、搜索名次、刷新失败保留。
- ✅ 4.2 新增 desktopTest `RankScreenTest.kt`：真实 Compose UI 选择/搜索/状态/设置交互；不依赖网站网络。
- ✅ 4.3 执行 `./gradlew :composeApp:desktopTest --console=plain`；按新增部署需求使用 `:composeApp:run` 连接云端服务联调；检查平台 Manifest/plist 与本地配置排除。临时证据存 `.verification/client/`。
- ✅ 4.4 修改 `README.md`、`server/README.md`，新增 `docs/features/rankings/v0.1.0/client/verification.md`：运行入口、服务地址、Debug/Release 区别、实际验证和未验证平台边界。

无新增后端/API；追加云部署后复用既有 API 链路，10/10 PASS。最终质量验收 SKIPPED（quality_gate=off）；未执行 Harness、覆盖率门禁、双 Agent。Android/iOS 原生构建与安装包按本轮边界不执行，保留准确命令供后续使用。

## 初始化修复：macOS 打包版本 `✅ 已完成`

- ✅ 修改 `composeApp/build.gradle.kts`：为 `nativeDistributions.macOS.packageVersion` 设置 `1.0.0`，修复 `0.1.0` 在项目配置阶段导致的 DMG 版本和构建版本校验失败。
- ✅ 更新 `README.md`：说明 macOS 安装包版本与应用开发版本的区别。
- ✅ 执行 `./gradlew help --offline --console=plain`：`BUILD SUCCESSFUL in 4s`，只验证 Gradle 项目配置，不编译或打包 Android、iOS、Desktop。
- ✅ 在 `verification.md` 记录修复与验证结果。GitHub 交付以对应远程修复提交为准，最终质量门禁仍为 `SKIPPED`。

## macOS 安装包构建 `✅ 已完成`

用户明确要求构建 macOS，目标为当前 Apple Silicon 主机上的 DMG 安装包。

- ✅ 执行 `./gradlew :composeApp:packageDmg --console=plain`：`BUILD SUCCESSFUL in 58s`，10 个任务执行，只构建 Desktop/macOS。
- ✅ DMG 镜像校验通过；启动器为 arm64，安装包版本 1.0.0，签名为 ad-hoc；产物大小和 SHA-256 已记录。
- ✅ 启动打包目录内的 `NovelRank.app`，读取到欢迎页与四站“待接入”状态。
- ✅ 更新 `README.md` 和 `verification.md` 的实际构建状态，补充 Android Studio 的 Gradle 运行配置操作；构建产物与本地日志保持忽略。

## 追加任务 5：云接口部署 `✅ 已完成`

用户要求部署到 `https://47.251.189.239/`，且不能影响其他服务。现有根路径是受 Basic Auth 保护的 IPA Review。

- ✅ 5.1 新增 `server/deploy/{novelrank.service,nginx-location.conf,nginx-limits.conf,novelrank.logrotate,README.md}`：独立 `/opt/novelrank`、venv、系统用户与 systemd 服务，监听 `127.0.0.1:18766`；`/novelrank/` 独立路由，保留旧服务认证/代理。限制新服务 CPU、内存与任务数；独立限流 zone 和日志轮转。
- ✅ 5.2 上传仅服务源码和依赖，在启动新服务后验证本机 health；备份目标 Nginx 配置，仅新增 include，`nginx -t` 成功后平滑 reload；失败恢复本次 include，禁止重启其他应用。
- ✅ 5.3 在公网 TLS 正常校验下验证 health/catalog/rankings/docs/OpenAPI 与 API 测试链；验证旧根路径仍 401、原服务 PID/活跃状态保持，新增 `docs/features/rankings/v0.1.0/server/deployment.md`。
- ✅ 5.4 三端默认地址改为 HTTPS 云地址，README 添加云接口入口与局域网调试说明。实际 SSH 配置、备份、原始日志存忽略目录，不提交。

## 当前执行结果（2026-11-03）

- `./gradlew :composeApp:desktopTest --console=plain`：最终 26/26 通过，20 项共享逻辑/契约 + 6 项 Compose UI。开发期编译 opt-in 和 URL/测试语义定位问题已修复。
- `./gradlew :composeApp:run --console=plain`：桌面实际读取并显示云端晋江前十，正常退出；可访问性树证据，未取得截图。
- `plutil -lint`、Android Manifest / Debug 覆盖与 iOS ATS 检查通过；Android/iOS 原生构建、安装及运行按本轮边界未执行。
- 云端复用 API 链路：10/10 PASS；公网 health/catalog/docs/OpenAPI 200，原根路径仍 401。番茄/晋江已测组合成功；七猫原站 405、起点 202，保留真实失败状态。
- 原 28 个服务 PID/状态及 Nginx master 未变化，原 HTTPS 配置只有一行新增 include；新服务资源限制和回环监听已核对，日志轮转 dry-run 通过。
- 详情见 [客户端验证](verification.md)、[部署记录](../server/deployment.md)；本地证据、缓存及个人配置继续忽略。按用户后续“提交下”的指令创建本地提交，未推送或切换分支。
- 最终质量验收 **SKIPPED（沿用 quality_gate=off）**；没有运行 Harness、门禁覆盖率或双 Agent。
