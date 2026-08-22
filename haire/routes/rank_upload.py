import io, time, csv, re
from flask import Blueprint, request, jsonify
from services.gemini_service import agent_resume_coverLetter_parser
from services.supaDB_service import save_candidate_and_cv, save_ranked_candidate
from services.theAlgorithm import theAlgorithm
from extensions import supabase 


upload_bp = Blueprint("upload_bp", __name__)

@upload_bp.route("/apply", methods=["POST"])
def handle_application():
    cv_file = request.files.get("cv")
    if not cv_file:
        return jsonify({"error": "No CV file provided"}), 400

    try:
        # 1. Upload CV to Supabase storage to get public URL
        file_bytes = cv_file.read()
        cv_file_url = upload_cv_file(file_bytes)

        # 2. Extract needed info for the AI parser
        cover_letter = request.form.get("coverLetter", "")
        
        # 3. Call the Gemini AI parser
        ai_output = agent_resume_coverLetter_parser(cv_file_url, cover_letter)
        
        # 4. Prepare full data for 'candidates_saved' table
        saved_data = {
            "fullName": request.form.get("fullName"),
            "cellphone": request.form.get("cellphone"),
            "email": request.form.get("email"),
            "gender": request.form.get("gender"),
            "nationality": request.form.get("nationality"),
            "cv_file_url": cv_file_url,
            "marStatus": request.form.get("marStatus"),
            "job_title": request.form.get("job_title"),
            "transport": request.form.get("transport") == "true" or request.form.get("transport") == "on",
            "address": request.form.get("address"),
            "professional_summary": ai_output.get("professional_summary"),
            "work_experience": ai_output.get("work_experience"),
            "skills": ai_output.get("skills"),
            "education": ai_output.get("education"),
            "certification": ai_output.get("certification"),
            "projects": ai_output.get("projects"),
            "cover_letter": ai_output.get("cover_letter"),
            "personal_summary": ai_output.get("personal_summary"),
            "candidate_summary": ai_output.get("candidate_summary")
        }

        # 5. Save all raw form + AI fields to 'candidates_saved'
        saved_record = save_candidate_saved(saved_data)
        saved_id = saved_record["id"]

        # ============================================================
        # ALGORITHM: Mega ranking algorithm placeholder
        # Pass candidate data into your algorithm function to compute match_score
        # match_score = mega_algorithm(saved_record)
        # ============================================================
        match_score = 0.0  # Placeholder until ALGORITHM function is connected

        # 6. Prepare data for 'candidates_ranked' table
        ranked_data = {
            "id": saved_id,
            "professional_summary": ai_output.get("professional_summary"),
            "work_experience": ai_output.get("work_experience"),
            "skills": ai_output.get("skills"),
            "education": ai_output.get("education"),
            "certification": ai_output.get("certification"),
            "projects": ai_output.get("projects"),
            "cover_letter": ai_output.get("cover_letter"),
            "personal_summary": ai_output.get("personal_summary"),
            "candidate_summary": ai_output.get("candidate_summary"),
            "match_score": match_score
        }

        # 7. Save AI output + match_score to 'candidates_ranked'
        ranked_record = save_ranked_candidate(ranked_data)

        return jsonify({
            "message": "Application submitted and ranked successfully", 
            "saved_data": saved_record,
            "ranked_data": ranked_record
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# # @upload_bp.route("/api/evaluate", methods=["POST"])

# candidate = agent_resume_coverLetter_parser(url, cover_letter)

# 1. CREATE APPLICANT PROFILE

