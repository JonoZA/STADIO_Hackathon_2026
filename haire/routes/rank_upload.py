import io, time, csv, re
from flask import Blueprint, request, jsonify
from services.gemini_service import agent_resume_coverLetter_parser
from services.supaDB_service import upload_cv_file, save_candidate_saved, save_ranked_candidate
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






# @upload_bp.route("/api/evaluate", methods=["POST"])

# ============================================================
# 1. CREATE APPLICANT PROFILE
# ============================================================

def create_applicant_profile():
    """
    Creates and returns an applicant dictionary.

    For now, this function simply returns an example
    dictionary.
    Later, this could receive information from:
        - A Flask form
        - A database
        - A CV parser
        - An API
        - An AI model
    """

    #THIS MUST BE PULLED FROM THE AI MODEL
    applicant = {

        "personal_details": {

            "name": "Sarah",

            "surname": "Smith",

            "gender": "Female",

            "address": "Cape Town, Western Cape",

            "cell": "082 123 4567",

            "email": "sarah.smith@email.com",

            "nationality": "South African",

            "transport": "Own vehicle"
        },

        "cv": {

            "education": [
                "Bachelor of Education specialising in Life Sciences",
                "Teaching qualification"
            ],

            "experience": [
                "Three years teaching Life Sciences",
                "Grade 10, 11 and 12 teaching experience",
                "Experience with classroom management",
                "Experience with learner assessment"
            ],

            "skills": [
                "Life Sciences",
                "Biology",
                "Genetics",
                "Ecology",
                "Human Biology",
                "Cell Biology",
                "Classroom Management",
                "Lesson Planning",
                "Communication",
                "Student Engagement",
                "Laboratory Experiments",
                "Microsoft Office",
                "Google Classroom",
                "Teamwork"
            ],

            "curriculum": [
                "CAPS curriculum",
                "Curriculum planning",
                "Assessment planning"
            ],

            "projects": [
                "Developed practical Life Sciences laboratory activities"
            ]
        }
    }

    return applicant


# ============================================================
# 2. LOAD REQUIREMENTS FROM CSV
# ============================================================

def get_job_requirements(
    csv_file,
    job_title
):
    """
    Reads the CSV and returns only the requirements
    belonging to the requested job.

    The algorithm does NOT know what the job requirements are.

    They come entirely from the CSV.
    """

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


# ============================================================
# 3. NORMALISE TEXT
# ============================================================

def normalize_text(text):
    """
    Converts text to lowercase and removes
    unnecessary punctuation.
    """

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


# ============================================================
# 4. EXTRACT ALL CV TEXT
# ============================================================

def get_cv_text(applicant):
    """
    Converts the entire CV dictionary into one searchable
    string.

    This is intentionally dynamic.

    It does NOT care whether the CV contains:

        education
        experience
        skills
        projects

    or something completely different.

    Any new CV section will automatically be included.
    """

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


# ============================================================
# 5. KEYWORD SIMILARITY
# ============================================================

def calculate_similarity(
    keywords,
    candidate_text
):
    """
    Determines how many of the requirement's keywords
    appear in the applicant's CV.

    Returns a value from 0 to 1.
    """

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


# ============================================================
# 6. EVIDENCE STRENGTH
# ============================================================

def calculate_evidence_strength(
    similarity
):
    """
    Converts the similarity score into an evidence
    strength score.

    This function is deliberately generic.

    It does not know what the requirement is.
    """

    if similarity == 0:

        return 0.0

    elif similarity < 0.25:

        return 0.40

    elif similarity < 0.50:

        return 0.60

    elif similarity < 0.75:

        return 0.80

    else:

        return 1.00


# ============================================================
# 7. RECENCY SCORE
# ============================================================

def calculate_recency(
    applicant
):
    """
    Placeholder for now.

    Later this can inspect dates in the applicant's
    experience and determine how recent the relevant
    experience is.

    For now, every applicant receives 0.90.
    """

    return 0.90


# ============================================================
# 8. CALCULATE ONE REQUIREMENT
# ============================================================

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

    # --------------------------------------------------------
    # Similarity
    # --------------------------------------------------------

    similarity = calculate_similarity(
        requirement["keywords"],
        cv_text
    )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    evidence = calculate_evidence_strength(
        similarity
    )

    # --------------------------------------------------------
    # Recency
    # --------------------------------------------------------

    recency = calculate_recency(
        applicant
    )

    # --------------------------------------------------------
    # Combine the three factors
    #
    # These percentages are currently the scoring model.
    #
    # Similarity = 60%
    # Evidence   = 25%
    # Recency    = 15%
    # --------------------------------------------------------

    match_score = (

        similarity * 0.60

        +

        evidence * 0.25

        +

        recency * 0.15
    )

    # Prevent score from exceeding 1
    match_score = min(
        match_score,
        1.0
    )

    # --------------------------------------------------------
    # Apply requirement weight
    # --------------------------------------------------------

    weighted_score = (

        match_score
        *
        requirement["weight"]
    )

    # --------------------------------------------------------
    # Determine whether requirement is met
    # --------------------------------------------------------

    requirement_met = (

        match_score
        >=
        requirement["threshold"]
    )

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


