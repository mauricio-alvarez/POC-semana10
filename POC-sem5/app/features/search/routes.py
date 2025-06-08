from fastapi import APIRouter
from app.features.search.schemas import SearchRequest, SearchResponse
from app.features.search.services import search_pokemon

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    return await search_pokemon(request.Pokemon_Name)
