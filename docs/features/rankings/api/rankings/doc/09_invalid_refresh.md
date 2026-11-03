# GET /api/v1/rankings

刷新参数类型错误返回 422。

> 执行时间：2026-11-03T06:27:37.980443+00:00；环境：本地服务 / 真实上游；结果：PASS。以下是本次 HTTP 实际响应，仅是运行记录，不能当作当前榜单。

## Parameters

| 参数 | 类型 | 必填 | 本次值 | 说明 |
| --- | --- | --- | --- | --- |
| source | string | 是 | `fanqie` | 网站 ID，来自目录 |
| category | string | 是 | `1_261` | 该网站分类 ID，来自目录 |
| board | string | 是 | `reading` | 该分类支持的榜单 ID |
| refresh | boolean | 否 | `invalid` | 是否刷新；仍受最短重试间隔约束 |

GET 无请求体。

## Response `422`

```json
{
  "detail": [
    {
      "type": "bool_parsing",
      "loc": [
        "query",
        "refresh"
      ],
      "msg": "Input should be a valid boolean, unable to interpret input",
      "input": "invalid"
    }
  ]
}
```

## curl

```bash
curl --silent --show-error --max-time 50 --request GET --write-out '
%{http_code}' 'http://127.0.0.1:8000/api/v1/rankings?source=fanqie&category=1_261&board=reading&refresh=invalid'
```
