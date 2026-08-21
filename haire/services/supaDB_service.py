import uuid
import re
from extensions import supabase

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

def upload_pdf_to_storage(file_bytes: bytes, filename: str, job_id: str) -> tuple[str, str]:
    clean_name = sanitize_filename(filename)
    unique_id = uuid.uuid4().hex[:8]
    storage_path = f"{sanitize_filename(job_id)}/{unique_id}_{clean_name}"

    supabase.storage.from_("cv-uploads").upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": "application/pdf"}
    )
    file_url = supabase.storage.from_("cv-uploads").get_public_url(storage_path)
    return file_url, storage_path

def save_evaluation_record(record_data: dict) -> dict:
    res = supabase.table("evaluations").insert(record_data).execute()
    return res.data[0] if res.data else {}

def get_all_evaluations(job_title: str = None) -> list:
    query = supabase.table("evaluations").select("*").order("match_score", desc=True)
    if job_title:
        query = query.ilike("job_title", f"%{job_title}%")
    return query.execute().data