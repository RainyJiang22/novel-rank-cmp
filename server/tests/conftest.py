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


def qimao_page(*, library=False, category="都市", gender="男生榜", period="日榜", count=10):
    if library:
        filters = ''.join(f'<span class="cascader-radio-btn active">{s}</span>'
                          for s in ["全部", category, "全部", "全部", "全部"])
        prefix = filters + '<div class="tab-inner active">按点击量</div><span class="page-btn num active">1</span>'
        rows = ''.join(f'''<li class="qm-cover-text-item">
            <span class="s-tit"><a href="/shuku/{i}/">测试作品{i}</a></span>
            <a class="s-author">测试作者{i}</a>
            <a class="s-category" href="/shuku/a-203-220-a-a-a-a-click-1/">都市高手</a></li>'''
                       for i in range(1, count + 1))
        return prefix + '<ul>' + rows + '</ul>'
    prefix = f'''<div class="qm-switch-tab"><span class="item active">{gender}</span></div>
        <a class="child-tabs-item menu-tab active">大热榜</a>
        <div class="date-type-tabs"><a class="tab active">{period}</a></div>'''
    rows = ''.join(f'''<li class="rank-list-item"><a class="s-book-title" href="/shuku/{i}/">测试作品{i}</a>
        <span class="rank-number">{i}</span><span class="s-book-info"><a href="/zuozhe/test/">测试作者{i}</a>
        <a href="/shuku/a-203-a-a-a-a-a-click-1/">都市</a></span>
        <em class="rank-num">12.3</em><em class="rank-unit">万</em></li>''' for i in range(1, count + 1))
    return prefix + '<ul class="rank-list">' + rows + '</ul>'


def jinjiang_page(category="古代言情", count=10):
    rows = ''.join(f'''<li><a href="onebook.php?novelid={i}" title="测试作品{i}">省略名</a>
        <a href="oneauthor.php?authorid={i}"><span class="author">测试作者{i}</span></a></li>'''
                   for i in range(1, count + 1))
    # Deliberately include a similarly titled historical section which must not be selected.
    return f'''<title>【收入金榜排行榜】_晋江文学城</title>
        <div class="wrapper box_07"><h5>{category}</h5><ul class="list_01"><li>历史榜</li></ul></div>
        <div class="wrapper box_06"><h5>{category}</h5><ul class="list_01">{rows}</ul></div>'''


def qidian_page(count=10):
    rows = ''.join(f'''<li><div class="book-img-box"><span class="rank-tag">{i}</span></div>
        <div class="book-mid-info"><h2><a href="//book.qidian.com/info/{i}/">测试作品{i}</a></h2>
        <p class="author"><a class="name">测试作者{i}</a><a>玄幻</a></p></div>
        <div class="book-right-info"><p class="total"><span>123</span>月票</p></div></li>'''
                   for i in range(1, count + 1))
    return '<div class="rank-header"><h3>月票榜</h3></div><div class="type-list"><a class="act">玄幻</a></div>' \
        + '<div class="rank-view-list"><div class="book-img-text"><ul>' + rows + '</ul></div></div>'


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
