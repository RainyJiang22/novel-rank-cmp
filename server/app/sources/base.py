import asyncio
import json
import re
import time
import unicodedata
import zlib
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, urlsplit

import httpx
from bs4 import BeautifulSoup

from ..config import Settings
from ..models import Book, Failure

HOSTS = frozenset({"fanqienovel.com", "www.qimao.com", "www.jjwxc.net", "www.qidian.com"})


class SourceError(Exception):
    def __init__(self, status: Failure, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def require(condition, message="来源页面结构或所选分类发生变化。"):
    if not condition:
        raise SourceError("parse_error", message)


def clean(value) -> str | None:
    if not isinstance(value, str):
        return None
    value = " ".join(value.split())
    if not value or "\ufffd" in value or any(unicodedata.category(c) in {"Co", "Cs"} for c in value):
        return None
    return value


def text(node) -> str | None:
    return clean(node.get_text(" ", strip=True)) if node else None


def make_book(*, rank, id, title, author, url, metric=None, genre=None) -> Book:
    title, author = clean(title), clean(author)
    return Book(rank=rank, id=id, title=title, author=author, url=url,
                metric=clean(metric), genre=clean(genre),
                metadata_status="complete" if title and author else "partial")


def numeric_metric(value, unit) -> str | None:
    value = clean(value)
    if value and re.fullmatch(r"[0-9]+(?:[.,][0-9]+)*(?:万|亿)?", value):
        return value + unit
    return None


def initial_state(html: str) -> dict:
    marker = re.search(r"window\.__INITIAL_STATE__\s*=\s*", html)
    require(marker, "来源缺少公开 SSR 状态。")
    try:
        state, _ = json.JSONDecoder().raw_decode(html[marker.end():])
    except (ValueError, RecursionError):
        raise SourceError("parse_error", "来源 SSR 数据不是有效 JSON。") from None
    require(isinstance(state, dict))
    return state


def book_id(href, base_url, pattern) -> str:
    require(isinstance(href, str))
    url = urlsplit(urljoin(base_url, href))
    require(url.scheme in {"http", "https"} and url.hostname == urlsplit(base_url).hostname)
    match = re.fullmatch(pattern, url.path + ("?" + url.query if url.query else ""))
    require(match, "作品链接格式发生变化。")
    return match[1]


@dataclass(frozen=True)
class SourceResult:
    books: tuple[Book, ...]
    source_updated_at: datetime | None = None
    partial: bool = False

    def validate(self):
        require(bool(self.books), "来源没有可验证的排名条目；不视为成功空榜。")
        ranks = [b.rank for b in self.books]
        require(ranks == list(range(1, len(ranks) + 1)), "来源名次缺失、重复或顺序不符。")
        require(len({b.id for b in self.books}) == len(self.books), "来源作品 ID 重复。")
        return self


class SourceHTTP:
    """One pooled client per service; all public URLs and redirects are constrained."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self.client = client or httpx.AsyncClient(
            timeout=settings.request_timeout,
            follow_redirects=False,
            limits=httpx.Limits(max_connections=settings.concurrency),
            headers={"User-Agent": "NovelRank/0.1.0 (+https://github.com/RainyJiang22/novel-rank-cmp)",
                     "Accept": "text/html", "Accept-Encoding": "gzip, deflate"},
        )
        self._semaphore = asyncio.Semaphore(settings.concurrency)
        self._locks = {host: asyncio.Lock() for host in HOSTS}
        self._last_start: dict[str, float] = {}

    async def close(self):
        await self.client.aclose()

    async def get(self, url: str, encoding="utf-8") -> str:
        original = urlsplit(url)
        require(original.scheme == "https" and original.hostname in HOSTS and
                original.port in {None, 443} and not original.username and not original.password,
                "来源 URL 不在允许范围。")
        try:
            # Also bounds queueing, redirects and slow streaming, not just socket reads.
            async with asyncio.timeout(self.settings.request_timeout):
                for _ in range(4):
                    async with self._semaphore:
                        async with self._locks[original.hostname]:
                            wait = self.settings.source_interval - (time.monotonic() - self._last_start.get(original.hostname, 0))
                            if wait > 0:
                                await asyncio.sleep(wait)
                            self._last_start[original.hostname] = time.monotonic()
                        async with self.client.stream("GET", url, follow_redirects=False) as response:
                            if response.status_code in {202, 401, 403, 429}:
                                raise SourceError("blocked", f"来源限制访问（HTTP {response.status_code}），请打开原站查看。")
                            if response.is_redirect:
                                target = urljoin(url, response.headers.get("location", ""))
                                parsed = urlsplit(target)
                                require(parsed.scheme == "https" and parsed.hostname == original.hostname
                                        and parsed.port in {None, 443} and not parsed.username and not parsed.password,
                                        "来源跳转至非允许地址，已停止。")
                                require(parsed.path.rstrip("/") == original.path.rstrip("/") and parsed.query == original.query,
                                        "来源跳转改变了所选榜单，已停止。")
                                url = target
                                continue
                            if response.status_code != 200:
                                raise SourceError("unavailable", f"来源暂不可用（HTTP {response.status_code}）。")
                            body = bytearray()
                            async for chunk in response.aiter_bytes(chunk_size=65536):
                                body.extend(chunk)
                                require(len(body) <= self.settings.max_response_bytes, "来源响应超过大小限制。")
                            return self._decode(bytes(body), encoding)
                raise SourceError("unavailable", "来源重定向次数过多。")
        except (TimeoutError, httpx.TimeoutException):
            raise SourceError("unavailable", "来源请求超时，请稍后重试。") from None
        except httpx.HTTPError:
            raise SourceError("unavailable", "来源网络连接失败。") from None

    def _decode(self, body: bytes, encoding: str) -> str:
        # JJ occasionally returns gzip bytes without Content-Encoding.
        if body.startswith(b"\x1f\x8b"):
            try:
                decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
                body = decoder.decompress(body, self.settings.max_response_bytes + 1)
                require(len(body) <= self.settings.max_response_bytes and decoder.eof,
                        "来源压缩响应无效或超过大小限制。")
            except zlib.error:
                raise SourceError("parse_error", "来源压缩数据无效。") from None
        try:
            html = body.decode(encoding)
        except UnicodeError:
            raise SourceError("parse_error", "来源字符编码发生变化。") from None
        require(bool(html.strip()), "来源响应为空。")
        title = BeautifulSoup(html[:12000], "html.parser").title
        title_text = (text(title) or "").lower()
        if any(marker in title_text for marker in ("验证", "captcha", "access denied", "just a moment")):
            raise SourceError("blocked", "来源要求访问验证，请打开原站查看。")
        if len(html) < 2000 and re.search(r"captcha|security.?check|访问验证|访问过于频繁", html, re.I):
            raise SourceError("blocked", "来源要求访问验证，请打开原站查看。")
        return html
