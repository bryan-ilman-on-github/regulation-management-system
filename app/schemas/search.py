from pydantic import BaseModel
from typing import List, Dict, Any


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float


class SearchResponse(BaseModel):
    results: List[SearchResult]
