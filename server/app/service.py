import asyncio
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from .catalog import Selection
from .config import Settings
from .models import RankingSnapshot
from .sources.base import SourceError, SourceHTTP
from .sources.fanqie import Fanqie
from .sources.jinjiang import Jinjiang
from .sources.qidian import Qidian


@dataclass(frozen=True)
class Entry:
    snapshot: RankingSnapshot
    saved_at: float


class RankingService:
    def __init__(self, settings: Settings | None = None, *, adapters=None, http=None,
                 clock=time.monotonic, utcnow=None):
        self.settings = settings or Settings.from_env()
        self.http = http
        if adapters is None:
            self.http = http or SourceHTTP(self.settings)
            adapters = {"fanqie": Fanqie(self.http),
                        "jinjiang": Jinjiang(self.http), "qidian": Qidian(self.http)}
        self.adapters = adapters
        self.clock = clock
        self.utcnow = utcnow or (lambda: datetime.now(timezone.utc))
        self._success: dict[tuple, Entry] = {}
        self._attempt: dict[tuple, Entry] = {}
        self._inflight: dict[tuple, asyncio.Task] = {}
        self._closed = False

    async def query(self, selection: Selection, refresh=False) -> RankingSnapshot:
        if self._closed:
            raise RuntimeError("RankingService is closed")
        now, key = self.clock(), selection.key
        # The catalog bounds the number of keys; prune expired payloads as well.
        self._success = {k: e for k, e in self._success.items() if now - e.saved_at < self.settings.stale_ttl}
        self._attempt = {k: e for k, e in self._attempt.items() if now - e.saved_at < self.settings.retry_interval}
        if key in self._attempt:
            return self._render(self._attempt[key].snapshot, key, cached=True)
        success = self._success.get(key)
        if success and now - success.saved_at < self.settings.cache_ttl and not refresh:
            return success.snapshot.model_copy(update={"from_cache": True})
        task = self._inflight.get(key)
        if task is None:
            task = asyncio.create_task(self._fetch(selection))
            self._inflight[key] = task
            task.add_done_callback(lambda done: self._finished(key, done))
        # One caller disconnecting must not cancel a shared fetch for all callers.
        return await asyncio.shield(task)

    def _finished(self, key, task):
        if self._inflight.get(key) is task:
            self._inflight.pop(key)
        if not task.cancelled():
            task.exception()  # Retrieve failures even if every waiter disconnected.

    async def _fetch(self, selection):
        try:
            async with asyncio.timeout(self.settings.query_timeout):
                result = (await self.adapters[selection.source.id].ranking(selection)).validate()
            partial = result.partial or len(result.books) < 10 or any(b.metadata_status == "partial" for b in result.books)
            snapshot = RankingSnapshot(
                source_id=selection.source.id, category_id=selection.category.id, board_id=selection.board.id,
                source_url=selection.url, fetched_at=self.utcnow(), source_updated_at=result.source_updated_at,
                books=result.books, status="partial" if partial else "ok",
                message=f"已获取 {len(result.books)}/10 条；部分名次或元数据不足。" if partial else "已获取来源前十名。",
            )
            self._success[selection.key] = Entry(snapshot, self.clock())
        except (SourceError, TimeoutError) as error:
            status = error.status if isinstance(error, SourceError) else "unavailable"
            message = error.message if isinstance(error, SourceError) else "本次榜单查询超时，请稍后重试。"
            snapshot = RankingSnapshot(
                source_id=selection.source.id, category_id=selection.category.id, board_id=selection.board.id,
                source_url=selection.url, fetched_at=self.utcnow(), status=status, failure_reason=status, message=message,
            )
        # Unexpected exceptions propagate as 500 and are not cached as source outages.
        self._attempt[selection.key] = Entry(snapshot, self.clock())
        return self._render(snapshot, selection.key, cached=False)

    def _render(self, snapshot, key, *, cached):
        if snapshot.failure_reason:
            success = self._success.get(key)
            if success and self.clock() - success.saved_at < self.settings.stale_ttl:
                return success.snapshot.model_copy(update={
                    "status": "stale", "message": f"{snapshot.message} 正在展示旧快照。",
                    "failure_reason": snapshot.failure_reason, "from_cache": True,
                })
        return snapshot.model_copy(update={"from_cache": cached})

    async def close(self):
        self._closed = True
        tasks = tuple(self._inflight.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._inflight.clear()
        self._attempt.clear()
        self._success.clear()
        if self.http is not None:
            await self.http.close()
