# GET /api/v1/rankings

分类与榜单不兼容时返回 400。

> 执行时间：2026-11-03T06:27:37.980443+00:00；环境：本地服务 / 真实上游；结果：PASS。以下是本次 HTTP 实际响应，仅是运行记录，不能当作当前榜单。

## Parameters

| 参数 | 类型 | 必填 | 本次值 | 说明 |
| --- | --- | --- | --- | --- |
| source | string | 是 | `qimao` | 网站 ID，来自目录 |
| category | string | 是 | `203` | 该网站分类 ID，来自目录 |
| board | string | 是 | `hot-daily` | 该分类支持的榜单 ID |

GET 无请求体。

## Response `400`

```json
{
  "detail": {
    "code": "INVALID_SELECTION",
    "message": "网站、分类与榜单组合不受支持，请从 /api/v1/catalog 选择。"
  }
}
```

## curl

```bash
curl --silent --show-error --max-time 50 --request GET --write-out '
%{http_code}' 'http://127.0.0.1:8000/api/v1/rankings?source=qimao&category=203&board=hot-daily'
```
