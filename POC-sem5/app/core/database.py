from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(settings.DATABASE_URL, settings.DATABASE_API_KEY)

def get_supabase() -> Client:
    return supabase