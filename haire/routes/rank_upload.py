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
        # 1. Save raw form data and CV file to Supabase
        result = save_candidate_and_cv(
            form_data=request.form,
            file_bytes=cv_file.read()
        )
        
        # 2. Extract needed info for the AI parser
        resume_url = result.get("cv_file_url")
        cover_letter = request.form.get("coverLetter", "")
        
        # 3. Call the Gemini AI parser
        ai_output = agent_resume_coverLetter_parser(resume_url, cover_letter)
        
        # 4. Prepare data for candidates_ranked table
        ranked_data = {
            "id": result["id"],
            "fullName": result.get("fullName"),
            "email": result.get("email"),
            "cellphone": result.get("cellphone"),
            "address": result.get("address"),
            "gender": result.get("gender"),
            "nationality": result.get("nationality"),
            "job_title": result.get("job_title"),
            "cv_file_url": result.get("cv_file_url"),
            "proffesional_summary": ai_output.get("professional_summary"),
            "work_experience": ai_output.get("work_experience"),
            "skills": ai_output.get("skills"),
            "education": ai_output.get("education"),
            "certification": ai_output.get("certification"),
            "projects": ai_output.get("projects"),
            "cover_letter": ai_output.get("cover_letter"),
            "personal_summary": ai_output.get("personal_summary"),
            "candidate_summary": ai_output.get("candidate_summary")
        }
        
        # 5. Save AI output and duplicate fields to candidates_ranked
        save_ranked_candidate(ranked_data)

        return jsonify({"message": "Application submitted successfully", "data": result}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# # @upload_bp.route("/api/evaluate", methods=["POST"])

# candidate = agent_resume_coverLetter_parser(url, cover_letter)

# 1. CREATE APPLICANT PROFILE

