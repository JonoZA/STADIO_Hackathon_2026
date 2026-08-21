import os
import uuid
import re
from flask import Flask, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def sanitize_filename(filename: str) -> str:
    # Remove special characters and spaces
    clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return clean

@app.route("/api/upload-cv", methods=["POST"])
def upload_cv():
    cv_file = request.files.get("cv")
    job_id = request.form.get("job_id", "general")

    if not cv_file:
        return jsonify({"error": "No file uploaded"}), 400

    # 1. Read binary content
    file_bytes = cv_file.read()
    
    # 2. Build unique path: <job_id>/<unique_id>_<cleaned_filename>
    clean_name = sanitize_filename(cv_file.filename)
    unique_id = uuid.uuid4().hex[:8]
    storage_path = f"{job_id}/{unique_id}_{clean_name}"

    # 3. Upload to Supabase Storage
    try:
        supabase.storage.from_("cv-uploads").upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": cv_file.content_type or "application/pdf"}
        )
    except Exception as e:
        return jsonify({"error": f"Storage upload failed: {str(e)}"}), 500

    # 4. Get the public file URL
    file_url = supabase.storage.from_("cv-uploads").get_public_url(storage_path)

    # 5. Store reference in evaluations table
    eval_row = supabase.table("evaluations").insert({
        "job_title": job_id,
        "cv_file_url": file_url,
        "cv_storage_path": storage_path
    }).execute()

    return jsonify({
        "message": "File uploaded successfully",
        "file_url": file_url,
        "record_id": eval_row.data[0]["id"]
    })