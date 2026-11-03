import copy

import pytest

from server.app.catalog import CATALOG, validate_selection
from server.app.sources.base import SourceError, clean
from server.app.sources.fanqie import Fanqie
from server.app.sources.jinjiang import Jinjiang
from server.app.sources.qidian import Qidian
from server.app.sources.qimao import Qimao
from conftest import FakeHTTP, fanqie_state, jinjiang_page, qidian_page, qimao_page, ssr


def test_catalog_combinations_have_unique_keys_and_fixed_urls():
    keys = set()
    for source in CATALOG.sources:
        for category in source.categories:
            for board in category.board_ids:
                selection = validate_selection(source.id, category.id, board)
                assert selection.key not in keys
                keys.add(selection.key)
                assert selection.url.startswith(source.home_url)
    with pytest.raises(ValueError):
        validate_selection("qimao", "203", "hot-daily")


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


@pytest.mark.parametrize("category,board,gender,period", [
    ("boy", "hot-daily", "男生榜", "日榜"), ("girl", "hot-monthly", "女生榜", "月榜"),
])
async def test_qimao_heat_rankings(category, board, gender, period):
    result = await Qimao(FakeHTTP(qimao_page(gender=gender, period=period, count=12))).ranking(
        validate_selection("qimao", category, board))
    assert len(result.books) == 10
    assert result.books[0].metric == "12.3万热度"


async def test_qimao_category_uses_click_order_without_fabricating_metric():
    result = await Qimao(FakeHTTP(qimao_page(library=True))).ranking(validate_selection("qimao", "203", "category-click"))
    assert len(result.books) == 10 and all(b.metric is None for b in result.books)
    assert result.books[0].genre == "都市高手"
    assert not result.partial


@pytest.mark.parametrize("old,new", [
    ("按点击量", "按更新时间"), (">都市<", ">玄幻奇幻<"),
    ("a-203-220", "a-202-220"), ('num active">1', 'num active">2'),
    ('href="/shuku/1/"', 'href="https://evil.test/shuku/1/"'),
])
async def test_qimao_rejects_wrong_filter_sort_page_or_link(old, new):
    html = qimao_page(library=True).replace(old, new)
    with pytest.raises(SourceError):
        await Qimao(FakeHTTP(html)).ranking(validate_selection("qimao", "203", "category-click"))


async def test_qimao_rejects_wrong_period():
    with pytest.raises(SourceError):
        await Qimao(FakeHTTP(qimao_page())).ranking(validate_selection("qimao", "boy", "hot-monthly"))


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


async def test_qidian_parser_and_font_encoded_metric():
    selection = validate_selection("qidian", "21", "yuepiao")
    result = await Qidian(FakeHTTP(qidian_page())).ranking(selection)
    assert len(result.books) == 10 and result.books[0].metric == "123月票"
    encoded = await Qidian(FakeHTTP(qidian_page().replace("123", "𘡙𘡘𘡓"))).ranking(selection)
    assert encoded.partial and all(b.metric is None for b in encoded.books)


@pytest.mark.parametrize("old,new", [("月票榜", "畅销榜"), ('act">玄幻', 'act">奇幻'),
                                     ('rank-tag">1', 'rank-tag">2')])
async def test_qidian_rejects_wrong_selection_or_rank(old, new):
    with pytest.raises(SourceError):
        await Qidian(FakeHTTP(qidian_page().replace(old, new))).ranking(validate_selection("qidian", "21", "yuepiao"))


@pytest.mark.parametrize("value", ["\ue123", "\U000f0001", "乱码\ufffd", None, "  "])
def test_corrupted_metadata_is_not_displayed(value):
    assert clean(value) is None
