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
    Fetches all ranked candidates from the 'candidates_ranked' table,
    enriches them with the matching candidate profile from 'candidates_saved',
    and sorts them from highest match_score to lowest.
    """
    ranked_result = supabase.table("candidates_ranked").select("*").execute()
    ranked_candidates = ranked_result.data or []

    enriched_candidates = []

    for candidate in ranked_candidates:
        candidate_id = candidate.get("id")
        saved_record = {}

        if candidate_id:
            saved_result = supabase.table("candidates_saved").select("*").eq("id", candidate_id).execute()
            if saved_result.data:
                saved_record = saved_result.data[0]

        merged = {**saved_record, **candidate}
        merged["full_name"] = merged.get("full_name") or "Unknown Candidate"

        match_score = merged.get("match_score")
        if match_score is None:
            merged["match_score"] = 0.0
        else:
            merged["match_score"] = float(match_score)

        if isinstance(merged.get("skills"), str):
            merged["skill_list"] = [
                skill.strip()
                for skill in merged["skills"].split(",")
                if skill.strip()
            ][:4]
        elif isinstance(merged.get("skills"), list):
            merged["skill_list"] = merged["skills"][:4]
        else:
            merged["skill_list"] = []

        enriched_candidates.append(merged)

    if job_title and job_title != "all":
        job_title = str(job_title).strip().lower()
        enriched_candidates = [
            candidate for candidate in enriched_candidates
            if str(candidate.get("job_title", "")).strip().lower() == job_title
        ]

    return sorted(
        enriched_candidates,
        key=lambda candidate: candidate.get("match_score", 0),
        reverse=True
    )