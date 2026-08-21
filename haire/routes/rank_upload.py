import io, time, csv, re
from flask import Blueprint, request, jsonify
from services.gemini_service import agent_resume_coverLetter_parser
# from services.supaDB_service import save_candidate_and_cv
#from extensions import supabase 


# upload_bp = Blueprint("upload_bp", __name__)

# @upload_bp.route("/apply", methods=["POST"])
# def handle_application():
#     cv_file = request.files.get("cv")
#     if not cv_file:
#         return jsonify({"error": "No CV file provided"}), 400

#     try:
#         result = save_candidate_and_cv(
#             form_data=request.form,
#             file_bytes=cv_file.read()
#         )
#         return jsonify({"message": "Application submitted successfully", "data": result}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

url="https://qfktrunnikcwulzwnlgi.supabase.co/storage/v1/object/public/cv-uploads/d4c5032c-02ca-4919-856b-fdca3cf81716.pdf"
cover_letter = """Dear Hiring Manager,

# I am writing to express my interest in the Life Sciences Teacher position at your school. I am passionate about education and science, and I am eager to contribute to a learning environment where students are encouraged to develop their knowledge, curiosity, and critical-thinking skills.

# I believe that effective Life Sciences education should go beyond memorising concepts. Students should be encouraged to understand how biological principles relate to the world around them, from human health and genetics to ecosystems, biodiversity, and environmental challenges. My approach to teaching focuses on making these concepts engaging, accessible, and relevant to students' everyday lives.

# I am committed to creating a positive and inclusive classroom environment where students feel comfortable asking questions, participating in discussions, and developing confidence in their abilities. I understand the importance of adapting teaching methods to accommodate different learning styles and abilities, while maintaining clear expectations and a strong academic standard.

# In addition to delivering quality lessons, I value the importance of building positive relationships with students, colleagues, and parents. I am organised, enthusiastic, and willing to contribute to the broader school community through extracurricular activities and other initiatives.

I would welcome the opportunity to bring my passion for Life Sciences and education to your school. Thank you for considering my application. I look forward to the opportunity to discuss how my skills and enthusiasm could contribute to your school and its students.
"""
candidate = agent_resume_coverLetter_parser(url, cover_letter)



# @upload_bp.route("/api/evaluate", methods=["POST"])

# 1. CREATE APPLICANT PROFILE

def create_applicant_profile():

    #THIS MUST BE PULLED FROM THE AI MODEL
    applicant = {

        "personal_details": {
            "name": "Anika",
            "surname": "Pillay",
            "gender": "Female",
            "address": "Durban, South Africa",
            "cell": "081 333 4444",
            "email": "anika.pillay@email.co.za",
            "nationality": "South African",
            "transport": "Own vehicle"
        },

        "cv": candidate
    }

    return applicant

# 2. LOAD REQUIREMENTS FROM CSV

