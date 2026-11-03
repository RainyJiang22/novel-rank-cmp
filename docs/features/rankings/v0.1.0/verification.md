# 工程初始化验证记录

日期：2026-11-03。范围：Android、iOS、Desktop CMP 工程骨架与项目文档。

## 初始化交付时的静态检查

| 检查 | 方法 / 命令 | 结果 |
| --- | --- | --- |
| Gradle Wrapper | 从 Gradle 官方 v8.14.3 获取脚本与 JAR，使用官方 wrapper.jar.sha256 比对 | PASS |
| Gradle 分发包校验 | 将官方 gradle-8.14.3-bin.zip.sha256 写入 distributionSha256Sum | PASS；未下载或执行分发包 |
| Wrapper 脚本 | `sh -n gradlew`，执行位检查，zipfile 验证 JAR 与入口类 | PASS |
| 版本目录 | Python tomllib 解析并核对依赖版本引用 | PASS |
| XML 与 Scheme | Python ElementTree 解析 Android XML、Xcode Scheme | PASS |
| iOS plist / 工程 | `plutil -lint iosApp/iosApp/Info.plist iosApp/iosApp.xcodeproj/project.pbxproj` | PASS |
| Xcode 对象关系 | xcodeproj 读取目标、Swift 文件、Framework 阶段与共享 Scheme | PASS |
| 配置可移植性 | 系统 Framework 使用 SDKROOT；无个人 Team；共享配置加载可选 local.xcconfig | PASS |
| 本地配置排除 | `git check-ignore` 检查 SDK、IDE、签名、账号环境、本地 Xcode 配置与缓存路径 | PASS |
| 待提交内容 | 对暂存文件检测机器绝对路径、SDK 路径、凭据模式；只报告文件名 | PASS |
| 补丁格式 | `git diff --cached --check` | PASS |

Wrapper JAR SHA-256：`7d3a4ac4de1c32b59bc6a4eb8ecb8e612ccd0cf1ae1e99f66902da64df296172`。

Gradle 8.14.3 bin ZIP SHA-256：`bd71102213493060956ec229d946beee57158dbd89d0e62b91bca0fa2c5f3531`。

校验来源：[Wrapper 官方校验和](https://services.gradle.org/distributions/gradle-8.14.3-wrapper.jar.sha256)、[分发包官方校验和](https://services.gradle.org/distributions/gradle-8.14.3-bin.zip.sha256)。

## 初始化交付时的验证边界

按本轮工程初始化范围，不执行 Gradle/Xcode 编译、打包、设备启动和视觉验证。本记录仅证明文件格式、工程引用与交付边界，不证明三端编译运行通过。未运行以下命令：

```bash
./gradlew :composeApp:compileKotlinDesktop
./gradlew :composeApp:run
./gradlew :androidApp:assembleDebug
```

iOS 的后续验证入口为 `iosApp/iosApp.xcodeproj` 的共享 `iosApp` Scheme。

当前无业务逻辑与接口，不新增仅重复欢迎页面实现的测试；后续功能任务已明确要求普通客户端测试、来源解析测试及 API 链路。尚未进行任何全量实时榜单接入验证。

最终质量验收：`SKIPPED`，`quality_gate=off`（工作流默认值）。Harness、覆盖率门禁、测试 Agent 和架构 Agent 均未执行；API 链路本轮不适用。

## GitHub 交付

已上传至 [RainyJiang22/novel-rank-cmp](https://github.com/RainyJiang22/novel-rank-cmp)，默认分支 `main`，沿用已有公开可见性。

- 初始化提交 `8dc85fffd67c`，通过 `git ls-remote origin refs/heads/main` 核对远程一致。
- GitHub tree API 读回的 34 个文件与本地清单一致，README blob SHA 与 `git hash-object README.md` 一致。
- 使用 `gh repo edit --description` 设置后，`gh repo view --json description,defaultBranchRef,visibility,url` 读回确认。
- Description：基于 Kotlin Compose Multiplatform 的小说分类热榜项目，面向 Android、iOS 与桌面端，计划接入起点、番茄、七猫和晋江。
- 未提交 SDK 路径、个人 IDE 配置、签名资料、认证凭据和构建缓存。GitHub 认证由本机凭据管理器处理。

本文件后续状态同步属于文档提交；工程初始化验证对应上述源码提交。完整实时热榜实现仍在后续任务中。

## 配置修复：macOS DMG 版本

初始化后的首次 Gradle 同步暴露了 DMG 版本校验错误：公共 `nativeDistributions.packageVersion = "0.1.0"` 被 macOS 继承，而插件要求 DMG 版本与构建版本的主版本号大于 0。原来的文件格式检查没有覆盖 Gradle 插件配置逻辑。

修复：在 `composeApp/build.gradle.kts` 的 `macOS` 中覆盖 `packageVersion = "1.0.0"`。应用开发版本和其他平台包版本仍为 `0.1.0`。

配置验证命令：

```bash
./gradlew help --offline --console=plain
git diff --check
```

结果：`BUILD SUCCESSFUL in 4s`，仅执行 `:help` 一个任务；补丁格式检查通过。Gradle 已成功配置项目，并通过 DMG 版本与构建版本校验。未执行应用编译、DMG 打包、设备启动或原生测试，最终质量门禁仍为 `SKIPPED`。

## 后续执行：macOS DMG 构建

用户明确要求构建 macOS 后，基于源码提交 `b8483a4e5227`，在 Apple Silicon / JDK 17 上执行：

```bash
./gradlew :composeApp:packageDmg --console=plain
hdiutil verify composeApp/build/compose/binaries/main/dmg/NovelRank-1.0.0.dmg
```

构建结果：`BUILD SUCCESSFUL in 58s`，10 个任务执行，包含 `compileKotlinDesktop`、`createDistributable` 与 `packageDmg`。DMG 校验结果为 `VALID`。

| 项目 | 结果 |
| --- | --- |
| 安装包 | `composeApp/build/compose/binaries/main/dmg/NovelRank-1.0.0.dmg` |
| 应用目录 | `composeApp/build/compose/binaries/main/app/NovelRank.app` |
| 安装包大小 | 67,326,531 bytes（约 67.3 MB） |
| SHA-256 | `1ff123d614b54b6f80579aff580288fa46f0ef2f29032b5841f74697e3f7cdfd` |
| 启动器架构 | Mach-O 64-bit arm64 |
| Bundle ID | `com.novelrank.desktop` |
| Bundle version / build version | 1.0.0 / 1.0.0 |
| 签名 | ad-hoc；未做 Developer ID 发布签名或公证 |
| 打包入口 | 产物 JAR 中存在 `com/novelrank/app/MainKt.class` |
| 启动检查 | 已启动打包目录内的应用，窗口标题“小说热榜 · NovelRank”；欢迎页显示四站“待接入” |
| 本地日志 | `.verification/macos/packageDmg.log`（已忽略） |

本次证明 macOS arm64 编译、打包、镜像完整性及欢迎页启动。不代表 Android/iOS 构建通过，也没有执行真实热榜业务、跨系统安装或完整 UI 测试。构建产物和日志均未纳入 Git；最终质量门禁保持 `SKIPPED`。
