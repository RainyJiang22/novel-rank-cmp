#!/usr/bin/env python3
"""NovelRank v0.1.0 API 测试链；实际响应自动写入同级 doc/，无需登录。"""
import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit

DEFAULT_DOCS_DIR = Path(__file__).resolve().parent.parent / "doc"
STATES = {"ok", "partial", "stale", "blocked", "unavailable", "parse_error"}


class Curl:
    def __init__(self):
        self.executable = shutil.which("curl.exe" if os.name == "nt" else "curl")
        if not self.executable:
            raise RuntimeError("需要系统 curl（Windows 为 curl.exe）。")

    def request(self, method, url, body=None):
        args = [self.executable, "--silent", "--show-error", "--max-time", "50",
                "--request", method, "--write-out", "\n%{http_code}", url]
        if body is not None:
            args.extend(["--header", "Content-Type: application/json", "--data", json.dumps(body, ensure_ascii=False)])
        response = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", timeout=55)
        if response.returncode:
            raise RuntimeError(f"curl 请求失败：{response.stderr.strip()}")
        raw, code = response.stdout.rsplit("\n", 1)
        return {"status": int(code), "body": raw, "data": json.loads(raw) if raw else None,
                "curl": shlex.join(["curl", *args[1:]])}

    def get(self, url):
        return self.request("GET", url)

    def post(self, url, body):
        return self.request("POST", url, body)

    def delete(self, url):
        return self.request("DELETE", url)


