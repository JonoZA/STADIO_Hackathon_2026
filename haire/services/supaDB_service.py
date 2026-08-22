import uuid
from extensions import supabase

def upload_cv_file(file_bytes: bytes) -> str:
    """
    Uploads a CV PDF to the 'cv-uploads' Supabase bucket and returns its public URL.
    """
    filename = f"{uuid.uuid4()}.pdf"
    supabase.storage.from_("cv-uploads").upload(
        path=filename,
        file=file_bytes,
        file_options={"content-type": "application/pdf"}
    )
    return supabase.storage.from_("cv-uploads").get_public_url(filename)

def save_candidate_saved(saved_data: dict) -> dict:
    """
    Saves candidate form data + AI parsed CV details to the 'candidates_saved' table.
    """
    insert_res = supabase.table("candidates_saved").insert(saved_data).execute()
    return insert_res.data[0]

def save_ranked_candidate(ranked_data: dict) -> dict:
    """
    Saves the algorithm output and match_score to the 'candidates_ranked' table.
    """
    insert_res = supabase.table("candidates_ranked").insert(ranked_data).execute()
    return insert_res.data[0]

def get_all_evaluations(job_title: str = None) -> list:
    """
    Fetches all ranked candidates from the 'candidates_ranked' table.
    Optionally filters by job_title if provided.
    """
    query = supabase.table("candidates_ranked").select("*")
    
    if job_title and job_title != "all":
        query = query.eq("job_title", job_title)
        
    result = query.execute()
    return result.data