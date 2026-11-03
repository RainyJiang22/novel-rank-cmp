from bs4 import BeautifulSoup

from ..catalog import Selection
from .base import SourceHTTP, SourceResult, book_id, make_book, numeric_metric, require, text


class Qimao:
    def __init__(self, http: SourceHTTP):
        self.http = http

    async def ranking(self, selection: Selection) -> SourceResult:
        soup = BeautifulSoup(await self.http.get(selection.url), "html.parser")
        library = selection.board.id == "category-click"
        if library:
            selected = [text(n) for n in soup.select(".cascader-radio-btn.active")]
            require(len(selected) >= 5 and selected[0] == "全部" and selected[1] == selection.category.name
                    and all(label == "全部" for label in selected[2:]), "七猫分类筛选不匹配。")
            require(text(soup.select_one(".tab-inner.active")) == "按点击量", "七猫排序口径发生变化。")
            require(text(soup.select_one(".page-btn.num.active")) == "1", "七猫未返回第一页。")
            rows = soup.select(".qm-cover-text-item")[:10]
        else:
            gender = "男生榜" if selection.category.id == "boy" else "女生榜"
            period = "日榜" if selection.board.id == "hot-daily" else "月榜"
            require(text(soup.select_one(".qm-switch-tab .item.active")) == gender
                    and text(soup.select_one(".child-tabs-item.menu-tab.active")) == "大热榜"
                    and text(soup.select_one(".date-type-tabs .tab.active")) == period,
                    "七猫频段或大热榜周期不匹配。")
            rows = soup.select(".rank-list .rank-list-item")[:10]
        books = []
        for rank, row in enumerate(rows, 1):
            link = row.select_one(".s-tit a" if library else ".s-book-title")
            require(link, "七猫作品链接缺失。")
            id_ = book_id(link.get("href"), selection.url, r"/shuku/([0-9]+)/?")
            author = text(row.select_one(".s-author" if library else '.s-book-info a[href*="/zuozhe/"]'))
            metric = None
            if library:
                genre_node = row.select_one(".s-category")
                require(genre_node and f"/shuku/a-{selection.category.id}-" in genre_node.get("href", ""),
                        "七猫作品分类与所选分类不符。")
                genre = text(genre_node)
            else:
                require(text(row.select_one(".rank-number")) == str(rank), "七猫排名顺序发生变化。")
                value = (text(row.select_one(".rank-num")) or "") + (text(row.select_one(".rank-unit")) or "")
                metric = numeric_metric(value, "热度")
                genre = " · ".join(filter(None, (text(n) for n in row.select('.s-book-info a[href*="/shuku/"]')))) or None
            books.append(make_book(rank=rank, id=id_, title=text(link), author=author,
                                   url=f"https://www.qimao.com/shuku/{id_}/", metric=metric, genre=genre))
        return SourceResult(tuple(books), partial=not library and any(b.metric is None for b in books)).validate()
