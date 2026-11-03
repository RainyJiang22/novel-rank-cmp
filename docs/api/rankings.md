# 小说热榜 API v0.1.0

本地默认地址 `http://127.0.0.1:8000`，无认证。OpenAPI 为 `/openapi.json`，交互文档为 `/docs`。字段使用 camelCase，时间使用带 UTC 时区的 ISO 8601。

本文件是稳定契约；[初版测试链生成的接口文档](../features/rankings/api/rankings/doc/00_link.md) 保留当时响应，不能作为持续更新的榜单或当前来源目录使用。当前验证见[来源修复记录](../features/rankings/v0.1.0/server/source-fix.md)。云端基础地址为 `https://47.251.189.239/novelrank`。

## 接口

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/health` | 200：`{"status":"ok"}`，只表示服务进程可响应 |
| GET | `/api/v1/catalog` | 200：`{"sources":[...]}`，支持的网站、分类和榜单，不进行来源网络请求 |
| GET | `/api/v1/rankings` | 合法查询返回 200，来源状态放在 JSON 的 `status` |

### 分类目录

`Source` 字段：`id`、`name`、`homeUrl`、`note`、`categories`、`boards`。

| 结构 | 字段 | 含义 |
| --- | --- | --- |
| Category | `id`, `name`, `group`, `boardIds` | 只允许使用该分类列出的榜单 ID |
| Board | `id`, `name`, `metricLabel` | 原站口径，不用于跨站比较 |

当前目录为起点、番茄、晋江三个来源，共 120 种合法组合。分类 ID 只在本站范围内唯一：起点使用 `all` 或官方分类 ID（如玄幻 `21`），番茄使用 `性别_官方分类ID`（如 `1_261`），晋江使用稳定英文分类 ID 对应官方分组名。七猫已移除，旧请求按未知来源在访问上游前返回 400。

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| source | string | 是 | `qidian/fanqie/jinjiang` |
| category | string | 是 | 从本站 categories 选择 |
| board | string | 是 | 必须包含于所选分类的 boardIds |
| refresh | boolean | 否 | 默认 false；true 尝试更新，但仍遵守 60 秒最短重试间隔 |

```bash
curl 'http://127.0.0.1:8000/api/v1/rankings?source=qidian&category=21&board=yuepiao'
```

### RankingSnapshot

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| sourceId / categoryId / boardId | string | 原请求的完整选择 |
| status | string | 下方状态枚举 |
| message | string | 面向用户的中文说明 |
| sourceUrl | string | 当前选择对应的官方页面 |
| fetchedAt | datetime | 成功数据的采集结束时间；无数据失败时为尝试结束时间 |
| sourceUpdatedAt | datetime/null | 来源明确提供的榜单更新时间；未知为 null，不用采集时间替代 |
| fromCache | boolean | 是否使用缓存；stale 总为 true |
| failureReason | string/null | blocked / unavailable / parse_error；stale 保留刷新失败的原因 |
| books | Book[] | 最多十条，原站顺序；失败且无旧快照时为空数组 |

### Book

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| rank | integer | 来源位置 1–10，不因元数据失败重新编号 |
| id | string | 网站作品 ID，仅在本站唯一 |
| title / author | string/null | 未能获取可读文本时为空，不返回字体编码乱码或虚构内容 |
| url | string | 官方作品页 |
| metric | string/null | 原始数值和单位；未公开或无法正确解码时为空 |
| genre | string/null | 本站分类 |
| metadataStatus | complete / partial | 标题和作者是否都完整；可选指标缺失不改变该字段 |

### 业务状态

| 状态 | 数据 | 客户端处理建议 |
| --- | --- | --- |
| ok | 十条完整排名 | 展示榜单、来源时间和缓存标记 |
| partial | 有排名，但不足十条或某些元数据/已公布指标缺失 | 展示已获取的原始名次，缺失字段显示未取得 |
| stale | 24 小时内旧数据 | 标注旧快照，保留原采集时间，显示 failureReason |
| blocked | 空 | 来源验证/访问限制；提供原站入口 |
| unavailable | 空 | 来源网络、超时或 HTTP 错误；稍后重试 |
| parse_error | 空 | 结构、分类、顺序不匹配；不能当作无作品 |

没有公开收入金额的晋江金榜、没有公开数值的起点畅销榜可以是 `ok` 且 `metric=null`；起点月票或番茄已有指标被字体编码或缺失时为 `partial`。不比较不同网站的 metric。

### HTTP 错误

- 400：未知网站、分类或不支持的组合；返回 `{"detail":{"code":"INVALID_SELECTION","message":"..."}}`。
- 422：缺少参数、字符串超长或 refresh 类型非法，返回 FastAPI 校验响应。
- 500：服务内部未知异常。不会伪装成上游失败或缓存成功。

## 缓存和边界

同一 `(source, category, board)` 请求合并；取消一个客户端请求不会影响其他等待者。新鲜期 15 分钟，旧数据上限 24 小时。失败或手动刷新不能延长旧数据年龄。立即连续点击刷新会返回同一个快照，`fromCache=true`。

缓存和节流为单进程内存状态；重启清空，当前以单 worker 启动。没有任意 URL 抓取接口，只有固定目录组合；来源跳转改变主机或所选榜单时停止请求。

## 来源核对入口

- [番茄都市日常阅读榜](https://fanqienovel.com/rank/1_2_261)：阅读/新书的作品条件及榜单更新说明来自原站。
- [晋江收入金榜](https://www.jjwxc.net/topten.php?orderstr=12)：按 `.box_06` 的官方分类分组；排除历史上榜天数列表。
- [起点玄幻月票榜](https://m.qidian.com/rank/yuepiao/catid21/) 与 [玄幻畅销榜](https://m.qidian.com/rank/hotsales/catid21/)：直接读取官方移动页面的公开 SSR JSON，校验当前月份、所选分类、榜单、第一页和原始名次；不执行页面脚本。全站榜使用不带 `catid` 的地址。
