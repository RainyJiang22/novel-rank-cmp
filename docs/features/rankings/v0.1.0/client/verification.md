# 客户端 v0.1.0 验证记录

日期：2026-11-03；基线：`main` / `6a5927a`。实现阶段验证完成后，用户追加“提交下”，按授权将本轮实现和文档提交到本地 `main`，未推送或切换分支。沿用 `quality_gate=off`。

## 实现

- commonMain：服务 DTO、Ktor Repository、地址校验、StateFlow Presenter、自适应页面和设置对话框。
- 网站/分类/榜单来自目录；请求取消与身份检查防止旧响应覆盖新选择；搜索只过滤当前前十并保留原名次。
- 明确显示来源受限、不可用、部分数据、缓存和旧快照；同榜刷新失败保留旧结果并标记未更新。
- Android：OkHttp、SharedPreferences、INTERNET、仅 Debug 明文许可；iOS：Darwin、NSUserDefaults、Debug/Release plist；Desktop：CIO、JVM Preferences。
- 三端默认 `https://47.251.189.239/novelrank`，允许保存自定义服务地址；Android/iOS Release 只接受 HTTPS。

## 普通自动测试

执行：

```bash
./gradlew :composeApp:desktopTest --console=plain
```

最终结果：**BUILD SUCCESSFUL in 33s，26 tests，0 failures**。

| 测试 | 数量 | 证明范围 |
| --- | ---: | --- |
| ServiceAddressTest | 3 | 云端路径前缀、IPv6、本地 HTTP、空主机/端口 0/相对路径/凭据拒绝、Release HTTPS |
| SelectionTest | 2 | 默认合法组合与网站/分类/榜单联动 |
| DisplayTest | 2 | 来源状态与本地时区展示 |
| HttpRankRepositoryTest | 6 | JSON 与请求参数、来源状态、身份与名次、非法目录、HTTP 错误、重定向、取消与网络错误 |
| RankPresenterTest | 7 | 快速切换、旧响应、改地址、存储失败、搜索、刷新失败保留、重试、关闭取消 |
| RankScreenTest | 6 | 宽屏来源选择、390×844 窄屏搜索与原名次、来源受限、刷新失败提示、分类菜单、设置校验 |

测试使用合成数据、MockEngine 和协程测试调度，不请求真实网站。共享测试在 JVM 执行；不能推断 Android / Kotlin Native 引擎和存储已运行通过。

正常开发修复记录：首次编译补充 `kotlin.time.ExperimentalTime` opt-in；两次测试失败定位到 Ktor 对缺少主机/端口 0 的默认处理，以及设置错误文案的合并语义节点。分别增加原始地址校验、使用未合并节点断言，最终全部通过。剩余两条 Datetime 旧属性弃用警告不影响本轮结果；未运行门禁重试流程。

本地报告：`composeApp/build/reports/tests/desktopTest/index.html`；日志 `.verification/client/desktop-test.log`，均被忽略。

## 桌面云端联调

执行 `./gradlew :composeApp:run --console=plain`，正常启动并退出，**BUILD SUCCESSFUL in 2m 27s**。通过 macOS 可访问性树读取到实际桌面窗口：

- 四站分类数量：起点 14、番茄 37、七猫 19、晋江 18。
- 晋江「衍生言情 / 分类收入金榜」、已获取 10 部作品、采集时间、来源更新时间缺失提示。
- 前两项显示「被小蜘蛛听见心声后」「［娱乐圈］顶流巨星是我十年网友」，保留 01/02 名次、作者与原站入口。

以上证明实际 JVM 客户端成功读取并呈现云端数据；交互逻辑由上述自动 UI 测试验证。本机 UI 工具未识别 Java 应用，系统截图捕获也未成功，因此没有桌面截图或像素级视觉验收证据。没有将旧欢迎页 DMG 当作本次运行结果。

云端接口测试及其他服务隔离结果见 [部署记录](../server/deployment.md)。

## 平台配置与边界

- `plutil -lint`：Info.plist、Info-Debug.plist、project.pbxproj 全部 OK；Debug 使用独立 ATS 放行，Release 不包含该放行。
- Android Manifest XML 与 debug 覆盖、INTERNET 声明检查；平台入口与引擎依赖按 source set 分开。
- `git diff --check` 通过；`.verification/`、`.venv/`、local.properties、本地 xcconfig 和构建产物由 `.gitignore` 排除。
- 未执行 Android assemble、iOS/Xcode 构建、真机/模拟器安装、Windows/Linux 运行、DMG 重打包、发布签名或公证。
- 未逐一在线验证所有分类；七猫和起点云端来源受限，详见部署记录。

最终质量验收：**SKIPPED（沿用 quality_gate=off）**。未执行 Harness、覆盖率门禁、测试/架构双 Agent；不宣称上述检查或覆盖率通过。
