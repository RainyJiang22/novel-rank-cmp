from bs4 import BeautifulSoup

from ..catalog import Selection
from .base import SourceHTTP, SourceResult, book_id, make_book, require, text


class Jinjiang:
    def __init__(self, http: SourceHTTP):
        self.http = http

    async def ranking(self, selection: Selection) -> SourceResult:
        soup = BeautifulSoup(await self.http.get(selection.url, encoding="gb18030"), "html.parser")
        require("收入金榜" in (text(soup.title) or ""), "晋江返回的榜单不是收入金榜。")
        groups = [box for box in soup.select(".wrapper.box_06")
                  if text(box.find("h5", recursive=False)) == selection.category.name]
        require(len(groups) == 1, "晋江分类收入金榜分组缺失或不唯一。")
        books = []
        for rank, row in enumerate(groups[0].select("ul.list_01 > li")[:10], 1):
            link = row.select_one('a[href*="onebook.php?novelid="]')
            require(link, "晋江排名中的作品链接缺失。")
            id_ = book_id(link.get("href"), selection.url, r"/onebook\.php\?novelid=([0-9]+)")
            author = row.select_one('a[href*="oneauthor.php?authorid="]')
            books.append(make_book(rank=rank, id=id_, title=link.get("title") or text(link),
                                   author=text(author), url=f"https://www.jjwxc.net/onebook.php?novelid={id_}",
                                   genre=selection.category.name))
        return SourceResult(tuple(books)).validate()
