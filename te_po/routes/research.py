from fastapi import APIRouter
from te_po.pipeline.research.search_engine import research_query

router = APIRouter()


@router.post("/research/query")
def research(body: dict):
    return research_query(body["query"], body.get("limit", 10))
