# from supabase import create_client, Client
# from config import settings

# class SupabaseService:
#     def __init__(self):
#         self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

#     def save_resume(self, data: dict):
#         return self.supabase.table("resumes").insert(data).execute()

import io
from datetime import datetime
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

BUCKET = "resumes"


def upload_file(content: bytes, storage_path: str, content_type: str) -> str:
    """Upload bytes to Supabase storage. Returns the storage path."""
    supabase.storage.from_(BUCKET).upload(
        path=storage_path,
        file=content,
        file_options={"content-type": content_type}
    )
    return storage_path


def get_signed_url(storage_path: str, expires_in: int = 3600) -> str:
    """Generate a signed URL valid for expires_in seconds (default 1 hour)."""
    result = supabase.storage.from_(BUCKET).create_signed_url(
        storage_path, expires_in
    )
    return result.get("signedURL") or result.get("signedUrl", "")


def save_resume_record(
    filename: str,
    category: str,
    fmt: str,
    storage_path: str,
) -> dict:
    """Insert a resume record into the DB and return the full row."""
    result = supabase.table("resumes").insert({
        "filename":     filename,
        "category":     category,
        "format":       fmt,
        "storage_path": storage_path,
    }).execute()
    return result.data[0]


def list_resumes() -> list[dict]:
    """Return all resumes ordered by most recent first."""
    result = (
        supabase.table("resumes")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data