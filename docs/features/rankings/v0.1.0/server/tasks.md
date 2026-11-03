# 小说热榜 — 服务端任务清单

基于 `design.md`。**全部为后续功能任务，用户本轮要求先初始化 CMP 项目，未执行以下服务端实现。** `quality_gate=off`，API 链路等业务接口存在后执行。

## 执行顺序

1. ⬜ 待处理 — 契约与目录。
2. ⬜ 待处理 — 来源适配器。
3. ⬜ 待处理 — 缓存、路由和普通测试。
4. ⬜ 待处理 — API 链路与文档。

## 任务 1：契约 `⬜ 待处理`

- ⬜ 1.1 新增 `server/app/models.py`：`Source/Category/Board/Book/RankingSnapshot`，字段见设计。
- ⬜ 1.2 新增 `server/app/catalog.py`：`validate_selection(source, category, board)`，支持组合来自官方页面，不编造分类映射。
- ⬜ 1.3 新增 `server/requirements.txt`、`server/pyproject.toml`，固定依赖与测试目录。

## 任务 2：来源 `⬜ 待处理`

- ⬜ 2.1 新增 `server/app/sources/base.py`：`async fetch(url)`，固定域名、超时、请求间隔、受限检测。
- ⬜ 2.2 新增 `fanqie.py`：`async ranking(category, board)`，SSR 名次与公开详情元数据；部分失败保留名次。
- ⬜ 2.3 新增 `qimao.py`：大热榜与分类热度排序分别校验。
- ⬜ 2.4 新增 `jinjiang.py`：GB18030 与分类收入金榜容器解析。
- ⬜ 2.5 新增 `qidian.py`：分类榜解析与访问受限状态。

## 任务 3：服务与测试 `⬜ 待处理`

- ⬜ 3.1 新增 `server/app/service.py`：`async query(selection, refresh)`，查询键隔离、并发合并、15 分钟缓存和 24 小时旧快照上限。
- ⬜ 3.2 新增 `server/app/main.py`：health/catalog/rankings 路由，非法组合返回 400。
- ⬜ 3.3 新增 `server/tests/test_sources.py`、`test_service.py`、`test_api.py`，覆盖真实结构构造样本、超时、错误分类、乱码、过期和并发。
- ⬜ 3.4 执行 `.venv/bin/python -m pytest server/tests -q`，记录结果；在线源探测和离线测试分开。

## 任务 4：API 链路 `⬜ 待处理`

- ⬜ 4.1 实现存在后调用 `feature-link-test-writer`，新增 `scripts/test_api_chain.py` 与 `docs/api/rankings.md`。
- ⬜ 4.2 启动服务，执行健康 → 目录 → 合法榜单 → 缓存 → 错误组合链路；写入验证报告。

本轮 API 阶段：`SKIPPED（按最新指令仅初始化客户端工程，尚无业务 API）`。最终质量验收：`SKIPPED（quality_gate=off）`。
