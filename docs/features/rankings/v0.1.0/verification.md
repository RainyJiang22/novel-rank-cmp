# 工程初始化验证记录

日期：2026-11-03。范围：Android、iOS、Desktop CMP 工程骨架与项目文档。

## 已执行

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

## 验证边界

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

目标：[RainyJiang22/novel-rank-cmp](https://github.com/RainyJiang22/novel-rank-cmp)。本地已初始化 `main` 分支，远程上传与 description 设置完成后更新交付记录。
