"""Synthetic public-page structures, never copied novel text or a live-network dependency."""
import asyncio
import json

import pytest

from server.app.catalog import validate_selection
from server.app.sources.base import SourceResult, make_book


class FakeHTTP:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    async def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        value = self.pages[url] if isinstance(self.pages, dict) else self.pages
        if isinstance(value, Exception):
            raise value
        return value


def ssr(state):
    return '<script>window.__INITIAL_STATE__ = ' + json.dumps(state, ensure_ascii=False) + ';</script>'


def fanqie_state(count=10):
    return {"rank": {
        "rankCategoryTypeList": {"male": [{"id": "261", "name": "都市日常"}]},
        "rankVersion": "1793676000",
        "book_list": [{"bookId": str(1000 + i), "currentPos": i, "curent_category_id": 261,
                       "pos_category_id": 261, "bookName": f"测试作品{i}", "author": f"测试作者{i}",
                       "read_count": "12345", "readCount": "0"} for i in range(1, count + 1)],
    }}


def jinjiang_page(category="古代言情", count=10):
    rows = ''.join(f'''<li><a href="onebook.php?novelid={i}" title="测试作品{i}">省略名</a>
        <a href="oneauthor.php?authorid={i}"><span class="author">测试作者{i}</span></a></li>'''
                   for i in range(1, count + 1))
    # Deliberately include a similarly titled historical section which must not be selected.
    return f'''<title>【收入金榜排行榜】_晋江文学城</title>
        <div class="wrapper box_07"><h5>{category}</h5><ul class="list_01"><li>历史榜</li></ul></div>
        <div class="wrapper box_06"><h5>{category}</h5><ul class="list_01">{rows}</ul></div>'''


def qidian_state(count=10, *, board="yuepiao", category="21"):
    filters = [{"key": "catId", "selectedIndex": 0, "items": [{"value": -1 if category == "all" else int(category),
                "text": "全站" if category == "all" else "玄幻"}]}]
    if board == "yuepiao":
        filters.append({"key": "yearmonth", "selectedIndex": 0, "items": [{"value": "202611", "text": "当月"}]})
    suffix = "" if category == "all" else f"catid{category}/"
    return {"pageContext": {
        "isMM": False, "mDomain": "m.qidian.com", "urlPathname": f"/rank/{board}/{suffix}",
        "errorMsg": "!undefined", "redirectUrl": "!undefined",
        "routeParams": {"pageType": board, "gender": "male", "filterParamOne": suffix.rstrip("/"), "filterParamTwo": ""},
        "pageProps": {"pageData": {"gender": "male", "pageNum": 1, "filters": filters,
            "records": [{"bid": str(i), "bName": f"测试作品{i}", "bAuth": f"测试作者{i}", "rankNum": i,
                         "catId": 21, "cat": "玄幻", "subCat": "东方玄幻",
                         **({"rankCnt": "1.23万月票"} if board == "yuepiao" else {})} for i in range(1, count + 1)]}},
    }}


def qidian_page(state):
    return '<script id="vite-plugin-ssr_pageContext" type="application/json">' + json.dumps(state, ensure_ascii=False) + '</script>'


@pytest.fixture
def selection():
    return validate_selection("fanqie", "1_261", "reading")


@pytest.fixture
def result():
    return SourceResult(tuple(make_book(rank=i, id=str(i), title=f"测试作品{i}", author="测试作者",
                                       url=f"https://fanqienovel.com/page/{i}") for i in range(1, 11)))


class Adapter:
    def __init__(self, result):
        self.result = result
        self.calls = 0
        self.started = asyncio.Event()
        self.release = None

    async def ranking(self, selection):
        self.calls += 1
        self.started.set()
        if self.release is not None:
            await self.release.wait()
        if isinstance(self.result, Exception):
            raise self.result
        return self.result
