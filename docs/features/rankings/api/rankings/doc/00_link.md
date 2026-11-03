# rankings - API test link

> 初版接口快照：保留生成时的四站目录与来源状态。当前三站契约见[接口说明](../../../../../api/rankings.md)，本轮云端测试结果见[来源修复记录](../../../v0.1.0/server/source-fix.md)。

Base URL: `http://127.0.0.1:8000`

执行时间：2026-11-03T06:27:37.980443+00:00；环境：本地服务 / 真实上游。无认证，不需要 token。

API 契约测试通过不代表所有来源可用；blocked 等业务状态会原样记录。
生成的榜单是运行时快照；稳定契约见 [接口说明](../../../../../api/rankings.md)。

| # | Interface | Status | Result | Doc |
| --- | --- | --- | --- | --- |
| 1 | `GET /health` | `200` | PASS | [01_health.md](01_health.md) |
| 2 | `GET /api/v1/catalog` | `200` | PASS | [02_catalog.md](02_catalog.md) |
| 3 | `GET /api/v1/rankings` | `200` | PASS | [03_rankings.md](03_rankings.md) |
| 4 | `GET /api/v1/rankings` | `200` | PASS | [04_cache.md](04_cache.md) |
| 5 | `GET /api/v1/rankings` | `200` | PASS | [05_refresh.md](05_refresh.md) |
| 6 | `GET /api/v1/rankings` | `400` | PASS | [06_invalid_source.md](06_invalid_source.md) |
| 7 | `GET /api/v1/rankings` | `400` | PASS | [07_invalid_combination.md](07_invalid_combination.md) |
| 8 | `GET /api/v1/rankings` | `422` | PASS | [08_missing.md](08_missing.md) |
| 9 | `GET /api/v1/rankings` | `422` | PASS | [09_invalid_refresh.md](09_invalid_refresh.md) |
| 10 | `GET /api/v1/rankings` | `200` | PASS | [10_other_source.md](10_other_source.md) |
