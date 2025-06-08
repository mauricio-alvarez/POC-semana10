'''from app.core.database import get_supabase

def get_stats_from_db(pokemon_name: str):
    supabase = get_supabase()
    
    response = supabase.table("stats").select("*").ilike("Name", pokemon_name.lower()).execute()

    if response.data:
        record = response.data[0]

        return [
            record.get("HP"),
            record.get("Attack"),
            record.get("Defense"),
            record.get("Sp. Atk"),
            record.get("Sp. Def"),
            record.get("Speed")
        ]
    else:
        return []  # Or raise an exception
    
def get_image_url(pokemon_name: str):
    return f"http://localhost:8000/images/{pokemon_name.lower()}/0.jpg"





------
'''
# Updated pokemon service functions with logging
from app.core.database import get_supabase
from app.core.logging_config import get_logger, log_execution_time
import time

# Get logger for this module
logger = get_logger("pokemon_stats")

@log_execution_time(logger)
def get_stats_from_db(pokemon_name: str):
    """Get Pokemon stats from database with logging"""
    logger.info(f"Fetching stats for Pokemon: {pokemon_name}")
    
    supabase = get_supabase()
    search_name = pokemon_name.lower()
    
    try:
        # Log database query start
        logger.info(f"Executing database query for: {search_name}")
        response = supabase.table("stats").select("*").ilike("Name", search_name).execute()
        
        if response.data:
            record = response.data[0]
            stats = [
                record.get("HP"),
                record.get("Attack"),
                record.get("Defense"),
                record.get("Sp. Atk"),
                record.get("Sp. Def"),
                record.get("Speed")
            ]
            logger.info(f"Successfully retrieved stats for {pokemon_name}: {stats}")
            return stats
        else:
            logger.warning(f"No stats found for Pokemon: {pokemon_name}")
            return []
            
    except Exception as e:
        logger.error(f"Database error while fetching stats for {pokemon_name}: {str(e)}")
        raise

@log_execution_time(logger)
def get_image_url(pokemon_name: str, base_url: str = "http://localhost:8000"):
    """Generate image URL with logging"""
    logger.info(f"Generating image URL for Pokemon: {pokemon_name}")
    url = f"{base_url}/images/{pokemon_name.lower()}/0.jpg"
    logger.info(f"Generated image URL: {url}")
    return url

