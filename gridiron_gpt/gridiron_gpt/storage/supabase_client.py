import os

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url:
        raise RuntimeError("SUPABASE_URL is not set.")

    if not key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is not set.")

    return create_client(url, key)
