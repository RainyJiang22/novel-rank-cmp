"""Runs the same curl chain against a real loopback HTTP server with synthetic adapters."""
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx
import uvicorn

from server.app.main import create_app
from server.app.service import RankingService
from server.app.sources.base import SourceError
from conftest import Adapter


def test_curl_chain_generates_actual_http_docs(tmp_path, result):
    service = RankingService(adapters={"fanqie": Adapter(result), "qidian": Adapter(SourceError("blocked", "测试验证页"))})
    server = uvicorn.Server(uvicorn.Config(create_app(service), log_level="error"))
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            try:
                if httpx.get(base + "/health", timeout=0.2).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.02)
        else:
            raise AssertionError("test server did not start")
        root = Path(__file__).resolve().parents[2]
        run = subprocess.run([sys.executable, str(root / "docs/features/rankings/api/rankings/request/rankings.py"),
                              "--base-url", base, "--docs-dir", str(tmp_path),
                              "--evidence-label", "离线合成来源 / 真实 loopback HTTP"],
                             capture_output=True, text=True, timeout=15)
        assert run.returncode == 0, run.stdout + run.stderr
        assert len(list(tmp_path.glob("*.md"))) == 11
        assert "测试作品1" in (tmp_path / "03_rankings.md").read_text()
        assert '"status": "blocked"' in (tmp_path / "10_other_source.md").read_text()
        assert "10/10 PASS" in run.stdout
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        sock.close()
    assert not thread.is_alive()
