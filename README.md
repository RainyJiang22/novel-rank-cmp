# 小说热榜 · NovelRank

一个基于 **Kotlin Compose Multiplatform（CMP）** 的小说分类热榜项目，目标是在 **Android、iOS 和桌面端** 查询不同小说网站、不同类型的前十热门作品。

首批来源为 **起点中文网、番茄小说、七猫中文网、晋江文学城**。

> 当前阶段：**三端共享客户端与 server v0.1.0 已实现，云端 API 已部署**。客户端支持网站/分类/榜单选择、前十查询、搜索、刷新、原站跳转和服务地址保存。默认连接 `https://47.251.189.239/novelrank`。云端实测番茄、晋江已测组合返回十条；起点访问受限，七猫返回 HTTP 405，界面会显示实际来源状态。

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
| Client HTTP | Ktor 3.3.2；Android OkHttp / iOS Darwin / Desktop CIO |
| Shared state | Coroutines 1.10.2、Serialization 1.9.0、Datetime 0.7.1 |
| Server | Python 3.11+、FastAPI 0.162.0、HTTPX 0.28.1、BeautifulSoup 4.15.0 |

采用固定的已发布版本，不使用动态版本。版本选择参考 [Kotlin Multiplatform 兼容表](https://kotlinlang.org/docs/multiplatform/multiplatform-compatibility-guide.html) 和 [Compose Multiplatform 1.9.3 发布说明](https://github.com/JetBrains/compose-multiplatform/releases/tag/v1.9.3)。

## 目录结构

```text
novel-rank-cmp/
├── androidApp/                   # Android 应用与 Activity
├── composeApp/
│   └── src/
│       ├── commonMain/            # 模型、HTTP、状态管理与共享 UI
│       ├── commonTest/            # 契约、状态、取消与 URL 测试
│       ├── androidMain/           # OkHttp 与 SharedPreferences
│       ├── desktopMain/           # JVM 桌面窗口入口
│       ├── desktopTest/           # Compose UI 自动测试
│       └── iosMain/               # Darwin、NSUserDefaults 与 UIViewController
├── iosApp/                       # SwiftUI 容器与 Xcode 工程
├── gradle/                       # 统一依赖版本与 Wrapper
├── server/                       # FastAPI 服务、四站适配器与普通测试
├── scripts/probe_sources.py       # 有限在线来源探测
├── docs/features/rankings/       # 分析、设计、任务与 API 测试链
├── docs/api/rankings.md          # 稳定接口契约
├── gradlew
└── settings.gradle.kts
```

`androidApp` 依赖 `composeApp`；iOS 嵌入共享 `ComposeApp.framework`；桌面入口运行共享 UI。独立 `server/` 提供聚合 API，三端共享 Repository、请求状态和界面。

## 开始使用

```bash
git clone https://github.com/RainyJiang22/novel-rank-cmp.git
cd novel-rank-cmp
```

准备 JDK 17，并使用支持 Kotlin Multiplatform 的 Android Studio / IntelliJ IDEA。首次 Gradle 同步会下载依赖；SDK、Xcode 签名信息均不入库。

### 聚合服务

已部署的服务可以直接使用，无需先启动本地服务：

- 基础地址：`https://47.251.189.239/novelrank`
- [Swagger 接口文档](https://47.251.189.239/novelrank/docs)
- [健康检查](https://47.251.189.239/novelrank/health) · [网站分类目录](https://47.251.189.239/novelrank/api/v1/catalog)
- [部署与回滚说明](server/deploy/README.md) · [云端验证记录](docs/features/rankings/v0.1.0/server/deployment.md)

部署使用独立 systemd 服务、venv 和 `127.0.0.1:18766`，仅 `/novelrank/` 路径公开；原根路径服务的认证与代理保持原样。新服务限制 CPU、内存和并发。

需要本地调试时，使用 Python 3.11 及以上：

在仓库根目录或 Android Studio 的 Terminal 中运行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r server/requirements-dev.txt
.venv/bin/python -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
```

打开 [Swagger 接口文档](http://127.0.0.1:8000/docs)。服务端不需要执行 Gradle 构建。

[服务端运行说明](server/README.md) · [API 契约](docs/api/rankings.md) · [实际 API 测试链记录](docs/features/rankings/api/rankings/doc/00_link.md)

### 客户端服务设置

应用右上角「服务设置」可修改并保存地址，也可恢复默认云地址。分类和榜单来自服务目录；搜索只匹配当前前十的书名/作者，保留原名次。来源失败、部分数据、缓存及旧快照会分别标记，刷新失败会保留上次结果并提示未更新。

本地调试地址：

| 环境 | 服务地址 |
| --- | --- |
| 桌面、iOS 模拟器 | `http://127.0.0.1:8000` |
| Android 官方模拟器 | `http://10.0.2.2:8000` |
| Android / iOS 真机 | `http://电脑局域网IP:8000`；服务显式监听 `0.0.0.0`，设备同网段 |

Android/iOS 仅 Debug 允许 HTTP；Release 要求 HTTPS。桌面支持本地 HTTP 调试。只保存服务地址，不保存密码或 Token；拒绝包含凭据、查询参数、片段和相对路径的地址。

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

在 **macOS 上的 Android Studio** 中构建 DMG：

1. 打开仓库根目录并完成 Gradle Sync，Gradle JDK 选择 17。
2. 进入 **Run → Edit Configurations… → + → Gradle**。
3. 名称填写 `Build macOS DMG`，Gradle project 选择仓库根目录，Tasks / Run 字段填写 `:composeApp:packageDmg`。
4. 点击 **Apply → Run**，以后可从顶部运行配置列表直接选择该配置打包。

也可以在 IDE 底部 **Terminal** 中执行：

```bash
./gradlew :composeApp:packageDmg
```

DMG 输出：`composeApp/build/compose/binaries/main/dmg/NovelRank-1.0.0.dmg`。

仅运行桌面程序时使用 `:composeApp:run`。任务说明见 [Compose 官方打包文档](https://kotlinlang.org/docs/multiplatform/compose-native-distribution.html)，运行配置字段见 [Gradle Run Configuration 文档](https://www.jetbrains.com/help/idea/run-debug-gradle.html)。

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

已验证工程文件、版本目录、XML/plist、Xcode 工程结构和 Gradle Wrapper 校验和，并通过 `./gradlew help --offline --console=plain` 的项目配置检查。

初始化阶段曾在 Apple Silicon 主机完成 DMG 构建与欢迎页启动验证，该旧安装包不包含本次客户端改动。本轮没有重新打包、发布签名或公证。

本轮 `./gradlew :composeApp:desktopTest --console=plain` 通过 **26 项测试**（20 项共享逻辑/契约、6 项 Compose UI）。`./gradlew :composeApp:run --console=plain` 已运行桌面客户端，并从云端读取、展示晋江前十。Android、iOS 尚未原生编译、安装或启动验证；共享 JVM 测试与 plist 检查不能代替这两端验证。

服务端实现阶段已通过 81 项普通测试；本轮云端 **10/10 API 链路通过**，HTTPS 验证正常。云端番茄、晋江已测组合返回十条，起点为 `blocked`，七猫为 `unavailable`（原站 HTTP 405）；此前本地七猫成功不能当作云端可用性保证。未逐一在线验证所有分类。

精确记录见 [当前客户端验证](docs/features/rankings/v0.1.0/client/verification.md)、[云部署记录](docs/features/rankings/v0.1.0/server/deployment.md)、[初始化历史](docs/features/rankings/v0.1.0/verification.md) 与 [服务端实现验证](docs/features/rankings/v0.1.0/server/verification.md)。最终质量验收为 `SKIPPED`（`quality_gate=off`）。

## 后续开发

- [x] 定义网站、分类、榜单及作品元数据契约。
- [x] 实现四站独立来源适配器与可用性状态（起点当前受限）。
- [x] 实现带缓存的聚合服务、普通测试及 API 链路测试。
- [x] 实现三端共享榜单查询、刷新、筛选和来源跳转。
- [x] 客户端业务/UI 测试与桌面云端联调。
- [x] 独立部署云端 API，保留原有服务配置并核对运行状态。
- [ ] Android、iOS 原生构建与设备运行验证。

规划资料：

- [需求分析](docs/features/rankings/v0.1.0/analysis.md)
- [客户端设计](docs/features/rankings/v0.1.0/client/design.md) · [客户端任务](docs/features/rankings/v0.1.0/client/tasks.md)
- [服务端设计](docs/features/rankings/v0.1.0/server/design.md) · [服务端任务](docs/features/rankings/v0.1.0/server/tasks.md)

## 数据来源原则

以各网站公开页面和实际可用接口为准，保存原始榜单口径与来源。只获取必要的公开作品元数据；访问受限、页面变化或数据不足时明确展示状态。网站目录代表支持的查询范围，**不代表所有来源和分类当前都可用**。
