# GET /api/v1/catalog

获取版本化网站、分类和榜单目录。

> 执行时间：2026-11-03T06:27:37.980443+00:00；环境：本地服务 / 真实上游；结果：PASS。以下是本次 HTTP 实际响应，仅是运行记录，不能当作当前榜单。

## Parameters

无。

GET 无请求体。

## Response `200`

```json
{
  "sources": [
    {
      "id": "qidian",
      "name": "起点中文网",
      "homeUrl": "https://www.qidian.com/",
      "note": "分类月票榜与畅销榜；验证页面返回 blocked，字体编码的数值不猜测。",
      "categories": [
        {
          "id": "all",
          "name": "全部分类",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "21",
          "name": "玄幻",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "1",
          "name": "奇幻",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "2",
          "name": "武侠",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "22",
          "name": "仙侠",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "4",
          "name": "都市",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "15",
          "name": "现实",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "6",
          "name": "军事",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "5",
          "name": "历史",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "7",
          "name": "游戏",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "8",
          "name": "体育",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "9",
          "name": "科幻",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "10",
          "name": "悬疑灵异",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        },
        {
          "id": "12",
          "name": "轻小说",
          "group": "男生",
          "boardIds": [
            "yuepiao",
            "hotsales"
          ]
        }
      ],
      "boards": [
        {
          "id": "yuepiao",
          "name": "月票榜",
          "metricLabel": "月票"
        },
        {
          "id": "hotsales",
          "name": "畅销榜",
          "metricLabel": "销售指数"
        }
      ]
    },
    {
      "id": "fanqie",
      "name": "番茄小说",
      "homeUrl": "https://fanqienovel.com/",
      "note": "原站阅读榜/新书榜；通过公开作品详情补全被字体编码的名称。",
      "categories": [
        {
          "id": "1_1141",
          "name": "西方奇幻",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_1140",
          "name": "东方仙侠",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_8",
          "name": "科幻末世",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_261",
          "name": "都市日常",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_124",
          "name": "都市修真",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_1014",
          "name": "都市高武",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_273",
          "name": "历史古代",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_27",
          "name": "战神赘婿",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_263",
          "name": "都市种田",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_258",
          "name": "传统玄幻",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_272",
          "name": "历史脑洞",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_539",
          "name": "悬疑脑洞",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_262",
          "name": "都市脑洞",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_257",
          "name": "玄幻脑洞",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_751",
          "name": "悬疑灵异",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_504",
          "name": "抗战谍战",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_746",
          "name": "游戏体育",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_718",
          "name": "动漫衍生",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "1_1016",
          "name": "男频衍生",
          "group": "男频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_1139",
          "name": "古风世情",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_8",
          "name": "科幻末世",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_746",
          "name": "游戏体育",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_1015",
          "name": "女频衍生",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_248",
          "name": "玄幻言情",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_23",
          "name": "种田",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_79",
          "name": "年代",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_267",
          "name": "现言脑洞",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_246",
          "name": "宫斗宅斗",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_539",
          "name": "悬疑脑洞",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_253",
          "name": "古言脑洞",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_24",
          "name": "快穿",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_749",
          "name": "青春甜宠",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_745",
          "name": "星光璀璨",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_747",
          "name": "女频悬疑",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_750",
          "name": "职场婚恋",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_748",
          "name": "豪门总裁",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        },
        {
          "id": "0_1017",
          "name": "民国言情",
          "group": "女频",
          "boardIds": [
            "reading",
            "new"
          ]
        }
      ],
      "boards": [
        {
          "id": "reading",
          "name": "阅读榜",
          "metricLabel": "在读人数"
        },
        {
          "id": "new",
          "name": "新书榜",
          "metricLabel": "在读人数"
        }
      ]
    },
    {
      "id": "qimao",
      "name": "七猫中文网",
      "homeUrl": "https://www.qimao.com/",
      "note": "男女大热榜使用热度；分类书库按点击量排序，无公开数值时 metric 为 null。",
      "categories": [
        {
          "id": "boy",
          "name": "男生",
          "group": "全频大热榜",
          "boardIds": [
            "hot-daily",
            "hot-monthly"
          ]
        },
        {
          "id": "girl",
          "name": "女生",
          "group": "全频大热榜",
          "boardIds": [
            "hot-daily",
            "hot-monthly"
          ]
        },
        {
          "id": "1",
          "name": "现代言情",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "2",
          "name": "古代言情",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "4",
          "name": "幻想言情",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "56",
          "name": "历史",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "60",
          "name": "军事",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "64",
          "name": "科幻",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "75",
          "name": "游戏",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "200",
          "name": "游戏竞技",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "202",
          "name": "玄幻奇幻",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "203",
          "name": "都市",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "204",
          "name": "奇闻异事",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "205",
          "name": "武侠仙侠",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "206",
          "name": "体育",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "207",
          "name": "N次元",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "277",
          "name": "衍生言情",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "306",
          "name": "现实题材",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        },
        {
          "id": "307",
          "name": "现实主义",
          "group": "小说分类",
          "boardIds": [
            "category-click"
          ]
        }
      ],
      "boards": [
        {
          "id": "hot-daily",
          "name": "大热榜·日榜",
          "metricLabel": "热度"
        },
        {
          "id": "hot-monthly",
          "name": "大热榜·月榜",
          "metricLabel": "热度"
        },
        {
          "id": "category-click",
          "name": "分类点击量排序",
          "metricLabel": "点击量（数值未公开）"
        }
      ]
    },
    {
      "id": "jinjiang",
      "name": "晋江文学城",
      "homeUrl": "https://www.jjwxc.net/",
      "note": "收入金榜按官方分类分组；只提供顺序，金额未公开，不等同月榜。",
      "categories": [
        {
          "id": "ancient-romance",
          "name": "古代言情",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "modern-romance",
          "name": "现代言情",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "time-travel",
          "name": "古代穿越",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "modern-danmei",
          "name": "现代都市纯爱",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "fantasy-danmei",
          "name": "现代幻想纯爱",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "ancient-danmei",
          "name": "古代纯爱",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "fan-danmei",
          "name": "衍生纯爱",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "modern-fantasy",
          "name": "幻想现言",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "fantasy-romance",
          "name": "奇幻言情",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "future-mystery",
          "name": "未来游戏悬疑",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "baihe",
          "name": "百合",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "no-cp",
          "name": "无CP",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "anime-romance",
          "name": "二次元言情",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "fan-romance",
          "name": "衍生言情",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "fan-no-cp",
          "name": "衍生无cp",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "future-danmei",
          "name": "未来幻想纯爱",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "light-novel",
          "name": "原创轻小说",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        },
        {
          "id": "diverse",
          "name": "多元",
          "group": "收入金榜",
          "boardIds": [
            "gold"
          ]
        }
      ],
      "boards": [
        {
          "id": "gold",
          "name": "分类收入金榜",
          "metricLabel": "收入排名（金额未公开）"
        }
      ]
    }
  ]
}
```

## curl

```bash
curl --silent --show-error --max-time 50 --request GET --write-out '
%{http_code}' http://127.0.0.1:8000/api/v1/catalog
```
