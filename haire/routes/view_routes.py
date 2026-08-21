from flask import Blueprint, render_template, jsonify, request
# from services.supaDB_service import get_all_evaluations

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

@view_bp.route("/brief")
def brief():
    return render_template("brief.html")

@view_bp.route("/success")
def success():
    return render_template("success.html")

# @view_bp.route("/api/candidates", methods=["GET"])
# def list_candidates():
#     job_title = request.args.get("job_title")
#     try:
#         data = get_all_evaluations(job_title)
#         return jsonify({"success": True, "candidates": data}), 200
#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500