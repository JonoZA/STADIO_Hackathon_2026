from extensions import supabase

def save_candidate_and_cv(form_data: dict, file_bytes: bytes) -> dict:
    # 1. Insert form fields to get the generated UUID
    insert_res = supabase.table("candidates_raw").insert({
        "fullName": form_data.get("fullName"),
        "cellphone": form_data.get("cellphone"),
        "email": form_data.get("email"),
        "address": form_data.get("address"),
        "gender": form_data.get("gender"),
        "marStatus": form_data.get("marStatus"),
        "transport": form_data.get("transport") == "true" or form_data.get("transport") == "on",
        "nationality": form_data.get("nationality"),
        "job_title": form_data.get("job_title")
    }).execute()

    candidate_id = insert_res.data[0]["id"]
    filename = f"{candidate_id}.pdf"

    # 2. Upload file named <id>.pdf to bucket
    supabase.storage.from_("cv-uploads").upload(
        path=filename,
        file=file_bytes,
        file_options={"content-type": "application/pdf"}
    )

    # 3. Get public URL and update the candidate row
    file_url = supabase.storage.from_("cv-uploads").get_public_url(filename)
    update_res = supabase.table("candidates_raw").update({"cv_file_url": file_url}).eq("id", candidate_id).execute()
    
    return update_res.data[0]

def save_ranked_candidate(ranked_data: dict) -> dict:
    """
    Saves the processed algorithm output to the 'candidates_ranked' table.
    The ranked_data dict should contain the fields required by your Supabase table schema
    (e.g., id, score, top_matches, etc.).
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