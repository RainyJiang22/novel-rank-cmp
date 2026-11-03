import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from ..catalog import Selection
from .base import SourceHTTP, SourceResult, make_book, numeric_metric, require, text


class Qidian:
    def __init__(self, http: SourceHTTP):
        self.http = http

    async def ranking(self, selection: Selection) -> SourceResult:
        soup = BeautifulSoup(await self.http.get(selection.url), "html.parser")
        board_name = "月票榜" if selection.board.id == "yuepiao" else "畅销榜"
        require(any(board_name in (text(h) or "") for h in soup.select(".rank-header h3, .rank-header h2")),
                "起点榜单标题不匹配。")
        selected = soup.select(".type-list .act, .type-list .active")
        require(any(text(n) == selection.category.name for n in selected), "起点所选分类不匹配。")
        rows = soup.select(".rank-view-list .book-img-text > ul > li")[:10]
        books = []
        for rank, row in enumerate(rows, 1):
            link = row.select_one(".book-mid-info h2 a")
            require(link, "起点作品链接缺失。")
            parsed = urlsplit(urljoin(selection.url, link.get("href", "")))
            match = re.fullmatch(r"/(?:info|book)/([0-9]+)/?", parsed.path)
            require(parsed.scheme in {"http", "https"} and parsed.hostname in {"book.qidian.com", "www.qidian.com"}
                    and match, "起点作品链接格式变化。")
            rank_text = text(row.select_one(".book-img-box .rank-tag"))
            require(rank_text == str(rank), "起点排名顺序发生变化。")
            author = text(row.select_one(".book-mid-info .author .name"))
            genre = " · ".join(filter(None, (text(n) for n in row.select('.book-mid-info .author a:not(.name)'))))
            metric = numeric_metric(text(row.select_one(".book-right-info .total span")), selection.board.metric_label)
            books.append(make_book(rank=rank, id=match[1], title=text(link), author=author,
                                   url=f"https://book.qidian.com/info/{match[1]}/", metric=metric, genre=genre))
        return SourceResult(tuple(books), partial=any(b.metric is None for b in books)).validate()
