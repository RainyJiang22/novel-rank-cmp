# Server v0.1.0 云部署记录

日期：2026-11-03；目标：`47.251.189.239`。用户明确要求部署现有榜单接口，且不能影响机器上的其他服务。应用源码对应 `6a5927a`，本轮未修改 API、来源解析或缓存实现。

## 已上线入口

基础地址：`https://47.251.189.239/novelrank`。

| 接口 | 公网结果 |
| --- | --- |
| [GET /health](https://47.251.189.239/novelrank/health) | 200，`{"status":"ok"}` |
| [GET /api/v1/catalog](https://47.251.189.239/novelrank/api/v1/catalog) | 200，四站目录 |
| GET /api/v1/rankings?source&category&board | 200 业务结果；非法组合 400、参数缺失或类型错误 422 |
| [Swagger /docs](https://47.251.189.239/novelrank/docs) | 200 |
| [OpenAPI](https://47.251.189.239/novelrank/openapi.json) | 200，`servers=[{"url":"/novelrank"}]` |

请求均使用正常证书校验，没有关闭 TLS 验证。接口文档位于 `/novelrank/docs`；基础地址 `/novelrank/` 没有应用首页。

## 隔离措施及实测

- Alibaba Linux 3 / x86_64，使用已有 Python 3.11.13 创建独立 `/opt/novelrank/venv`，固定依赖 `pip check` 通过；不使用系统 Python 3.6 或原应用的虚拟环境。
- 源码目录 `/opt/novelrank/releases/server-v0.1.0-6a5927a`，`current` 软链；上传包仅包含服务源码、requirements 与部署模板，上传后核对文件哈希。
- 独立非登录用户、`novelrank.service`、单 worker、`127.0.0.1:18766`。实际监听仅回环地址，未开新公网端口或改动防火墙。
- 生效限制：`MemoryMax=268435456`（256 MiB），`CPUQuotaPerSecUSec=500ms`（单核 50%），`TasksMax=64`。15:08 检查进程内存约 49 MiB，MainPID `2325425`。
- Nginx 使用独立限流 zone；只在原 HTTPS server 中新增 `include /etc/novelrank/nginx-location.conf;`，该行移除后的内容与部署前备份完全一致。
- `nginx -t` 成功后执行平滑 `nginx -s reload`。保留现有证书、原根路由 upstream、认证文件和代理头。
- 专用日志目录及 `/etc/logrotate.d/novelrank`，7 份轮转、5 MiB 检查阈值，dry-run 通过；现有 `/etc/cron.daily/logrotate` 可执行。使用 `copytruncate`，不发送重启/reload 信号，不匹配其他应用日志。Uvicorn 关闭 access log。

15:08（Asia/Shanghai）对比部署前记录：**28 个已运行服务的 MainPID、ActiveState 均无变化，Nginx master PID 无变化**。

| 原服务 | 部署前后 |
| --- | --- |
| ipa-review.service | active，MainPID `2318679` |
| postgresql.service | active，MainPID `185320` |
| Nginx master | PID `106529` |
| HTTPS `/` | 仍为 401，`Basic realm="IPA Review"` |

没有重启原应用或数据库，没有修改其认证信息。上述证据覆盖配置、进程和原根路径认证响应；未执行原业务登录后的功能回归，也未做同机负载/压力测试。

原配置及服务基线保存在服务器 `/etc/novelrank/backups/20261103-initial/`。安装、更新和最小回滚步骤见 [部署操作说明](../../../../../server/deploy/README.md)。

## API 链路与来源结果

执行：

```bash
.venv/bin/python docs/features/rankings/api/rankings/request/rankings.py \
  --base-url https://47.251.189.239/novelrank \
  --docs-dir .verification/cloud/api-doc \
  --evidence-label '云端 HTTPS 服务 / 真实上游'
```

结果：**10/10 PASS**。覆盖健康、目录、番茄真实前十、缓存一致性、60 秒刷新冷却、非法网站、非法组合、缺少参数、错误 refresh 类型和跨站状态。未使用 `--allow-upstream-failure`。本轮重用了已有脚本，没有新造 API 契约。

15:09–15:10 有限云端来源检查：

| 来源 / 分类 / 榜单 | 业务状态 | 作品数 | 说明 |
| --- | --- | ---: | --- |
| 番茄 `1_1141 / reading` | ok | 10 | 真实前十；另有链路脚本默认 `1_261 / reading` 成功 |
| 晋江 `ancient-romance / gold` | ok | 10 | 分类收入金榜，金额未公开 |
| 七猫 `boy / hot-daily` | unavailable | 0 | 原站返回 HTTP 405，接口保留明确失败原因 |
| 起点 `all / yuepiao` | blocked | 0 | 原站 HTTP 202 访问限制 |

随后桌面客户端实际展示晋江「衍生言情」前十。没有填充模拟数据或用其他网站替代受限来源，也未绕过来源验证。此前本地七猫成功不等于这台云服务器出口可用；目录的 141 种组合没有全部在线验证。

## 证据与交付边界

原始证据位于本地忽略目录 `.verification/cloud/`：`public-checks.json`、`isolation.json`、`source-checks.json`、`api-chain.log`、`api-doc/`、`manifest.json`、`logrotate-check.log`。远程实际配置/SSH 配置和备份不进入 Git。仓库只保留可复用模板与本记录。

实现与部署验证完成后，用户追加“提交下”，按授权将客户端及部署模板、文档创建为本地提交，未推送；云端服务源码仍对应 `6a5927a`。普通 API 验证完成；**最终质量验收 SKIPPED（沿用 quality_gate=off）**，未执行 Harness、覆盖率门禁和双 Agent。
