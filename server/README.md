# NovelRank Server v0.1.0

Python 3.11+ / FastAPI 聚合服务。提供起点、番茄、七猫、晋江的版本化分类目录和按需前十查询，保留各站排名口径、来源链接、采集时间及失败状态。客户端本轮尚未接入。

## 启动

以下命令都在仓库根目录运行；Android Studio 底部 Terminal 也可直接使用：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r server/requirements-dev.txt
.venv/bin/python -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
```

只运行服务时可安装 `server/requirements.txt`。Windows 使用 `.venv\Scripts\python.exe`。依赖版本固定，实测环境为 macOS arm64 / Python 3.14.7。

- Swagger：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 健康检查：[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- 分类目录：[http://127.0.0.1:8000/api/v1/catalog](http://127.0.0.1:8000/api/v1/catalog)

```bash
curl 'http://127.0.0.1:8000/api/v1/rankings?source=fanqie&category=1_261&board=reading'
```

开发时可添加 `--reload`。内存缓存、请求间隔和并发合并都按进程生效，当前使用 **单 worker**。重启会清空缓存。

后续连接真机时可显式改为 `--host 0.0.0.0`，设备使用本机局域网 IP。Android 模拟器通常使用 `10.0.2.2:8000`，桌面与 iOS 模拟器使用 `127.0.0.1:8000`。本轮没有实现客户端网络配置、认证或公网部署。

## 目录口径

| 网站 | 首版支持 | 数据含义 |
| --- | --- | --- |
| 起点 | 常用 14 类（含全部），月票 / 畅销 | 受限时返回 `blocked`；当前未完成真实榜单解析验证 |
| 番茄 | 男频 19 类、女频 18 类，阅读 / 新书 | 原站名次，在读人数；被字体编码的书名通过公开作品页补全 |
| 七猫 | 男女大热日榜 / 月榜；17 个小说分类按点击量排序 | 大热榜热度与书库点击量保持区别；书库未公开数值返回 `null` |
| 晋江 | 18 个分类收入金榜 | 官方分类分组的收入排序，金额未公开；不等同月榜 |

目录是支持范围，不能当作实时可用性保证；未列出的分类不接受查询。不会把全站榜按类型筛选后冒充分类榜。

## 状态与缓存

- `ok`：取得十条且必要元数据完整；`partial`：不足十条、标题/作者缺失或已公布的指标无法解析。保留原名次，不补假数据。
- `blocked`：202/401/403/429 或验证页面；`unavailable`：网络、超时或其他非 200；`parse_error`：结构、分类、排序或数据格式不符。
- `stale`：获取失败后使用不超过 24 小时的旧快照，保留原 `fetchedAt`，`failureReason` 提供当前失败原因。
- 缓存按网站、分类、榜单隔离，新鲜期 15 分钟；同查询并发合并；每次请求完成后至少 60 秒才重取，`refresh=true` 同样遵守。
- 公开页请求默认总并发 4、同站启动间隔 0.5 秒、单页总预算 10 秒、整次查询总预算 40 秒、响应上限 3 MB。

仅公开书名、作者、排名、类型和来源链接。没有章节/正文接口，不处理登录、验证码、付费内容，不做后台持续扫榜。

## 本地配置

可选环境变量示例见 [.env.example](.env.example)。应用读取 `NOVELRANK_*` 环境变量，**不自动加载 `.env`**。例如：

```bash
export NOVELRANK_QUERY_TIMEOUT=45
.venv/bin/python -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
```

个人变量、`.env`、虚拟环境、日志和 `.verification/` 探测文件均不提交。

## 测试和接口文档

离线测试不请求任何真实小说网站，使用合成 HTML、HTTP 故障注入和本地临时端口：

```bash
.venv/bin/python -m pytest -c server/pyproject.toml server/tests -q
```

有限在线探测（默认每站一种组合，不遍历全站）：

```bash
.venv/bin/python scripts/probe_sources.py
```

保持服务运行，在另一终端执行完整 API 测试链。脚本调用系统 `curl`，生成含实际响应和可复制请求的中文文档：

```bash
.venv/bin/python docs/features/rankings/api/rankings/request/rankings.py
```

默认要求首个番茄查询取得真实数据；网络受限时可显式加 `--allow-upstream-failure` 只验证接口契约，并在报告中保留失败业务状态。自定义服务使用 `--base-url`；生成本地运行记录可加 `--docs-dir .verification/server/api-doc`。

[稳定接口契约](../docs/api/rankings.md) · [API 链路文档](../docs/features/rankings/api/rankings/doc/00_link.md) · [本次验证记录](../docs/features/rankings/v0.1.0/server/verification.md)

最终质量验收：`SKIPPED（quality_gate=off）`，普通测试和 API 链路独立执行。
