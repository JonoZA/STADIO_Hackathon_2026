from flask import Blueprint, render_template, jsonify, request
from services.supaDB_service import get_all_evaluations

view_bp = Blueprint("view_bp", __name__)

@view_bp.route("/")
def home():
    return render_template("index.html")

@view_bp.route("/apply")
def apply():
    return render_template("apply.html")

@view_bp.route("/recruit")
def recruit():
    job_title = request.args.get("job_title")
    candidates = get_all_evaluations(job_title)

    total = len(candidates)
    scores = [float(candidate.get("match_score", 0)) for candidate in candidates]

    stats = {
        "total_applicants": total,
        "average_score": round(sum(scores) / total, 1) if total else 0,
        "highest_score": round(max(scores), 1) if scores else 0,
        "lowest_score": round(min(scores), 1) if scores else 0,
    }

    return render_template("recruit.html", candidates=candidates, stats=stats)

@view_bp.route("/brief")
def brief():
    return render_template("brief.html")

@view_bp.route("/success")
def success():
    return render_template("success.html")