from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    Pokemon_Name: str

class SearchResponse(BaseModel):
    name: str
    stats: List[int]
    image: str
