from flask import Blueprint, render_template, jsonify, request
from services.supaDB_service import get_all_evaluations, get_all_job_titles

view_bp = Blueprint("view_bp", __name__)

@view_bp.route("/")
def home():
    return render_template("index.html")

@view_bp.route("/apply")
def apply():
    return render_template("apply.html")

@view_bp.route("/recruit")
def recruit():
    return render_template("recruit.html")

@view_bp.route("/api/candidates", methods=["GET"])
def list_candidates():
    job_title = request.args.get("job_title", "all")
    sort_by = request.args.get("sort_by", "highest-score")

    try:
        candidates = get_all_evaluations(job_title=job_title, sort_by=sort_by)
        return jsonify({
            "success": True,
            "candidates": candidates,
            "job_titles": get_all_job_titles()
        }), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

@view_bp.route("/brief")
def brief():
    return render_template("brief.html")

@view_bp.route("/success")
def success():
    return render_template("success.html")