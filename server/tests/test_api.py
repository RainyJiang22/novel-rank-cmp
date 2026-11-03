import pytest
from fastapi.testclient import TestClient

from server.app.main import create_app
from server.app.service import RankingService
from server.app.sources.base import SourceError
from conftest import Adapter

PARAMS = {"source": "fanqie", "category": "1_261", "board": "reading"}


def test_health_catalog_query_cache_refresh_and_lifecycle(result):
    adapter = Adapter(result)
    service = RankingService(adapters={"fanqie": adapter})
    with TestClient(create_app(service)) as client:
        assert client.get("/health").json() == {"status": "ok"}
        catalog = client.get("/api/v1/catalog").json()
        assert len(catalog["sources"]) == 4
        assert "boardIds" in catalog["sources"][0]["categories"][0]
        first = client.get("/api/v1/rankings", params=PARAMS)
        data = first.json()
        assert first.status_code == 200 and data["status"] == "ok"
        assert data["sourceId"] == "fanqie" and not data["fromCache"] and len(data["books"]) == 10
        assert first.headers["cache-control"] == "no-store"
        for extra in [{}, {"refresh": "true"}]:
            cached = client.get("/api/v1/rankings", params=PARAMS | extra).json()
            assert cached["fromCache"] and cached["fetchedAt"] == data["fetchedAt"]
        assert adapter.calls == 1
        schema = client.get("/openapi.json").json()
        assert set(schema["paths"]) == {"/health", "/api/v1/catalog", "/api/v1/rankings"}
    assert service._closed


@pytest.mark.parametrize("params,status", [
    ({}, 422), (PARAMS | {"source": "unknown"}, 400), (PARAMS | {"category": "missing"}, 400),
    ({"source": "qimao", "category": "203", "board": "hot-daily"}, 400),
    (PARAMS | {"refresh": "not-a-bool"}, 422), (PARAMS | {"category": "../../etc/passwd"}, 400),
])
def test_api_rejects_bad_selection_before_network(result, params, status):
    adapter = Adapter(result)
    with TestClient(create_app(RankingService(adapters={"fanqie": adapter}))) as client:
        response = client.get("/api/v1/rankings", params=params)
        assert response.status_code == status
        if status == 400:
            assert response.json()["detail"]["code"] == "INVALID_SELECTION"
        assert adapter.calls == 0


@pytest.mark.parametrize("status", ["blocked", "unavailable", "parse_error"])
def test_upstream_errors_are_explicit_business_states(status):
    with TestClient(create_app(RankingService(adapters={"fanqie": Adapter(SourceError(status, "测试故障"))}))) as client:
        response = client.get("/api/v1/rankings", params=PARAMS)
        assert response.status_code == 200
        assert response.json()["status"] == status and response.json()["books"] == []
        assert response.json()["failureReason"] == status


def test_programming_errors_remain_server_errors():
    with TestClient(create_app(RankingService(adapters={"fanqie": Adapter(RuntimeError("bug"))})),
                    raise_server_exceptions=False) as client:
        response = client.get("/api/v1/rankings", params=PARAMS)
        assert response.status_code == 500