def get_job_requirements(
    csv_file,
    job_title
):
    requirements = []

    with open(
        csv_file,
        "r",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["job_title"] == job_title:
                requirement = {
                    "id": row["requirement_id"],
                    "category": row["category"],
                    "description": row["description"],
                    "keywords": [
                        keyword.strip()
                        for keyword
                        in row["keywords"].split("|")
                    ],
                    "weight": float(
                        row["weight"]
                    ),
                    "mandatory":
                        row["mandatory"].lower()
                        == "true",
                    "threshold": float(
                        row["threshold"]
                    )
                }
                requirements.append(
                    requirement
                )

    return requirements

# 3. NORMALISE TEXT

def normalize_text(text):
    text = str(text).lower()
    text = re.sub(
        r"[^a-z0-9\s\-]",
        " ",
        text
    )
    text = re.sub(
        r"\s+",
        " ",
        text
    )
    
    return text.strip()

# 4. EXTRACT ALL CV TEXT

def get_cv_text(applicant):
    cv = applicant.get(
        "cv",
        {}
    )
    text_parts = []
    def extract(value):
        if isinstance(value, dict):
            for item in value.values():
                extract(item)
        elif isinstance(value, list):
            for item in value:
                extract(item)
        else:
            text_parts.append(
                str(value)
            )
    extract(cv)
    return normalize_text(
        " ".join(text_parts)
    )

# 5. KEYWORD SIMILARITY

def calculate_similarity(
    keywords,
    candidate_text
):
    if not keywords:
        return 0.0
    candidate_text = normalize_text(
        candidate_text
    )
    matches = 0
    for keyword in keywords:
        keyword = normalize_text(
            keyword
        )
        if keyword in candidate_text:
            matches += 1
    return matches / len(keywords)


# 6. EVIDENCE STRENGTH

def calculate_evidence_strength(
    similarity
):    
    if similarity == 0:
        return 0.0
    elif similarity < 0.25:
        return 0.60
    elif similarity < 0.50:
        return 0.75
    elif similarity < 0.75:
        return 0.90
    else:
        return 1.00

def calculate_recency(
    applicant
):
    """ 
    Recency is difficult to implement as we are not tracking how recently a candidate got work experience
    """

    return 1


def calculate_requirement_score(
    requirement,
    applicant
):
    """
    Calculates the candidate's score for ONE requirement.
    """
    
    cv_text = get_cv_text(
        applicant
    )
    similarity = calculate_similarity(
        requirement["keywords"],
        cv_text
    )
    evidence = calculate_evidence_strength(
        similarity
    )
    recency = calculate_recency(
        applicant
    )
    match_score = (
        similarity * 0.50 + evidence * 0.30 + recency * 0.20
    )

# Prevent score from exceeding 1
    match_score = min(
        match_score,
        1.0
    )
    
# Apply requirement weight

    weighted_score = (
        match_score * requirement["weight"]
    )

    # Determine whether requirement is met

    requirement_met = match_score >= (requirement.get("threshold", 0.0) * 0.90)
    return {
        "similarity":
            similarity,
        "evidence":
            evidence,
        "recency":
            recency,
        "match":
            match_score,
        "weighted_score":
            weighted_score,
        "met":
            requirement_met
    }


# 9. MAIN SCORING ALGORITHM

def score_application(
    applicant,
    requirements
):
    total_weight = 0
    total_points = 0
    mandatory_failures = []
    requirement_results = []

# Process every requirement

    for requirement in requirements:
        result = calculate_requirement_score(
            requirement,
            applicant
        )
        # Add requirement weight
        total_weight += (
            requirement["weight"]
        )
        # Add points earned
        total_points += (
            result["weighted_score"]
        )

# Check mandatory requirement

        if (
            requirement["mandatory"]
            and
            not result["met"]
        ):
            mandatory_failures.append(
                requirement["id"]
            )

# Save detailed result

        requirement_results.append({
            "id":
                requirement["id"],
            "category":
                requirement["category"],
            "description":
                requirement["description"],
            "weight":
                requirement["weight"],
            "similarity":
                round(
                    result["similarity"],
                    3
                ),
            "evidence":
                round(
                    result["evidence"],
                    3
                ),
            "recency":
                round(
                    result["recency"],
                    3
                ),
            "match":
                round(
                    result["match"] * 100,
                    2
                ),
            "points":
                round(
                    result["weighted_score"],
                    2
                ),
            "mandatory":
                requirement["mandatory"],

            "met":
                result["met"]
        })

# FINAL SCORE

    if total_weight == 0:
        final_score = 0
    else:
        final_score = (
            total_points
            /
            total_weight
        ) * 100

    final_score = round(
        final_score,
        2
    )

# RECOMMENDATION

    if mandatory_failures:
        recommendation = (
            "REVIEW - Mandatory "
            "requirement(s) not met"
        )
    elif final_score >= 85:
        recommendation = (
            "Excellent Candidate"
        )
    elif final_score >= 75:
        recommendation = (
            "Strong Candidate"
        )
    elif final_score >= 65:
        recommendation = (
            "Potential Candidate"
        )
    elif final_score >= 50:
        recommendation = (
            "Weak Candidate"
        )
    else:
        recommendation = (
            "Poor Candidate"
        )

# RETURN RESULT AS DICTIONARY
    
    personal = applicant.get(
        "personal_details",
        {}
    )

    return {

        "candidate": {

            "name":
                personal.get(
                    "name"
                ),

            "surname":
                personal.get(
                    "surname"
                ),

            "email":
                personal.get(
                    "email"
                ),

            "cell":
                personal.get(
                    "cell"
                ),

            "address":
                personal.get(
                    "address"
                ),

            "gender":
                personal.get(
                    "gender"
                ),

            "nationality":
                personal.get(
                    "nationality"
                ),

            "transport":
                personal.get(
                    "transport"
                )
        },

        "score":
            final_score,

        "score_out_of":
            100,

        "recommendation":
            recommendation,

        "total_weight":
            total_weight,

        "total_points":
            round(
                total_points,
                2
            ),

        "mandatory_failures":
            mandatory_failures,

        "requirements":
            requirement_results
    }


# # ============================================================
# # 10. DISPLAY RESULT
# # ============================================================

# def display_result(result):

#     print("=" * 70)

#     print(
#         "CANDIDATE EVALUATION"
#     )

#     print("=" * 70)

#     candidate = result["candidate"]

#     print(
#         f"Candidate: "
#         f"{candidate['name']} "
#         f"{candidate['surname']}"
#     )

#     print(
#         f"Email: "
#         f"{candidate['email']}"
#     )

#     print(
#         f"Cell: "
#         f"{candidate['cell']}"
#     )

#     print(
#         f"\nFinal Score: "
#         f"{result['score']}/100"
#     )

#     print(
#         f"Recommendation: "
#         f"{result['recommendation']}"
#     )

#     print("\n" + "-" * 70)

#     print(
#         "REQUIREMENT BREAKDOWN"
#     )

#     print("-" * 70)

#     for requirement in result["requirements"]:

#         print(
#             f"\n{requirement['id']} - "
#             f"{requirement['description']}"
#         )

#         print(
#             f"Category: "
#             f"{requirement['category']}"
#         )

#         print(
#             f"Weight: "
#             f"{requirement['weight']}"
#         )

#         print(
#             f"Similarity: "
#             f"{requirement['similarity']:.2f}"
#         )

#         print(
#             f"Evidence: "
#             f"{requirement['evidence']:.2f}"
#         )

#         print(
#             f"Recency: "
#             f"{requirement['recency']:.2f}"
#         )

#         print(
#             f"Match: "
#             f"{requirement['match']:.2f}%"
#         )

#         print(
#             f"Points Earned: "
#             f"{requirement['points']:.2f}/"
#             f"{requirement['weight']}"
#         )

#         print(
#             f"Mandatory: "
#             f"{'YES' if requirement['mandatory'] else 'NO'}"
#         )

#         print(
#             f"Requirement Met: "
#             f"{'YES' if requirement['met'] else 'NO'}"
#         )

#     # --------------------------------------------------------
#     # Mandatory failures
#     # --------------------------------------------------------

#     if result["mandatory_failures"]:

#         print(
#             "\n" + "=" * 70
#         )

#         print(
#             "MANDATORY REQUIREMENTS "
#             "REQUIRING REVIEW"
#         )

#         print("=" * 70)

#         for failure in result[
#             "mandatory_failures"
#         ]:

#             print(
#                 f"- {failure}"
#             )

#     else:

#         print(
#             "\nAll mandatory requirements "
#             "were satisfied."
#         )


# # ============================================================
# # 11. MAIN PROGRAM
# # ============================================================

# if __name__ == "__main__":

#     # --------------------------------------------------------
#     # Create applicant
#     # --------------------------------------------------------

#     applicant = create_applicant_profile()

#     # --------------------------------------------------------
#     # Select the job
#     #
#     # This is the ONLY thing you need to change to test
#     # another job.
#     # --------------------------------------------------------

#     selected_job = (
#         "Grade 10 - 12 Life Science Teacher"
#     )

#     # --------------------------------------------------------
#     # Load requirements from CSV
#     # --------------------------------------------------------

#     requirements = get_job_requirements(
#         "../haire/static/data/jobRequirements.csv",
#         selected_job
#     )

#     # --------------------------------------------------------
#     # Check that requirements were found
#     # --------------------------------------------------------

#     if not requirements:

#         print(
#             f"No requirements found for: "
#             f"{selected_job}"
#         )

#     else:

#         # ----------------------------------------------------
#         # Score applicant
#         # ----------------------------------------------------

#         result = score_application(
#             applicant,
#             requirements
#         )

#         # ----------------------------------------------------
#         # Display result
#         # ----------------------------------------------------

#         display_result(
#             result
#         )