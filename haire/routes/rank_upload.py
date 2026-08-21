import io
from flask import Blueprint, request, jsonify
from pypdf import PdfReader
from services.gemini_service import evaluate_cv_content
from services.supadb_service import upload_pdf_to_storage, save_evaluation_record

upload_bp = Blueprint("upload_bp", __name__)

def extract_pdf_text(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join([page.extract_text() or "" for page in reader.pages])

@upload_bp.route("/api/evaluate", methods=["POST"])
def evaluate_cv():
    # this is where the ALGORITHM GOES!!!!!!
    
    return "EPIC ALGORITHM"

































    # cv_file = request.files.get("cv")
    # job_description = request.form.get("job_description")
    # job_title = request.form.get("job_title", "General Role")

    # if not cv_file or not job_description:
    #     return jsonify({"error": "Missing CV file or job description"}), 400

    # try:
    #     file_bytes = cv_file.read()
        
    #     # 1. Upload to Supabase Storage
    #     file_url, storage_path = upload_pdf_to_storage(file_bytes, cv_file.filename or "cv.pdf", job_title)
        
    #     # 2. Extract PDF Text
    #     cv_text = extract_pdf_text(file_bytes)
        
    #     # 3. AI Evaluation
    #     eval_data = evaluate_cv_content(cv_text, job_description)
        
    #     # 4. Save to Database
    #     db_record = {
    #         "candidate_name": eval_data["candidate_name"],
    #         "job_title": job_title,
    #         "match_score": eval_data["match_score"],
    #         "evaluation_json": eval_data,
    #         "cv_file_url": file_url,
    #         "cv_storage_path": storage_path,
    #     }
    #     saved_record = save_evaluation_record(db_record)

    #     return jsonify({"success": True, "evaluation": eval_data, "record": saved_record}), 201

    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500