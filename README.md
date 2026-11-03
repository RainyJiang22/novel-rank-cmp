# 小说热榜 · NovelRank

一个基于 **Kotlin Compose Multiplatform（CMP）** 的小说分类热榜项目，目标是在 **Android、iOS 和桌面端** 查询不同小说网站、不同类型的前十热门作品。

首批计划覆盖 **起点中文网、番茄小说、七猫中文网、晋江文学城**。

> 当前阶段：工程初始化。已提供三端入口、共享欢迎页面、Gradle Wrapper 和功能规划文档；真实榜单与聚合服务尚未实现。页面中的网站均标记为“待接入”，没有模拟排名。

## 项目目标

- 按网站、小说分类、榜单类型查看前十作品。
- 展示书名、作者、原始名次、热度口径、来源链接与采集时间。
- 明确区分实时获取、缓存、部分数据、来源受限和获取失败。
- 保留各站自己的分类与排名规则，不将不同口径混排。

## 技术栈

| 项目 | 版本 / 说明 |
| --- | --- |
| Kotlin | 2.2.21 |
| Compose Multiplatform | 1.9.3 |
| Material 3 | 1.9.0 |
| Gradle Wrapper | 8.14.3 |
| Android Gradle Plugin | 8.11.1 |
| JDK | 17 |
| Android | minSdk 26，compileSdk / targetSdk 36 |
| iOS | 最低 iOS 15，支持 arm64 真机、Apple Silicon / Intel 模拟器 |
| Desktop | JVM，桌面入口；安装包需在对应操作系统上构建 |

采用固定的已发布版本，不使用动态版本。版本选择参考 [Kotlin Multiplatform 兼容表](https://kotlinlang.org/docs/multiplatform/multiplatform-compatibility-guide.html) 和 [Compose Multiplatform 1.9.3 发布说明](https://github.com/JetBrains/compose-multiplatform/releases/tag/v1.9.3)。

## 目录结构

```text
novel-rank-cmp/
├── androidApp/                   # Android 应用与 Activity
├── composeApp/
│   └── src/
│       ├── commonMain/            # 三端共享 UI
│       ├── desktopMain/           # JVM 桌面窗口入口
│       └── iosMain/               # Compose UIViewController 入口
├── iosApp/                       # SwiftUI 容器与 Xcode 工程
├── gradle/                       # 统一依赖版本与 Wrapper
├── docs/features/rankings/       # 需求、客户端/服务端设计和后续任务
├── gradlew
└── settings.gradle.kts
```

`androidApp` 依赖 `composeApp`；iOS 嵌入共享 `ComposeApp.framework`；桌面入口运行共享 UI。聚合服务是后续规划，当前没有 `server/` 运行模块。

## 开始使用

```bash
git clone https://github.com/RainyJiang22/novel-rank-cmp.git
cd novel-rank-cmp
```

准备 JDK 17，并使用支持 Kotlin Multiplatform 的 Android Studio / IntelliJ IDEA。首次 Gradle 同步会下载依赖；SDK、Xcode 签名信息均不入库。

### Android

1. 用 Android Studio 打开仓库根目录，Gradle JDK 选择 17。
2. 安装 Android SDK Platform 36；由 IDE 生成 `local.properties`，或设置自己的 `ANDROID_HOME`。
3. 选择 `androidApp`，运行到 API 26 及以上设备或模拟器。

仅构建 Debug APK：

```bash
./gradlew :androidApp:assembleDebug
```

### 桌面端

```bash
./gradlew :composeApp:run
```

打包当前系统的桌面安装包：

```bash
./gradlew :composeApp:packageDistributionForCurrentOS
```

macOS / Windows / Linux 安装包分别在对应主机上构建。

macOS 安装包版本单独设为 `1.0.0`，满足 [DMG 的主版本号必须大于 0 的校验规则](https://github.com/JetBrains/compose-multiplatform/blob/v1.9.3/gradle-plugins/compose/src/main/kotlin/org/jetbrains/compose/desktop/application/internal/validation/validatePackageVersions.kt)；应用开发版本及其他桌面包仍使用 `0.1.0`。

### iOS

1. 在 macOS 上安装 Xcode 并完成首次启动配置，确保可使用 JDK 17。
2. 打开 `iosApp/iosApp.xcodeproj`，选择共享 Scheme `iosApp`。
3. 选择 iOS 模拟器运行。工程构建阶段会调用 `:composeApp:embedAndSignAppleFrameworkForXcode`。
4. 真机运行时，按下方约定配置自己的 Team 与 Bundle Identifier，再在 Xcode 的 **Signing & Capabilities** 中检查签名状态。

不依赖 CocoaPods。源码不包含签名证书或固定开发团队。

### 本地配置约定

SDK 路径写入 `local.properties`。iOS 的共享 `iosApp/Configuration/Config.xcconfig` 会自动加载可选的本地 `Config.local.xcconfig`；真机签名可以写入后者：

```xcconfig
DEVELOPMENT_TEAM = YOUR_TEAM_ID
PRODUCT_BUNDLE_IDENTIFIER = com.yourname.novelrank
```

该本地文件、IDE 用户设置、签名资料、账号凭据、`.env` 和构建缓存均已加入 `.gitignore`。仓库保留用于协作的 Gradle 版本、Wrapper、Xcode 工程和共享 Scheme。

## 验证状态

已验证工程文件、版本目录、XML/plist、Xcode 工程结构和 Gradle Wrapper 校验和，并通过 `./gradlew help --offline --console=plain` 的项目配置检查。**尚未执行应用编译、三端启动或设备验证**，不能将配置检查视为应用构建通过。

精确检查记录见 [初始化验证记录](docs/features/rankings/v0.1.0/verification.md)。初始化阶段尚无业务接口；最终质量验收为 `SKIPPED`（`quality_gate=off`）。

## 后续开发

- [ ] 定义网站、分类、榜单及作品元数据契约。
- [ ] 实现四站独立来源适配器与可用性状态。
- [ ] 实现带缓存的聚合服务及 API 链路测试。
- [ ] 实现三端共享榜单查询、刷新、筛选和来源跳转。
- [ ] 补充业务单元测试、接口契约测试和三端运行验证。

规划资料：

- [需求分析](docs/features/rankings/v0.1.0/analysis.md)
- [客户端设计](docs/features/rankings/v0.1.0/client/design.md) · [客户端任务](docs/features/rankings/v0.1.0/client/tasks.md)
- [服务端设计](docs/features/rankings/v0.1.0/server/design.md) · [服务端任务](docs/features/rankings/v0.1.0/server/tasks.md)

## 数据来源原则

以各网站公开页面和实际可用接口为准，保存原始榜单口径与来源。只规划必要的公开作品元数据；访问受限、页面变化或数据不足时明确展示状态。网站列表代表接入计划，**不代表四站已接通**。
