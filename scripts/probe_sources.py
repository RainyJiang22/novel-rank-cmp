"""Bounded live smoke test. Never claims that one selection proves the whole site."""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.app.catalog import validate_selection
from server.app.service import RankingService

SELECTIONS = {
    "fanqie": ("1_261", "reading"),
    "jinjiang": ("ancient-romance", "gold"),
    "qidian": ("21", "yuepiao"),
}


async def main(source):
    service = RankingService()
    try:
        for site, (category, board) in SELECTIONS.items():
            if source != "all" and source != site:
                continue
            result = await service.query(validate_selection(site, category, board))
            print(json.dumps({
                "selection": [site, category, board], "status": result.status,
                "count": len(result.books), "missingMetadata": sum(b.metadata_status == "partial" for b in result.books),
                "fetchedAt": result.fetched_at.isoformat(), "sourceUrl": result.source_url,
                "message": result.message,
            }, ensure_ascii=False), flush=True)
    finally:
        await service.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["all", *SELECTIONS], default="all")
    asyncio.run(main(parser.parse_args().source))
