# GET /api/v1/rankings

重复查询命中缓存，采集时间与作品顺序不变。

> 执行时间：2026-11-03T06:27:37.980443+00:00；环境：本地服务 / 真实上游；结果：PASS。以下是本次 HTTP 实际响应，仅是运行记录，不能当作当前榜单。

## Parameters

| 参数 | 类型 | 必填 | 本次值 | 说明 |
| --- | --- | --- | --- | --- |
| source | string | 是 | `fanqie` | 网站 ID，来自目录 |
| category | string | 是 | `1_261` | 该网站分类 ID，来自目录 |
| board | string | 是 | `reading` | 该分类支持的榜单 ID |

GET 无请求体。

## Response `200`

```json
{
  "sourceId": "fanqie",
  "categoryId": "1_261",
  "boardId": "reading",
  "status": "ok",
  "message": "已获取来源前十名。",
  "sourceUrl": "https://fanqienovel.com/rank/1_2_261",
  "fetchedAt": "2026-11-03T06:27:43.753116Z",
  "sourceUpdatedAt": "2026-11-03T06:20:00Z",
  "fromCache": true,
  "failureReason": null,
  "books": [
    {
      "rank": 1,
      "id": "7646327973087300670",
      "title": "公安局长之扫黑风暴",
      "author": "南至",
      "url": "https://fanqienovel.com/page/7646327973087300670",
      "metric": "790871人在读",
      "genre": "都市日常",
      "metadataStatus": "complete"
    },
    {
      "rank": 2,
      "id": "7326876174989134910",
      "title": "天眼风水师",
      "author": "道之光",
      "url": "https://fanqienovel.com/page/7326876174989134910",
      "metric": "725795人在读",
      "genre": "都市日常",
      "metadataStatus": "complete"
    },
    {
      "rank": 3,
      "id": "7501902210347830334",
      "title": "公考逆袭：从面试开始一路攀登",
      "author": "元明小阳",
      "url": "https://fanqienovel.com/page/7501902210347830334",
      "metric": "712621人在读",
      "genre": "都市日常",
      "metadataStatus": "complete"
    },
    {
      "rank": 4,
      "id": "7630067790849788953",
      "title": "都重生了，谁还装富二代啊",
      "author": "爱和美式",
      "url": "https://fanqienovel.com/page/7630067790849788953",
      "metric": "645345人在读",
      "genre": "都市日常",
      "metadataStatus": "complete"
    },
    {
      "rank": 5,
      "id": "7259957689197792297",
      "title": "开局停职？我转投纪委调查组",
      "author": "江门二爷",
      "url": "https://fanqienovel.com/page/7259957689197792297",
      "metric": "534857人在读",
      "genre": "都市日常",
      "metadataStatus": "complete"
    },
    {
      "rank": 6,
      "id": "7487619780287941656",
      "title": "穿书后，我把女主养成病娇了",
      "author": "狂打胰岛素",
      "url": "https://fanqienovel.com/page/7487619780287941656",
      "metric": "523647人在读",
      "genre": "都市日常",
      "metadataStatus": "complete"
    },
    {
      "rank": 7,
      "id": "7658653641691106329",
      "title": "财阀大小姐的恶毒男友重生了",
      "author": "白月疏",
      "url": "https://fanqienovel.com/page/7658653641691106329",
      "metric": "512776人在读",
      "genre": "都市日常",
      "metadataStatus": "complete"
    },
    {
      "rank": 8,
      "id": "7645556324868049945",
      "title": "穿书反派，把阴湿女主养成病娇了",
      "author": "二次元的猫",
      "url": "https://fanqienovel.com/page/7645556324868049945",
      "metric": "508531人在读",
      "genre": "都市日常",
      "metadataStatus": "complete"
    },
    {
      "rank": 9,
      "id": "7212512693792541734",
      "title": "宦海官途",
      "author": "风流小二",
      "url": "https://fanqienovel.com/page/7212512693792541734",
      "metric": "494181人在读",
      "genre": "都市日常",
      "metadataStatus": "complete"
    },
    {
      "rank": 10,
      "id": "7628905846411365400",
      "title": "官场：她走后，我青云直上！",
      "author": "幸运指",
      "url": "https://fanqienovel.com/page/7628905846411365400",
      "metric": "485209人在读",
      "genre": "都市日常",
      "metadataStatus": "complete"
    }
  ]
}
```

## curl

```bash
curl --silent --show-error --max-time 50 --request GET --write-out '
%{http_code}' 'http://127.0.0.1:8000/api/v1/rankings?source=fanqie&category=1_261&board=reading'
```
