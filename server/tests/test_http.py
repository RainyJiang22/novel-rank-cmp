import asyncio
import gzip

import httpx
import pytest
from pydantic import ValidationError

from server.app.config import Settings
from server.app.sources.base import SourceError, SourceHTTP

URL = "https://www.jjwxc.net/topten.php?orderstr=12"


def make_http(handler, **settings):
    return SourceHTTP(Settings(source_interval=0, **settings), httpx.AsyncClient(transport=httpx.MockTransport(handler)))


@pytest.mark.parametrize("code,expected", [(202, "blocked"), (403, "blocked"), (429, "blocked"),
                                          (401, "blocked"), (404, "unavailable"), (503, "unavailable")])
async def test_http_status_classification(code, expected):
    http = make_http(lambda _: httpx.Response(code))
    try:
        with pytest.raises(SourceError) as caught:
            await http.get(URL)
        assert caught.value.status == expected
    finally:
        await http.close()


@pytest.mark.parametrize("headers", [{}, {"Content-Encoding": "gzip"}])
async def test_gb18030_gzip_with_and_without_encoding_header(headers):
    html = "<title>收入金榜</title>"
    http = make_http(lambda _: httpx.Response(200, content=gzip.compress(html.encode("gb18030")), headers=headers))
    try:
        assert await http.get(URL, encoding="gb18030") == html
    finally:
        await http.close()


@pytest.mark.parametrize("content,expected", [
    (b"<title>captcha</title>", "blocked"), ("<title>安全验证</title>".encode(), "blocked"),
    (b"\xff\xfe\xff", "parse_error"), (b"", "parse_error"), (b"x" * 2000, "parse_error"),
    (gzip.compress(b"x" * 2000), "parse_error"), (b"\x1f\x8bbroken", "parse_error"),
])
async def test_invalid_empty_challenge_or_oversized_body(content, expected):
    http = make_http(lambda _: httpx.Response(200, content=content), max_response_bytes=1024)
    try:
        with pytest.raises(SourceError) as caught:
            await http.get(URL)
        assert caught.value.status == expected
    finally:
        await http.close()


@pytest.mark.parametrize("target", ["https://evil.test/", "http://127.0.0.1/", "https://www.jjwxc.net/other", "https://user:pass@www.jjwxc.net/"])
async def test_redirects_never_fetch_other_hosts_or_silent_default_boards(target):
    calls = []
    def handler(request):
        calls.append(str(request.url))
        return httpx.Response(302, headers={"location": target})
    http = make_http(handler)
    try:
        with pytest.raises(SourceError):
            await http.get(URL)
        assert calls == [URL]
    finally:
        await http.close()


async def test_unknown_host_rejected_without_network():
    http = make_http(lambda _: pytest.fail("should not fetch"))
    try:
        with pytest.raises(SourceError):
            await http.get("https://evil.test/")
    finally:
        await http.close()


@pytest.mark.parametrize("error", [httpx.ReadTimeout("timeout"), httpx.ConnectError("dns")])
async def test_network_failures(error):
    def handler(_): raise error
    http = make_http(handler)
    try:
        with pytest.raises(SourceError) as caught:
            await http.get(URL)
        assert caught.value.status == "unavailable"
    finally:
        await http.close()


async def test_global_concurrency_and_client_close():
    current = maximum = 0
    async def handler(_):
        nonlocal current, maximum
        current += 1
        maximum = max(maximum, current)
        await asyncio.sleep(0.001)
        current -= 1
        return httpx.Response(200, text="<title>test</title>")
    http = make_http(handler, concurrency=2)
    await asyncio.gather(*(http.get(URL) for _ in range(6)))
    assert maximum == 2
    await http.close()
    assert http.client.is_closed


def test_settings_env_and_invalid_bounds(monkeypatch):
    monkeypatch.setenv("NOVELRANK_CONCURRENCY", "2")
    assert Settings.from_env().concurrency == 2
    with pytest.raises(ValidationError): Settings(concurrency=0)
    with pytest.raises(ValidationError): Settings(cache_ttl=1000, stale_ttl=900)
