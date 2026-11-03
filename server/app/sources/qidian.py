import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from ..catalog import Selection
from .base import SourceError, SourceHTTP, SourceResult, clean, make_book, numeric_metric, require


def current_month() -> str:
    return datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m")


def ssr_text(value) -> str | None:
    # The SSR serializer escapes literal leading ! as !!; other ! values encode non-text types.
    if not isinstance(value, str):
        return None
    if value.startswith("!!"):
        value = value[1:]
    elif value.startswith("!"):
        return None
    return clean(value)


def selected_filter(filters: list, key: str) -> dict:
    matches = [f for f in filters if isinstance(f, dict) and f.get("key") == key]
    require(len(matches) == 1, "起点筛选信息缺失或重复。")
    options, index = matches[0].get("items"), matches[0].get("selectedIndex")
    require(isinstance(options, list) and type(index) is int and 0 <= index < len(options),
            "起点筛选选中项无效。")
    require(isinstance(options[index], dict), "起点筛选选中项无效。")
    return options[index]


class Qidian:
    def __init__(self, http: SourceHTTP):
        self.http = http

    async def ranking(self, selection: Selection) -> SourceResult:
        # Parse public JSON from the official mobile page; never execute its scripts.
        soup = BeautifulSoup(await self.http.get(selection.url), "html.parser")
        scripts = soup.select('script#vite-plugin-ssr_pageContext[type="application/json"]')
        require(len(scripts) == 1, "起点页面缺少唯一的公开榜单数据。")
        try:
            payload = json.loads(scripts[0].get_text())
        except (ValueError, RecursionError):
            raise SourceError("parse_error", "起点公开榜单数据不是有效 JSON。") from None
        require(isinstance(payload, dict))
        context = payload.get("pageContext")
        require(isinstance(context, dict))
        require(context.get("isMM") is False and context.get("mDomain") == "m.qidian.com",
                "起点站点或频段不匹配。")
        # This public SSR payload encodes absent optional values as the literal !undefined.
        require(context.get("errorMsg") in (None, "", "!undefined")
                and context.get("redirectUrl") in (None, "", "!undefined"), "起点返回错误或跳转页面。")
        require(context.get("urlPathname") == urlsplit(selection.url).path, "起点页面地址与所选榜单不匹配。")
        route = context.get("routeParams")
        require(isinstance(route, dict) and route.get("pageType") == selection.board.id
                and route.get("gender") == "male", "起点榜单类型不匹配。")
        expected_filter = "" if selection.category.id == "all" else f"catid{selection.category.id}"
        require(route.get("filterParamOne") == expected_filter and route.get("filterParamTwo") == "",
                "起点分类或榜单周期不匹配。")
        props = context.get("pageProps")
        require(isinstance(props, dict))
        data = props.get("pageData")
        require(isinstance(data, dict) and data.get("gender") == "male"
                and type(data.get("pageNum")) is int and data["pageNum"] == 1, "起点未返回所选频段第一页。")
        filters = data.get("filters")
        require(isinstance(filters, list))
        category = selected_filter(filters, "catId")
        expected_id = "-1" if selection.category.id == "all" else selection.category.id
        expected_name = "全站" if selection.category.id == "all" else selection.category.name
        require(str(category.get("value")) == expected_id and category.get("text") == expected_name,
                "起点所选分类不匹配。")
        monthly = selection.board.id == "yuepiao"
        if monthly:
            month = selected_filter(filters, "yearmonth")
            require(month.get("text") == "当月" and str(month.get("value")) == current_month(),
                    "起点未返回当月月票榜。")
        rows = data.get("records")
        require(isinstance(rows, list), "起点排名列表格式发生变化。")
        books = []
        for rank, row in enumerate(rows[:10], 1):
            require(isinstance(row, dict), "起点排名条目格式发生变化。")
            id_ = row.get("bid")
            require(isinstance(id_, str) and re.fullmatch(r"[0-9]{1,20}", id_), "起点作品 ID 格式发生变化。")
            require(type(row.get("rankNum")) is int and row["rankNum"] == rank, "起点排名顺序发生变化。")
            if selection.category.id != "all":
                require(str(row.get("catId")) == selection.category.id, "起点作品不属于所选分类。")
            metric = None
            if monthly:
                raw_metric = ssr_text(row.get("rankCnt"))
                if raw_metric and raw_metric.endswith("月票"):
                    metric = numeric_metric(raw_metric.removesuffix("月票"), "月票")
            genre = " · ".join(filter(None, (ssr_text(row.get("cat")), ssr_text(row.get("subCat"))))) or None
            books.append(make_book(rank=rank, id=id_, title=ssr_text(row.get("bName")), author=ssr_text(row.get("bAuth")),
                                   url=f"https://m.qidian.com/book/{id_}/", metric=metric, genre=genre))
        return SourceResult(tuple(books), partial=monthly and any(b.metric is None for b in books)).validate()
