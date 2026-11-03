import asyncio
import re
from datetime import datetime, timezone

from ..catalog import Selection
from .base import SourceError, SourceHTTP, SourceResult, clean, initial_state, make_book, numeric_metric, require


class Fanqie:
    def __init__(self, http: SourceHTTP):
        self.http = http

    async def ranking(self, selection: Selection) -> SourceResult:
        state = initial_state(await self.http.get(selection.url))
        rank = state.get("rank")
        require(isinstance(rank, dict))
        rows = rank.get("book_list")
        require(isinstance(rows, list) and rows, "番茄未返回分类排名。")
        gender, genre = selection.category.id.split("_")
        catalog = rank.get("rankCategoryTypeList", {})
        require(isinstance(catalog, dict))
        choices = catalog.get("male" if gender == "1" else "female", [])
        require(isinstance(choices, list) and any(isinstance(c, dict) and str(c.get("id")) == genre
                and c.get("name") == selection.category.name for c in choices), "番茄分类目录不匹配。")
        rows = rows[:10]
        for position, row in enumerate(rows, 1):
            require(isinstance(row, dict))
            require(str(row.get("currentPos")) == str(position), "番茄名次顺序发生变化。")
            require(str(row.get("curent_category_id")) == genre and str(row.get("pos_category_id")) == genre,
                    "番茄返回的排名分类与请求不符。")
            require(re.fullmatch(r"[0-9]+", str(row.get("bookId", ""))), "番茄作品 ID 无效。")
        require(len({str(row["bookId"]) for row in rows}) == len(rows), "番茄返回重复作品。")

        async def resolve(row):
            id_ = str(row["bookId"])
            title, author = clean(row.get("bookName")), clean(row.get("author"))
            if not title or not author:
                try:
                    page = initial_state(await self.http.get(f"https://fanqienovel.com/page/{id_}")).get("page")
                    require(isinstance(page, dict) and str(page.get("bookId")) == id_, "番茄作品详情 ID 不匹配。")
                    title = title or clean(page.get("bookName"))
                    author = author or clean(page.get("author"))
                except SourceError:
                    # Keep the original position and ID; no fabricated title or rank compaction.
                    pass
            return make_book(rank=int(row["currentPos"]), id=id_, title=title, author=author,
                             url=f"https://fanqienovel.com/page/{id_}",
                             metric=numeric_metric(row.get("read_count"), "人在读"),
                             genre=selection.category.name)

        books = tuple(await asyncio.gather(*(resolve(row) for row in rows)))
        updated = None
        version = str(rank.get("rankVersion", ""))
        if re.fullmatch(r"[0-9]{10}", version):
            updated = datetime.fromtimestamp(int(version), tz=timezone.utc)
        return SourceResult(books, updated, partial=any(b.metric is None for b in books)).validate()
