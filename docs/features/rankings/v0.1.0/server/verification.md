# server v0.1.0 验证记录

日期：2026-11-03。环境：macOS arm64，Python 3.14.7，独立仓库 `novel-rank-cmp`，分支 `main`。本次仅实现服务端，客户端仍是工程骨架。

## 实现范围

新增 `server/app/` 的契约、目录、配置、四站独立适配器、受限 HTTP 边界、缓存和 FastAPI 生命周期；新增离线测试、来源探测脚本、API 链路脚本与中文文档。更新需求/设计/任务和根 README。

目录包含 141 种合法查询组合：起点 28、番茄 74、七猫 21、晋江 18。目录合法性全部离线检查；在线验证只覆盖下表列出的组合。

## 普通验证

```bash
.venv/bin/python -m pytest -c server/pyproject.toml server/tests -q
.venv/bin/python -m pip check
git diff --check
```

- **81 passed**。合成公开页结构验证：原站顺序、前十截断、错分类/榜单/周期、重复或损坏条目、字体编码、作品详情失败及 ID 不一致。
- 网络验证：受限状态、非 200、超时、连接失败、GB18030、gzip（含缺失编码头）、空页、超限、重定向与域名限制、总并发、关闭连接。
- 服务验证：完整查询键隔离、15 分钟新鲜缓存、60 秒刷新/错误冷却、24 小时旧快照绝对上限、并发合并、客户端取消隔离、查询总超时、服务关闭取消工作、未知异常 500。
- API 验证：三条路由、camelCase、OpenAPI、400/422、来源失败业务状态、真实 loopback HTTP + 系统 curl 自动生成 11 份文档。该测试的来源为合成数据，与下方在线证据分开。
- `pip check`：`No broken requirements found.`；差异空白检查通过。
- 一个第三方弃用提示：Starlette TestClient 提示未来使用 httpx2；当前 HTTPX 测试仍通过，未隐藏该警告。

## 真实来源验证

```bash
.venv/bin/python scripts/probe_sources.py
.venv/bin/python -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
.venv/bin/python docs/features/rankings/api/rankings/request/rankings.py
```

API 链路 **10/10 PASS**：健康 → 目录 → 番茄分类排名 → 缓存 → 立即刷新冷却 → 未知网站 400 → 不支持组合 400 → 缺参数 422 → 非法 refresh 422 → 独立起点来源状态。实际请求、响应和时间见 [API 链路大纲](../../api/rankings/doc/00_link.md)。

| 来源 | category / board | UTC 采集时间 | 结果 |
| --- | --- | --- | --- |
| 番茄 | `1_261 / reading`，男频都市日常阅读榜 | 06:22:03，API 链路随后再次验证 | ok，10 条，标题/作者完整 |
| 番茄 | `0_748 / new`，女频豪门总裁新书榜 | 06:28:05 | ok，10 条，标题/作者完整 |
| 七猫 | `203 / category-click`，都市按点击量排序 | 06:22:04 | ok，10 条，未公开点击数值为 null |
| 七猫 | `boy / hot-daily`，男生大热日榜 | 06:28:06 | ok，10 条，热度单位保留 |
| 七猫 | `girl / hot-monthly`，女生大热月榜 | 06:28:07 | ok，10 条，热度单位保留 |
| 晋江 | `ancient-romance / gold`，古代言情收入金榜 | 06:22:05 | ok，10 条，未公开金额为 null |
| 晋江 | `modern-romance / gold`，现代言情收入金榜 | 06:28:08 | ok，10 条 |
| 起点 | `21 / yuepiao`，玄幻月票榜 | 06:22:05，API 链路随后再次验证 | blocked，HTTP 202，空 books |

本次只读公开排名和作品页元数据，没有读取章节接口或运行验证绕过。起点正常页解析只使用合成结构验证；当前官方页面无法读取，真实解析选择器、全部分类映射与畅销榜仍需在来源恢复后复核。未测分类可能因网站改版或站点限制返回明确失败状态，不应被视为全部接通。

本地网络日志、探测 JSON/HTML、虚拟环境存放在忽略目录，不作为源码交付。API 文档仅保留公开元数据响应快照，没有账号凭据、个人路径或小说正文。

## 工作流结果与边界

- 已完成分析更新、设计更新、任务拆解、编码、普通测试、API 链路与中文接口文档。
- 沿用 `quality_gate=off`。**最终质量验收：SKIPPED**。
- Harness、门禁覆盖率、专用静态扫描、测试 Agent、架构 Agent、最终 Harness 均未执行，不报告为通过。
- 普通测试首次 80 项通过，新增 API 链路脚本验证后 81 项通过；无失败回退。没有未完成的正常测试任务。
- 未进行 Android/iOS/macOS 构建、客户端榜单接入、公网部署、持久存储或登录体系。

依赖实践依据：[FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/)、[HTTPX 连接池与关闭](https://www.python-httpx.org/advanced/clients/)。来源口径入口见 [接口说明](../../../../api/rankings.md)。
