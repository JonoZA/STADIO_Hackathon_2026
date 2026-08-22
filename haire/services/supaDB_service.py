import uuid
from extensions import supabase

def sort_candidates_for_display(candidates: list, sort_by: str = "highest-score") -> list:
    """
    Sort candidates for recruiter display.
    """
    records = list(candidates or [])
    if not records:
        return records

    sort_by = (sort_by or "highest-score").strip().lower()

    if sort_by == "alphabetical":
        return sorted(
            records,
            key=lambda candidate: (
                str(candidate.get("full_name") or candidate.get("name") or "").lower(),
                float(candidate.get("match_score") or 0)
            )
        )

    return sorted(
        records,
        key=lambda candidate: (
            float(candidate.get("match_score") or 0),
            str(candidate.get("full_name") or candidate.get("name") or "").lower()
        ),
        reverse=True
    )


def get_all_job_titles() -> list:
    """
    Return a unique list of job titles from candidates_ranked.
    """
    result = supabase.table("candidates_ranked").select("job_title").execute()
    titles = []
    for row in result.data or []:
        title = (row.get("job_title") or "").strip()
        if title and title not in titles:
            titles.append(title)

    return sorted(titles)


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


def get_all_evaluations(job_title: str = None, sort_by: str = "highest-score") -> list:
    """
    Fetch all ranked candidates, merge in saved profile data, and sort for display.
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
        merged["match_score"] = float(merged.get("match_score") or 0)

        raw_skills = merged.get("skills")
        if isinstance(raw_skills, list):
            merged["skill_list"] = raw_skills[:4]
        elif isinstance(raw_skills, str):
            merged["skill_list"] = [
                skill.strip()
                for skill in raw_skills.split(",")
                if skill.strip()
            ][:4]
        else:
            merged["skill_list"] = []

        enriched_candidates.append(merged)

    if job_title and job_title != "all":
        target_job = str(job_title).strip().lower()
        enriched_candidates = [
            candidate
            for candidate in enriched_candidates
            if str(candidate.get("job_title", "")).strip().lower() == target_job
        ]

    return sort_candidates_for_display(enriched_candidates, sort_by)