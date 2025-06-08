import httpx
from app.features.search.repositories import get_stats_from_db, get_image_url

async def search_pokemon(name: str):
    async with httpx.AsyncClient() as client:
        poke_api_url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
        response = await client.get(poke_api_url)
        data = response.json()
        
    
    stats = get_stats_from_db(name)  
    image_url = get_image_url(name)  

    return {
        "name": data["name"],
        "stats": stats,
        "image": image_url
    }
