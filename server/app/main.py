from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request, Response

from .catalog import CATALOG, validate_selection
from .models import Catalog, Health, RankingSnapshot, SelectionError
from .service import RankingService


def create_app(service: RankingService | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app):
        app.state.rankings = service or RankingService()
        try:
            yield
        finally:
            await app.state.rankings.close()

    app = FastAPI(title="NovelRank API", version="0.1.0", lifespan=lifespan,
                  description="起点、番茄、晋江的公开分类排名；业务状态区分真实数据、缓存、受限和解析失败。")

    @app.get("/health", response_model=Health, tags=["服务"], summary="服务健康检查")
    async def health():
        return Health()

    @app.get("/api/v1/catalog", response_model=Catalog, tags=["榜单"], summary="支持的网站、分类与榜单组合")
    async def catalog():
        return CATALOG

    @app.get("/api/v1/rankings", response_model=RankingSnapshot, tags=["榜单"], summary="查询来源前十名",
             responses={400: {"model": SelectionError, "description": "目录不支持的组合"}})
    async def rankings(
        request: Request, response: Response,
        source: Annotated[str, Query(min_length=1, max_length=32)],
        category: Annotated[str, Query(min_length=1, max_length=64)],
        board: Annotated[str, Query(min_length=1, max_length=32)],
        refresh: bool = False,
    ):
        try:
            selection = validate_selection(source, category, board)
        except ValueError as error:
            raise HTTPException(status_code=400, detail={"code": "INVALID_SELECTION", "message": str(error)}) from None
        response.headers["Cache-Control"] = "no-store"
        return await request.app.state.rankings.query(selection, refresh=refresh)

    return app


app = create_app()
