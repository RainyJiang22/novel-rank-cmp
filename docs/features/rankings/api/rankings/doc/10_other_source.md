# GET /api/v1/rankings

跨站查询保持独立状态；起点验证页可返回 blocked。

> 执行时间：2026-11-03T06:27:37.980443+00:00；环境：本地服务 / 真实上游；结果：PASS。以下是本次 HTTP 实际响应，仅是运行记录，不能当作当前榜单。

## Parameters

| 参数 | 类型 | 必填 | 本次值 | 说明 |
| --- | --- | --- | --- | --- |
| source | string | 是 | `qidian` | 网站 ID，来自目录 |
| category | string | 是 | `21` | 该网站分类 ID，来自目录 |
| board | string | 是 | `yuepiao` | 该分类支持的榜单 ID |

GET 无请求体。

## Response `200`

```json
{
  "sourceId": "qidian",
  "categoryId": "21",
  "boardId": "yuepiao",
  "status": "blocked",
  "message": "来源限制访问（HTTP 202），请打开原站查看。",
  "sourceUrl": "https://www.qidian.com/rank/yuepiao/chn21/",
  "fetchedAt": "2026-11-03T06:27:44.466963Z",
  "sourceUpdatedAt": null,
  "fromCache": false,
  "failureReason": "blocked",
  "books": []
}
```

## curl

```bash
curl --silent --show-error --max-time 50 --request GET --write-out '
%{http_code}' 'http://127.0.0.1:8000/api/v1/rankings?source=qidian&category=21&board=yuepiao'
```
