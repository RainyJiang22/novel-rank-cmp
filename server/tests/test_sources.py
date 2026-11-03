import copy

import pytest

from server.app.catalog import CATALOG, validate_selection
from server.app.sources.base import SourceError, clean
from server.app.sources.fanqie import Fanqie
from server.app.sources.jinjiang import Jinjiang
from server.app.sources.qidian import Qidian
from conftest import FakeHTTP, fanqie_state, jinjiang_page, qidian_page, qidian_state, ssr


def test_catalog_combinations_have_unique_keys_and_fixed_urls():
    assert {s.id for s in CATALOG.sources} == {"qidian", "fanqie", "jinjiang"}
    keys = set()
    for source in CATALOG.sources:
        for category in source.categories:
            for board in category.board_ids:
                selection = validate_selection(source.id, category.id, board)
                assert selection.key not in keys
                keys.add(selection.key)
                assert selection.url.startswith(source.home_url)
    with pytest.raises(ValueError):
        validate_selection("qimao", "203", "category-click")
    assert len(keys) == 120


async def test_fanqie_top_ten_and_correct_metric(selection):
    http = FakeHTTP(ssr(fanqie_state(12)))
    result = await Fanqie(http).ranking(selection)
    assert [b.rank for b in result.books] == list(range(1, 11))
    assert all(b.metric == "12345人在读" for b in result.books)
    assert result.source_updated_at.utcoffset().total_seconds() == 0
    assert len(http.calls) == 1  # Clear names require no additional public-page requests.


async def test_fanqie_detail_failure_keeps_original_rank_and_does_not_leak_pua(selection):
    state = fanqie_state()
    for row in state["rank"]["book_list"][:2]:
        row["bookName"] = "\ue123字"
        row["author"] = "\ue456"
    http = FakeHTTP({selection.url: ssr(state),
        "https://fanqienovel.com/page/1001": ssr({"page": {"bookId": "1001", "bookName": "公开测试名", "author": "作者甲"}}),
        "https://fanqienovel.com/page/1002": SourceError("unavailable", "详情超时"),
    })
    result = await Fanqie(http).ranking(selection)
    assert result.books[0].title == "公开测试名"
    assert result.books[1].title is None and result.books[1].author is None
    assert result.books[1].metadata_status == "partial"
    assert result.books[2].rank == 3
    assert len(result.books) == 10


async def test_fanqie_wrong_detail_id_not_used(selection):
    state = fanqie_state(1)
    state["rank"]["book_list"][0]["bookName"] = "\ue123"
    http = FakeHTTP({selection.url: ssr(state),
        "https://fanqienovel.com/page/1001": ssr({"page": {"bookId": "9999", "bookName": "错误作品"}})})
    result = await Fanqie(http).ranking(selection)
    assert result.books[0].title is None


@pytest.mark.parametrize("change", ["empty", "category", "rank", "duplicate", "id", "type", "catalog"])
async def test_fanqie_rejects_malformed_or_mismatched_ranking(selection, change):
    state = copy.deepcopy(fanqie_state())
    row = state["rank"]["book_list"][0]
    if change == "empty": state["rank"]["book_list"] = []
    if change == "category": row["curent_category_id"] = 262
    if change == "rank": row["currentPos"] = 2
    if change == "duplicate": row["bookId"] = "1002"
    if change == "id": row["bookId"] = "../../evil"
    if change == "type": state["rank"]["book_list"][0] = None
    if change == "catalog": state["rank"]["rankCategoryTypeList"]["male"][0]["name"] = "错误分类"
    with pytest.raises(SourceError, match="番茄|来源") as caught:
        await Fanqie(FakeHTTP(ssr(state))).ranking(selection)
    assert caught.value.status == "parse_error"


@pytest.mark.parametrize("html", ["<title>空页面</title>", "<script>window.__INITIAL_STATE__=evil();</script>"])
async def test_fanqie_never_executes_non_json_ssr(selection, html):
    with pytest.raises(SourceError):
        await Fanqie(FakeHTTP(html)).ranking(selection)


async def test_jinjiang_gold_section_and_order():
    http = FakeHTTP(jinjiang_page(count=24))
    result = await Jinjiang(http).ranking(validate_selection("jinjiang", "ancient-romance", "gold"))
    assert len(result.books) == 10 and result.books[0].title == "测试作品1"
    assert all(b.metric is None for b in result.books)
    assert http.calls[0][1]["encoding"] == "gb18030"


@pytest.mark.parametrize("old,new", [("收入金榜", "总分榜"), ("古代言情", "现代言情"),
                                      ("novelid=1\"", "novelid=2\"")])
async def test_jinjiang_does_not_substitute_another_board_or_duplicate(old, new):
    with pytest.raises(SourceError):
        await Jinjiang(FakeHTTP(jinjiang_page().replace(old, new))).ranking(
            validate_selection("jinjiang", "ancient-romance", "gold"))


@pytest.fixture
def qidian_month(monkeypatch):
    monkeypatch.setattr("server.app.sources.qidian.current_month", lambda: "202611")


