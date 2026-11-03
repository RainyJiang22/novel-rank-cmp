# 起点修复与七猫移除记录

日期：2026-11-03。基线：`main` / `a2a86e9`，本轮代码尚未提交或推送。用户明确要求移除七猫；当前来源为起点、番茄、晋江。云端已更新，共 120 种合法查询组合。

## 改动与原因

- 七猫：删除目录、适配器注册、解析器、请求域名和在线探测项；两个旧请求组合实测返回 HTTP 400 / `INVALID_SELECTION`。离线测试确认非法来源不会访问上游。客户端从目录加载网站，重新打开应用后只显示三个来源；设置文案和测试数据同步调整。
- 起点：旧 PC 地址返回 HTTP 202 和探测脚本，官方移动端普通 GET 可直接读取榜单。改为解析 `m.qidian.com` 的公开 SSR JSON，不执行页面脚本。保留现有 14 类和月票/畅销两个榜单。
- 解析验证：校验网站/频段、路由、分类 ID/名称、当前月份（UTC+8）、第一页、作品 ID 和原始名次；异常结构返回 `parse_error`。SSR 的非文本标记不会显示成书名，缺失标题/作者保留位置并标记 `partial`。
- 指标：月票保留原单位；畅销榜没有公开销售数值，`metric=null`，不因此标为缺失数据。
- README、稳定 API 契约和当前设计已更新；初版验证、部署和接口快照保留为历史记录。