class Chain:
    def __init__(self, args):
        parsed = urlsplit(args.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("base-url 必须是不含凭据、query 或 fragment 的 HTTP(S) 服务地址。")
        self.base = args.base_url.rstrip("/")
        self.docs = Path(args.docs_dir)
        self.docs.mkdir(parents=True, exist_ok=True)
        self.args = args
        self.curl = Curl()
        self.entries = []
        self.time = datetime.now(timezone.utc).isoformat()

    def write_doc(self, filename, path, description, params, response, passed):
        parameter_table = "无。"
        if params:
            descriptions = {"source": "网站 ID，来自目录", "category": "该网站分类 ID，来自目录",
                            "board": "该分类支持的榜单 ID", "refresh": "是否刷新；仍受最短重试间隔约束"}
            rows = ["| 参数 | 类型 | 必填 | 本次值 | 说明 |", "| --- | --- | --- | --- | --- |"]
            for key, value in params.items():
                rows.append(f"| {key} | {'boolean' if key == 'refresh' else 'string'} | {'否' if key == 'refresh' else '是'} | `{value}` | {descriptions[key]} |")
            parameter_table = "\n".join(rows)
        payload = json.dumps(response["data"], ensure_ascii=False, indent=2) if response["data"] is not None else "(empty body)"
        self.docs.joinpath(filename).write_text(
            f"# GET {path}\n\n{description}\n\n"
            f"> 执行时间：{self.time}；环境：{self.args.evidence_label}；结果：{'PASS' if passed else 'FAIL'}。"
            "以下是本次 HTTP 实际响应，仅是运行记录，不能当作当前榜单。\n\n"
            f"## Parameters\n\n{parameter_table}\n\nGET 无请求体。\n\n"
            f"## Response `{response['status']}`\n\n```json\n{payload}\n```\n\n"
            f"## curl\n\n```bash\n{response['curl']}\n```\n", encoding="utf-8")

    def write_link(self):
        rows = ["# rankings - API test link", "", f"Base URL: `{self.base}`", "",
                f"执行时间：{self.time}；环境：{self.args.evidence_label}。无认证，不需要 token。",
                "", "API 契约测试通过不代表所有来源可用；blocked 等业务状态会原样记录。",
                "生成的榜单是运行时快照；稳定契约见 [接口说明](../../../../../api/rankings.md)。", "",
                "| # | Interface | Status | Result | Doc |", "| --- | --- | --- | --- | --- |"]
        for i, path, status, passed, filename in self.entries:
            rows.append(f"| {i} | `GET {path}` | `{status}` | {'PASS' if passed else 'FAIL'} | [{filename}]({filename}) |")
        self.docs.joinpath("00_link.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

    def step(self, name, path, description, *, params=None, expected=200, check=None):
        n = len(self.entries) + 1
        print(f"[{n}] {description}", flush=True)
        url = self.base + path + ("?" + urlencode(params) if params else "")
        response = self.curl.get(url)
        passed = response["status"] == expected
        detail = ""
        if passed and check:
            try:
                check(response["data"])
            except (AssertionError, KeyError, TypeError, ValueError) as error:
                passed, detail = False, str(error)
        filename = f"{n:02d}_{name}.md"
        self.write_doc(filename, path, description, params, response, passed)
        self.entries.append((n, path, response["status"], passed, filename))
        self.write_link()
        if not passed:
            raise RuntimeError(f"步骤 {n} 失败：HTTP {response['status']}，预期 {expected}；{detail}")
        print("PASS", flush=True)
        return response["data"]

    def run(self):
        def health(data): assert data == {"status": "ok"}
        self.step("health", "/health", "检查服务是否运行。", check=health)

        def catalog(data):
            assert {s["id"] for s in data["sources"]} == {"fanqie", "qimao", "qidian", "jinjiang"}
            assert all(s["categories"] and s["boards"] for s in data["sources"])
        directory = self.step("catalog", "/api/v1/catalog", "获取版本化网站、分类和榜单目录。", check=catalog)
        params = {"source": self.args.source, "category": self.args.category, "board": self.args.board}
        assert any(s["id"] == params["source"] and any(c["id"] == params["category"] and params["board"] in c["boardIds"]
                   for c in s["categories"]) for s in directory["sources"]), "指定查询不在目录中"

        def snapshot(data, selection=params):
            assert data["sourceId"] == selection["source"] and data["categoryId"] == selection["category"] and data["boardId"] == selection["board"]
            assert data["status"] in STATES and len(data["books"]) <= 10
            assert datetime.fromisoformat(data["fetchedAt"].replace("Z", "+00:00")).utcoffset().total_seconds() == 0
            assert data["sourceUrl"].startswith("https://")
            assert [b["rank"] for b in data["books"]] == list(range(1, len(data["books"]) + 1))
            if data["status"] in {"ok", "partial", "stale"}: assert data["books"]
            else: assert data["books"] == [] and data["failureReason"] == data["status"]
            if data["status"] == "ok": assert len(data["books"]) == 10

        def first_check(data):
            snapshot(data)
            if not self.args.allow_upstream_failure:
                assert data["status"] in {"ok", "partial"}, "未取得真实排名，检查来源状态或显式使用 --allow-upstream-failure"
        first = self.step("rankings", "/api/v1/rankings", "查询所选分类的前十名，校验业务状态与来源顺序。", params=params, check=first_check)

        def cache(data):
            snapshot(data)
            assert data["fromCache"] and data["fetchedAt"] == first["fetchedAt"] and data["books"] == first["books"]
        self.step("cache", "/api/v1/rankings", "重复查询命中缓存，采集时间与作品顺序不变。", params=params, check=cache)
        self.step("refresh", "/api/v1/rankings", "立即刷新仍遵守 60 秒最短重试间隔。", params=params | {"refresh": "true"}, check=cache)
        self.step("invalid_source", "/api/v1/rankings", "未知网站返回 400。", params=params | {"source": "unknown"}, expected=400)
        self.step("invalid_combination", "/api/v1/rankings", "分类与榜单不兼容时返回 400。",
                  params={"source": "qimao", "category": "203", "board": "hot-daily"}, expected=400)
        self.step("missing", "/api/v1/rankings", "缺少必填参数返回 422。", expected=422)
        self.step("invalid_refresh", "/api/v1/rankings", "刷新参数类型错误返回 422。", params=params | {"refresh": "invalid"}, expected=422)
        other = {"source": "qidian", "category": "21", "board": "yuepiao"}
        self.step("other_source", "/api/v1/rankings", "跨站查询保持独立状态；起点验证页可返回 blocked。",
                  params=other, check=lambda data: snapshot(data, other))
        print(f"API 链路完成：{len(self.entries)}/10 PASS，文档：{self.docs}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--docs-dir", type=Path, default=DEFAULT_DOCS_DIR)
    parser.add_argument("--source", default="fanqie")
    parser.add_argument("--category", default="1_261")
    parser.add_argument("--board", default="reading")
    parser.add_argument("--allow-upstream-failure", action="store_true")
    parser.add_argument("--evidence-label", default="本地服务 / 真实上游")
    args = parser.parse_args()
    try:
        Chain(args).run()
    except (RuntimeError, ValueError, AssertionError, subprocess.SubprocessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
