# GET /health

检查服务是否运行。

> 执行时间：2026-11-03T06:27:37.980443+00:00；环境：本地服务 / 真实上游；结果：PASS。以下是本次 HTTP 实际响应，仅是运行记录，不能当作当前榜单。

## Parameters

无。

GET 无请求体。

## Response `200`

```json
{
  "status": "ok"
}
```

## curl

```bash
curl --silent --show-error --max-time 50 --request GET --write-out '
%{http_code}' http://127.0.0.1:8000/health
```