@pytest.mark.parametrize("board,category", [("yuepiao", "21"), ("yuepiao", "all"), ("hotsales", "21"), ("hotsales", "all")])
async def test_qidian_public_mobile_rankings(qidian_month, board, category):
    selection = validate_selection("qidian", category, board)
    http = FakeHTTP(qidian_page(qidian_state(12, board=board, category=category)))
    result = await Qidian(http).ranking(selection)
    assert len(result.books) == 10
    assert [b.rank for b in result.books] == list(range(1, 11))
    assert result.books[0].metric == ("1.23万月票" if board == "yuepiao" else None)
    assert result.books[0].url == "https://m.qidian.com/book/1/"
    assert not result.partial
    assert http.calls[0][0] == selection.url
    assert selection.url.startswith("https://m.qidian.com/rank/")


@pytest.mark.parametrize("value", [None, "乱码", "𘡙𘡘𘡓月票", "10推荐票"])
async def test_qidian_missing_or_unreadable_monthly_votes_are_partial(qidian_month, value):
    state = qidian_state()
    state["pageContext"]["pageProps"]["pageData"]["records"][0]["rankCnt"] = value
    result = await Qidian(FakeHTTP(qidian_page(state))).ranking(validate_selection("qidian", "21", "yuepiao"))
    assert result.partial and result.books[0].metric is None and len(result.books) == 10


@pytest.mark.parametrize("value", ["!undefined", "!NaN", "!Date:2026-11-03T00:00:00.000Z", None, 123])
async def test_qidian_missing_or_non_text_metadata_is_not_displayed(qidian_month, value):
    state = qidian_state()
    row = state["pageContext"]["pageProps"]["pageData"]["records"][0]
    row.update(bName=value, bAuth=value, cat=value, subCat=value)
    result = await Qidian(FakeHTTP(qidian_page(state))).ranking(validate_selection("qidian", "21", "yuepiao"))
    book = result.books[0]
    assert book.title is None and book.author is None and book.genre is None
    assert book.metadata_status == "partial" and book.rank == 1
    assert len(result.books) == 10


async def test_qidian_decodes_escaped_literal_text(qidian_month):
    state = qidian_state()
    row = state["pageContext"]["pageProps"]["pageData"]["records"][0]
    row.update(bName="!!测试作品", bAuth="!!undefined")
    result = await Qidian(FakeHTTP(qidian_page(state))).ranking(validate_selection("qidian", "21", "yuepiao"))
    assert result.books[0].title == "!测试作品"
    assert result.books[0].author == "!undefined"
    assert result.books[0].metadata_status == "complete"


@pytest.mark.parametrize("change", ["site", "gender", "board", "path", "route_category", "route_month", "page",
    "category", "category_name", "month", "month_name", "missing_filter", "duplicate_filter", "filter_index",
    "record_category", "rank", "rank_bool", "duplicate", "id", "empty", "records_type", "row_type", "error", "props"])
async def test_qidian_rejects_wrong_selection_or_malformed_page(qidian_month, change):
    state = qidian_state()
    context = state["pageContext"]
    route = context["routeParams"]
    data = context["pageProps"]["pageData"]
    row = data["records"][0]
    if change == "site": context["mDomain"] = "m.qdmm.com"
    if change == "gender": data["gender"] = "female"
    if change == "board": route["pageType"] = "hotsales"
    if change == "path": context["urlPathname"] = "/rank/yuepiao/"
    if change == "route_category": route["filterParamOne"] = "catid4"
    if change == "route_month": route["filterParamTwo"] = "202610"
    if change == "page": data["pageNum"] = 2
    if change == "category": data["filters"][0]["items"][0]["value"] = 4
    if change == "category_name": data["filters"][0]["items"][0]["text"] = "都市"
    if change == "month": data["filters"][1]["items"][0]["value"] = "202610"
    if change == "month_name": data["filters"][1]["items"][0]["text"] = "10月"
    if change == "missing_filter": data["filters"] = []
    if change == "duplicate_filter": data["filters"].append(data["filters"][0])
    if change == "filter_index": data["filters"][0]["selectedIndex"] = -1
    if change == "record_category": row["catId"] = 4
    if change == "rank": row["rankNum"] = 2
    if change == "rank_bool": row["rankNum"] = True
    if change == "duplicate": row["bid"] = "2"
    if change == "id": row["bid"] = "../secret"
    if change == "empty": data["records"] = []
    if change == "records_type": data["records"] = {}
    if change == "row_type": data["records"][0] = None
    if change == "error": context["errorMsg"] = "upstream failed"
    if change == "props": context["pageProps"] = None
    with pytest.raises(SourceError) as caught:
        await Qidian(FakeHTTP(qidian_page(state))).ranking(validate_selection("qidian", "21", "yuepiao"))
    assert caught.value.status == "parse_error"


@pytest.mark.parametrize("html", ["<html>empty</html>", '<script id="vite-plugin-ssr_pageContext" type="application/json">notJSON()</script>',
                                      qidian_page([]), qidian_page({"pageContext": None})])
async def test_qidian_never_executes_scripts_or_accepts_missing_payload(qidian_month, html):
    with pytest.raises(SourceError):
        await Qidian(FakeHTTP(html)).ranking(validate_selection("qidian", "21", "yuepiao"))


@pytest.mark.parametrize("value", ["\ue123", "\U000f0001", "乱码\ufffd", None, "  "])
def test_corrupted_metadata_is_not_displayed(value):
    assert clean(value) is None
