# 小说热榜 — 服务端任务清单

基于 `design.md`，用户要求实现 server v0.1.0。`quality_gate=off`（沿用本功能选择），普通测试和 API 链路必须执行。仅四站公开排名元数据；不实现客户端、章节、账户、反爬绕过、公网部署，不提交本地配置或抓取原文。

## 执行顺序

1. ✅ 已完成 — 契约、目录与依赖。
2. ✅ 已完成 — 四站适配器与网络边界（依赖 1）。
3. ✅ 已完成 — 缓存、路由与生命周期（依赖 2）。
4. ✅ 已完成 — 普通测试、在线探测、API 链路与文档（依赖 3）。

## 任务 1：契约与配置 `✅ 已完成`

- ✅ 1.1 新增 `server/app/__init__.py`、`models.py`：不可变 Pydantic 模型，camelCase JSON，字段见设计；`Book.title/author` 可空，`metadataStatus` 区分缺失；`RankingSnapshot.failureReason` 保留来源失败原因。
- ✅ 1.2 新增 `server/app/catalog.py`：版本化官方分类；`validate_selection(source: str, category: str, board: str) -> Selection`；所有非法组合在网络前拒绝。
- ✅ 1.3 新增 `server/app/config.py`：`Settings.from_env()`；超时、并发、来源间隔、TTL/最大旧缓存年龄、重试间隔验证。
- ✅ 1.4 新增 `server/requirements.txt`、`requirements-dev.txt`、`pyproject.toml`：固定依赖、pytest asyncio 与 Python 路径；根目录 `.venv/` 为本地环境。

## 任务 2：来源适配 `✅ 已完成`

- ✅ 2.1 新增 `server/app/sources/__init__.py`、`base.py`：`async get(url, encoding) -> str`；域名/跳转白名单、超时、有限响应、并发/间隔、明确 `SourceError`。
- ✅ 2.2 新增 `fanqie.py`：`async ranking(selection) -> SourceResult`；只解析 JSON SSR，验证分类与名次，公开作品元数据补全；不读取章节内容，详情失败保留位置。
- ✅ 2.3 新增 `qimao.py`：男女大热榜与分类点击量排序独立解析，检查选中分类/排序。
- ✅ 2.4 新增 `jinjiang.py`：GB18030 解码，收入金榜的精确分类容器，按来源位置取前十。
- ✅ 2.5 新增 `qidian.py`：月票/畅销榜分类校验，遇到验证页返回 blocked。

## 任务 3：缓存与 API `✅ 已完成`

- ✅ 3.1 新增 `server/app/service.py`：`async query(selection, refresh=False)`；完整键隔离、15 分钟缓存、24 小时旧快照、60 秒冷却、并发合并/取消隔离；未知异常保留 500。
- ✅ 3.2 新增 `server/app/main.py`：`create_app(service=None)`；health/catalog/rankings 与 OpenAPI，lifespan 释放资源。

## 任务 4：验证与交付 `✅ 已完成`

- ✅ 4.1 新增 `server/tests/{conftest,test_sources,test_service,test_api,test_http}.py` 及必要合成 fixtures：覆盖错分类、结构变化、乱码、详情部分失败、超时、跳转域名限制、缓存/并发/取消/过期与 400/422/500。
- ✅ 4.2 新增 `scripts/probe_sources.py`：每站一次有限在线请求，输出来源状态/数量/时间，不提交原站 HTML。执行 `.venv/bin/python -m pytest -c server/pyproject.toml server/tests -q`。
- ✅ 4.3 路由存在后加载 `feature-link-test-writer`，按其约定新增 `docs/features/rankings/api/rankings/request/rankings.py` 与同级 `doc/{00_link,01_health,02_catalog,03_rankings,04_cache,05_refresh,06_invalid_source,07_invalid_combination,08_missing,09_invalid_refresh,10_other_source}.md`；用 macOS/Linux `curl`、Windows `curl.exe`，无认证无需 token，记录实际返回而不造示例。新增 `docs/api/rankings.md` 为稳定契约入口及 `server/tests/test_api_chain.py` 验证脚本生成的文档；启动真实服务并执行健康 → 目录 → 合法排名 → 缓存 → 错误组合，故障测试注明合成来源。
- ✅ 4.4 修改 `README.md`，新增 `server/README.md`、`server/.env.example`、`docs/features/rankings/v0.1.0/server/verification.md`；记录运行命令、真实来源覆盖、未覆盖边界。根据链路技能要求补充精确文件路径。

最终质量验收：`SKIPPED（quality_gate=off）`；不启动 Harness、门禁覆盖率或双 Agent 审核。

## 执行结果

2026-11-03：普通测试 81 passed；本地 HTTP 合成来源链路与真实来源链路均 10/10 PASS；`pip check` 通过。在线验证三站共七种不同组合取得 10 条，起点玄幻月票榜返回 blocked。详见 [验证记录](verification.md)。未运行 Gradle/Xcode；未执行 Harness、覆盖率门禁或双 Agent。
