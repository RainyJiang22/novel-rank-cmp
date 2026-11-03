# 小说热榜 — 客户端任务清单

基于 `design.md`。用户最新要求是先初始化三端项目并上传指定 GitHub，当前只执行 I-1 工程初始化。榜单 UI、网络、数据模型与业务测试留到功能开发阶段。

全局约束：独立仓库；保留原工作区；不执行 Gradle/Xcode 构建；`quality_gate=off`（默认）；最终质量验收 `SKIPPED`。用户明确授权上传，因此允许在新仓库内提交、推送，禁止强制覆盖远程历史。

## 执行顺序

1. ✅ 已完成 — Gradle 与三端启动工程（文件与配置验证）。
2. ✅ 已完成 — 共享初始页面和项目文档（未编译运行）。
3. ✅ 已完成 — 配置验证、提交、GitHub 上传与 description 读回。
4. ⬜ 待处理 — 后续热榜业务开发，不属于本次初始化。

## 任务 1：工程配置 `✅ 已完成`

新增 `settings.gradle.kts`、`build.gradle.kts`、`gradle.properties`、`gradle/libs.versions.toml`、`gradle/wrapper/*`、`gradlew*`。

- ✅ 1.1 固定版本，配置 `include(":androidApp", ":composeApp")`；Wrapper 来自 Gradle 官方并校验 SHA-256。
- ✅ 1.2 新增 `composeApp/build.gradle.kts`：`androidTarget()`、`jvm("desktop")`、`iosArm64()`、`iosSimulatorArm64()`、`iosX64()`；iOS 输出静态 `ComposeApp` framework。
- ✅ 1.3 新增 `androidApp/build.gradle.kts`、`src/main/AndroidManifest.xml`、`MainActivity.kt`、`res/values/strings.xml`：`ComponentActivity.setContent { App() }`。
- ✅ 1.4 新增 `composeApp/src/desktopMain/kotlin/com/novelrank/app/main.kt`：`fun main() = application { Window { App() } }`。
- ✅ 1.5 新增 `composeApp/src/iosMain/kotlin/com/novelrank/app/MainViewController.kt`、`iosApp/iosApp/{iOSApp.swift,ContentView.swift,Info.plist}`、`iosApp/iosApp.xcodeproj/*`：`ComposeUIViewController { App() }`，SwiftUI 包装，Gradle Embed Framework 构建阶段，签名团队由开发者设置。

## 任务 2：初始页面与说明 `✅ 已完成`

- ✅ 2.1 新增 `composeApp/src/commonMain/kotlin/com/novelrank/app/App.kt`：共享欢迎页面、三端标识、四站规划卡片、明确“尚未接入榜单”。不填充模拟排名。
- ✅ 2.2 新增 `.gitignore`、`.editorconfig`：排除构建产物、IDE、local.properties、签名与本地配置。
- ✅ 2.3 新增 `README.md`：产品目标、当前状态、目录结构、精确运行命令、环境和验证边界、后续路线、官方参考。

## 任务 3：验证与 GitHub 交付 `✅ 已完成`

- ✅ 3.1 验证 TOML、XML/plist、shell 语法、Xcode 项目目标与共享 Scheme、Gradle Wrapper 校验和、`git diff --check`，仅证明工程配置及文件完整性。
- ✅ 3.2 以本地提交推送到 `https://github.com/RainyJiang22/novel-rank-cmp.git`，读取远程分支确认提交一致；设置仓库 description 并读回。远程默认分支为 main，34 个文件与 README blob 已核对一致。
- ✅ 3.3 将验证命令、结果和缺口写入 `verification.md`。

编译验证命令（按用户偏好本轮不执行）：`./gradlew :composeApp:compileKotlinDesktop`、`./gradlew :androidApp:assembleDebug`；iOS 在 Xcode 选择模拟器运行。初始化页面没有业务逻辑，暂不新增镜像实现的单元测试。业务阶段必须补齐有意义的状态、契约与 UI 测试。

## 任务 4：后续业务阶段 `⬜ 待处理`

依赖服务端契约后新增 `model/Models.kt`、`data/RankRepository.kt`、`presentation/RankPresenter.kt`、`ui/components/*` 和各端网络/存储实现；再新增 `commonTest` 覆盖非法选择、取消旧请求、服务失败和搜索。执行 `./gradlew :composeApp:desktopTest` 的权限与范围在该阶段明确。不得将未执行项勾选为通过。
