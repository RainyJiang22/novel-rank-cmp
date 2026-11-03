import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from server.app.catalog import validate_selection
from server.app.config import Settings
from server.app.service import RankingService
from server.app.sources.base import SourceError, SourceResult
from conftest import Adapter


class Clock:
    value = 0.0

    def __call__(self):
        return self.value

    def utcnow(self):
        return datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=self.value)


@pytest.fixture
def setup_service(result):
    clock = Clock()
    adapter = Adapter(result)
    service = RankingService(adapters={"fanqie": adapter}, clock=clock, utcnow=clock.utcnow)
    return service, adapter, clock


async def test_cache_refresh_throttle_and_complete_selection_key(setup_service, selection):
    service, adapter, clock = setup_service
    first = await service.query(selection)
    assert first.status == "ok" and not first.from_cache
    assert (await service.query(selection, refresh=True)).from_cache
    assert adapter.calls == 1
    clock.value = 61
    assert (await service.query(selection)).from_cache
    await service.query(selection, refresh=True)
    assert adapter.calls == 2
    for other in [validate_selection("fanqie", "1_261", "new"), validate_selection("fanqie", "1_262", "reading")]:
        snapshot = await service.query(other)
        assert snapshot.category_id == other.category.id and snapshot.board_id == other.board.id
    assert adapter.calls == 4
    clock.value = 1000
    await service.query(selection)
    assert adapter.calls == 5
    await service.close()


async def test_concurrent_fetches_coalesce_and_waiter_cancellation_is_isolated(setup_service, selection):
    service, adapter, _ = setup_service
    adapter.release = asyncio.Event()
    a = asyncio.create_task(service.query(selection))
    await adapter.started.wait()
    b = asyncio.create_task(service.query(selection))
    await asyncio.sleep(0)
    a.cancel()
    with pytest.raises(asyncio.CancelledError):
        await a
    adapter.release.set()
    assert (await b).status == "ok" and adapter.calls == 1
    await service.close()


@pytest.mark.parametrize("failure", ["blocked", "unavailable", "parse_error"])
async def test_failure_cooldown_stale_snapshot_and_absolute_expiry(setup_service, selection, failure):
    service, adapter, clock = setup_service
    good = await service.query(selection)
    clock.value = 900
    adapter.result = SourceError(failure, "故障注入")
    stale = await service.query(selection)
    assert stale.status == "stale" and stale.failure_reason == failure and stale.from_cache
    assert stale.fetched_at == good.fetched_at and stale.books == good.books
    assert (await service.query(selection, refresh=True)).status == "stale"
    assert adapter.calls == 2
    # A failure just before expiration must not extend the age of the successful data.
    clock.value = 86399
    assert (await service.query(selection)).status == "stale"
    clock.value = 86400
    expired = await service.query(selection)
    assert expired.status == failure and expired.books == () and expired.from_cache
    assert adapter.calls == 3
    await service.close()


async def test_failure_without_cache_is_not_ok_empty_and_can_recover(setup_service, selection, result):
    service, adapter, clock = setup_service
    adapter.result = SourceError("blocked", "上游验证")
    first = await service.query(selection)
    assert first.status == "blocked" and not first.from_cache and not first.books
    assert (await service.query(selection, refresh=True)).from_cache
    assert adapter.calls == 1
    clock.value = 60
    adapter.result = result
    assert (await service.query(selection)).status == "ok"
    await service.close()


async def test_partial_metadata_and_short_result_are_explicit(setup_service, selection, result):
    service, adapter, _ = setup_service
    adapter.result = SourceResult((result.books[0].model_copy(update={"title": None, "metadata_status": "partial"}),))
    snapshot = await service.query(selection)
    assert snapshot.status == "partial" and len(snapshot.books) == 1 and snapshot.books[0].rank == 1
    await service.close()


async def test_parser_cannot_publish_empty_success(setup_service, selection):
    service, adapter, _ = setup_service
    adapter.result = SourceResult(())
    assert (await service.query(selection)).status == "parse_error"
    await service.close()


async def test_unknown_exception_propagates_and_does_not_poison_cache(setup_service, selection, result):
    service, adapter, _ = setup_service
    adapter.result = RuntimeError("bug")
    with pytest.raises(RuntimeError, match="bug"):
        await service.query(selection)
    adapter.result = result
    assert (await service.query(selection)).status == "ok"
    await service.close()


async def test_query_budget_and_shutdown_cancel_work(result, selection):
    adapter = Adapter(result)
    adapter.release = asyncio.Event()
    service = RankingService(Settings(query_timeout=0.01), adapters={"fanqie": adapter})
    assert (await service.query(selection)).status == "unavailable"
    await service.close()
    service = RankingService(adapters={"fanqie": adapter})
    adapter.started.clear()
    task = asyncio.create_task(service.query(selection))
    await adapter.started.wait()
    await service.close()
    with pytest.raises(asyncio.CancelledError):
        await task
    with pytest.raises(RuntimeError, match="closed"):
        await service.query(selection)