# ============================================================
# 9. MAIN SCORING ALGORITHM
# ============================================================

def score_application(
    applicant,
    requirements
):
    """
    Calculates the final weighted candidate score.

    This function is completely independent of the job.

    It can score:

        Life Sciences Teacher
        Python Developer
        Waiter
        Accountant

    or any future job added to the CSV.
    """

    total_weight = 0

    total_points = 0

    mandatory_failures = []

    requirement_results = []

    # --------------------------------------------------------
    # Process every requirement
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # Check mandatory requirement
        # ----------------------------------------------------

        if (
            requirement["mandatory"]
            and
            not result["met"]
        ):

            mandatory_failures.append(
                requirement["id"]
            )

        # ----------------------------------------------------
        # Save detailed result
        # ----------------------------------------------------

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

    # ========================================================
    # FINAL SCORE
    # ========================================================

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

    # ========================================================
    # RECOMMENDATION
    # ========================================================

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

    # ========================================================
    # RETURN RESULT
    # ========================================================

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


# ============================================================
# 10. DISPLAY RESULT
# ============================================================

def display_result(result):

    print("=" * 70)

    print(
        "CANDIDATE EVALUATION"
    )

    print("=" * 70)

    candidate = result["candidate"]

    print(
        f"Candidate: "
        f"{candidate['name']} "
        f"{candidate['surname']}"
    )

    print(
        f"Email: "
        f"{candidate['email']}"
    )

    print(
        f"Cell: "
        f"{candidate['cell']}"
    )

    print(
        f"\nFinal Score: "
        f"{result['score']}/100"
    )

    print(
        f"Recommendation: "
        f"{result['recommendation']}"
    )

    print("\n" + "-" * 70)

    print(
        "REQUIREMENT BREAKDOWN"
    )

    print("-" * 70)

    for requirement in result["requirements"]:

        print(
            f"\n{requirement['id']} - "
            f"{requirement['description']}"
        )

        print(
            f"Category: "
            f"{requirement['category']}"
        )

        print(
            f"Weight: "
            f"{requirement['weight']}"
        )

        print(
            f"Similarity: "
            f"{requirement['similarity']:.2f}"
        )

        print(
            f"Evidence: "
            f"{requirement['evidence']:.2f}"
        )

        print(
            f"Recency: "
            f"{requirement['recency']:.2f}"
        )

        print(
            f"Match: "
            f"{requirement['match']:.2f}%"
        )

        print(
            f"Points Earned: "
            f"{requirement['points']:.2f}/"
            f"{requirement['weight']}"
        )

        print(
            f"Mandatory: "
            f"{'YES' if requirement['mandatory'] else 'NO'}"
        )

        print(
            f"Requirement Met: "
            f"{'YES' if requirement['met'] else 'NO'}"
        )

    # --------------------------------------------------------
    # Mandatory failures
    # --------------------------------------------------------

    if result["mandatory_failures"]:

        print(
            "\n" + "=" * 70
        )

        print(
            "MANDATORY REQUIREMENTS "
            "REQUIRING REVIEW"
        )

        print("=" * 70)

        for failure in result[
            "mandatory_failures"
        ]:

            print(
                f"- {failure}"
            )

    else:

        print(
            "\nAll mandatory requirements "
            "were satisfied."
        )


# ============================================================
# 11. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Create applicant
    # --------------------------------------------------------

    applicant = create_applicant_profile()

    # --------------------------------------------------------
    # Select the job
    #
    # This is the ONLY thing you need to change to test
    # another job.
    # --------------------------------------------------------

    selected_job = (
        "Grade 10 - 12 Life Science Teacher"
    )

    # --------------------------------------------------------
    # Load requirements from CSV
    # --------------------------------------------------------

    requirements = get_job_requirements(
        "job_requirements.csv",
        selected_job
    )

    # --------------------------------------------------------
    # Check that requirements were found
    # --------------------------------------------------------

    if not requirements:

        print(
            f"No requirements found for: "
            f"{selected_job}"
        )

    else:

        # ----------------------------------------------------
        # Score applicant
        # ----------------------------------------------------

        result = score_application(
            applicant,
            requirements
        )

        # ----------------------------------------------------
        # Display result
        # ----------------------------------------------------

        display_result(
            result
        )
  

































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