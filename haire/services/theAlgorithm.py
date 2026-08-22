import io, csv, re

class theAlgorithm():
    def __init__(self, personalDetails, candidateCV, requirementsFP, jobTitle):
        self.personalDetails = personalDetails
        self.candidateCV = candidateCV
        self.requirementsFP = requirementsFP
        self.jobTitle = jobTitle
        

    def create_applicant_profile(self, personalDetails,candidateCV):

        #THIS MUST BE PULLED FROM THE AI MODEL
        applicant = {

            "personal_details": personalDetails,

            "cv": candidateCV
        }

        return applicant

    # 2. LOAD REQUIREMENTS FROM CSV

    def get_job_requirements(self,
        csv_file,
        job_title
    ):
        requirements = []

        alias_map = {
            "intermediate life science teacher": "grade 10 - 12 life science teacher",
            "life science teacher": "grade 10 - 12 life science teacher",
            "pub and grill waiter": "a pub and grill waiter",
            "senior accountant": "a senior accountant"
        }

        with open(
            csv_file,
            "r",
            encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)
            target_job = str(job_title or "").strip().lower()
            if target_job in alias_map:
                target_job = alias_map[target_job]

            for row in reader:
                csv_job = str(row.get("job_title", "")).strip().lower()
                is_match = (
                    csv_job == target_job
                    or (target_job and (target_job in csv_job or csv_job in target_job))
                    or ("life science" in target_job and "life science" in csv_job)
                    or ("teacher" in target_job and "teacher" in csv_job)
                    or ("python" in target_job and "python" in csv_job)
                    or ("waiter" in target_job and "waiter" in csv_job)
                    or ("accountant" in target_job and "accountant" in csv_job)
                )

                if is_match:
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

    def normalize_text(self, text):
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

    def get_cv_text(self, applicant):
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
        return self.normalize_text(
            " ".join(text_parts)
        )

    # 5. KEYWORD SIMILARITY

    def calculate_similarity(self,
        keywords,
        candidate_text
    ):
        if not keywords:
            return 0.0
        candidate_text = self.normalize_text(
            candidate_text
        )
        matches = 0
        for keyword in keywords:
            keyword = self.normalize_text(
                keyword
            )
            if keyword in candidate_text:
                matches += 1
        return matches / len(keywords)

    # 6. EVIDENCE STRENGTH

    def calculate_evidence_strength(self,
        similarity
    ):    
        if similarity == 0:
            return 0.0
        elif similarity < 0.25:

            return 0.40

        elif similarity < 0.50:

            return 0.60

        elif similarity < 0.75:
            return 0.90
        else:
            return 1.00

    def calculate_recency(
        self,
        applicant
    ):
        """ 
        Recency is difficult to implement as we are not tracking how recently a candidate got work experience
        """

        return 1

    def calculate_requirement_score(self,
        requirement,
        applicant
    ):
        """
        Calculates the candidate's score for ONE requirement.
        """
        
        cv_text = self.get_cv_text(
            applicant
        )
        similarity = self.calculate_similarity(
            requirement["keywords"],
            cv_text
        )
        evidence = self.calculate_evidence_strength(
            similarity
        )
        recency = self.calculate_recency(
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

    def score_application(self, applicant, requirements):

        total_weight = 0
        total_points = 0

        # Process every requirement
        for requirement in requirements:

            result = self.calculate_requirement_score(
                requirement,
                applicant
            )

            # Add requirement weight
            total_weight += requirement["weight"]

            # Add points earned
            total_points += result["weighted_score"]

        # Calculate final score
        if total_weight == 0:
            final_score = 0
        else:
            final_score = (
                total_points / total_weight
            ) * 100

        # Round to 2 decimal places
        final_score = round(final_score, 2)

        return final_score

    def perform_the_mega_algorithm_of_doom(self):
            # Create applicant profile
        profile = self.create_applicant_profile(
            self.personalDetails,
            self.candidateCV
        )

        # Load requirements for the job
        requirements = self.get_job_requirements(
            self.requirementsFP,
            self.jobTitle
        )

        # Run scoring algorithm
        score = self.score_application(
            profile,
            requirements
        )

        return score
    