来源依据：[官方玄幻月票榜](https://m.qidian.com/rank/yuepiao/catid21/)、[官方玄幻畅销榜](https://m.qidian.com/rank/hotsales/catid21/)。SSR 特殊值按[序列化器的类型定义](https://github.com/brillout/json-serializer/blob/main/src/types.ts)处理。

七猫此前云端 405 页面与 WAF 拦截特征匹配，具体触发规则需对方日志才能确定，参见[阿里云 WAF 405 排查说明](https://help.aliyun.com/zh/waf/how-to-troubleshoot-405-errors)。用户随后决定移除，因此本轮不继续请求七猫或办理放行。

## 普通测试

```bash
.venv/bin/python -m pytest -c server/pyproject.toml server/tests -q
./gradlew :composeApp:desktopTest --console=plain
```

- 服务端：**114 passed**，1 条现有 Starlette/httpx 弃用提示。覆盖三站目录、120 种组合、已移除来源、起点合法榜单及错误分类/月份/页码/名次/JSON/元数据，并保留缓存、HTTP 边界与 API 测试。
- 客户端：**26 passed**，20 项共享逻辑/契约与 6 项 Compose UI，0 失败/错误/跳过。Gradle 成功；已有日期字段弃用提示未在本轮修改。
- 当前捕获的官方页面筛选项与全部 14 个已支持起点分类 ID/名称一致。真实页面解析覆盖全站/玄幻的月票和畅销榜；没有逐一在线请求全部分类。
- `git diff --check` 通过。用户原有 `ServiceAddress.kt` 格式改动的 SHA-256 与本轮开始时一致。

## 云端更新与隔离

基础地址：`https://47.251.189.239/novelrank`。

| 项目 | 结果 |
| --- | --- |
| 当前 release | `/opt/novelrank/releases/server-v0.1.0-source-fix-20261103T080339Z` |
| 上一 release | `/opt/novelrank/releases/server-v0.1.0-6a5927a`，保留用于回滚 |
| 切换时间 | 2026-11-03 08:06:04 UTC |
| 上传范围 | 11 个 `server/app/` Python 源文件、`server/requirements.txt` 和来源清单 |
| 归档 SHA-256 | `dcb7cf06fb7b49b708f44fe417a0a54ecfeaa98dd17ea46a75505e13dc8c4e39` |
| 依赖 | 与上一版本完全相同，复用 NovelRank 独立 venv；`pip check` 通过 |
| 预检查 | 受资源限制的临时服务监听 `127.0.0.1:18767`；health、三站目录、七猫 400、起点玄幻月票十条通过后停止 |
| 正式服务 | 原子切换 `current` 软链，只重启 `novelrank.service`；PID `2325425` → `2328443` |
| 资源限制 | 继续使用 256 MiB 内存、50% 单核 CPU、64 tasks、单 worker 和原有并发/请求间隔 |
| 其他服务 | 更新前后其余 **28 个运行服务**的 MainPID、ActiveState、SubState 均相同 |
| Nginx | master PID `106529` 未变，未 reload/restart；目标站点、NovelRank 路由与限流配置哈希均未变 |
| 其他配置 | NovelRank systemd unit、日志轮转配置哈希未变；原 HTTPS 根路径仍返回 401 |
| 回滚 | 本轮未触发；保留上一 release，只需切回软链并重启 NovelRank，见[部署说明](../../../../../server/deploy/README.md) |

服务器逐文件验证清单哈希，部署后再次核对本地运行源码与上传归档一致。release 来自当前未提交工作区，不将它标成已有 Git 提交。

## 公网 API 验证

正常校验 HTTPS 证书，没有使用 `-k`。health/catalog/docs/OpenAPI 均返回 200；目录只有 `qidian`、`fanqie`、`jinjiang`。

```bash
.venv/bin/python docs/features/rankings/api/rankings/request/rankings.py \
  --base-url https://47.251.189.239/novelrank \
  --source qidian --category 21 --board yuepiao \
  --docs-dir .verification/source-fix/cloud-api-doc \
  --evidence-label '云端 HTTPS / 三站目录与起点官方移动榜单'
```

**10/10 PASS**：健康、三站目录、起点真实前十、缓存、刷新冷却、400/422 和跨站状态。未启用 `--allow-upstream-failure`。脚本生成 11 份包含当时真实响应的中文接口文档，保存在本地忽略目录。

有限实测结果如下；仅代表本次观察，不能保证上游持续可用：

| 网站 / 分类 / 榜单 | 结果 | 元数据与指标 |
| --- | --- | --- |
| 起点 / 全部 / 月票 | ok，10 条 | 标题、作者完整，原始月票数值 |
| 起点 / 全部 / 畅销 | ok，10 条 | 标题、作者完整，销售数值 null |
| 起点 / 玄幻 / 月票 | ok，10 条 | 标题、作者完整，原始月票数值 |
| 起点 / 玄幻 / 畅销 | ok，10 条 | 标题、作者完整，销售数值 null |
| 番茄 / 都市日常 / 阅读 | partial，10 条 | 第 7 名标题/作者未取得，保留名次和原站链接；其余 9 条元数据完整 |
| 晋江 / 古代言情 / 收入金榜 | ok，10 条 | 标题、作者完整，金额未公开 |
| 已移除七猫 / boy / hot-daily | HTTP 400 | INVALID_SELECTION |
| 已移除七猫 / 203 / category-click | HTTP 400 | INVALID_SELECTION |

辅助冒烟脚本初次以所有来源都为 `ok` 断言，在番茄 `partial` 时失败。随后按既有 API 契约分别验证三站状态并继续完成检查，保留初次失败日志；起点四项仍严格要求 `ok`、十条、连续名次和完整标题/作者，未放宽新修复的验收。

证据保存在 `.verification/source-fix/`：`pytest.log`、`desktop-test.log`、`real-page-parser-results.json`、`cloud-{before,after,preflight,promotion}.json`、`cloud-isolation-results.json`、`cloud-api-chain.log`、`cloud-api-doc/`、`cloud-check{,-initial}.log`、`cloud-check-results.json` 与各查询响应。这些本地日志、抓取页面和运维脚本不提交。

## 验证边界

本轮未运行 Android assemble、Xcode/iOS 构建、设备安装或三端发布打包；共享 JVM/UI 测试不能替代平台运行验证。未重新进行桌面窗口人工联调，当前去除七猫的客户端行为依赖目录重新加载。

沿用 `quality_gate=off`，最终质量验收：**SKIPPED**。未运行 Harness、门禁覆盖率或双 Agent 审核；普通测试和 API 链路已完成。
