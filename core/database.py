import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def get_db_client() -> Client:
    """
    Returns the Supabase Client instance.
    Make sure SUPABASE_URL and SUPABASE_KEY are set in the .env file.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be provided in .env")
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def save_to_db(table_name: str, record_data: dict) -> dict:
    """
    Saves a purely structured dict (like a dumped Pydantic model) into Supabase.
    Requires table_name to exist in Supabase.
    """
    try:
        db = get_db_client()
        response = db.table(table_name).insert(record_data).execute()
        return response.data
    except Exception as e:
        print(f"[-] Veritabanı (Supabase) yazma hatası ({table_name}): {str(e)}")
        # Sessizce devam et, hata logunu dönüyor
        return {"error": str(e)}
