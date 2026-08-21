from google import genai
from pydantic import BaseModel, Field
<<<<<<< HEAD
from extensions import ai_client
from pypdf import PdfReader
=======
from dotenv import load_dotenv
from google.genai import types
import fitz
import time
>>>>>>> 293890e (Created agent, pdf reader, intepretation and output works)

start_time = time.time()
load_dotenv()
cover_letter = """Dear Hiring Manager,

I am writing to express my interest in the Life Sciences Teacher position at your school. I am passionate about education and science, and I am eager to contribute to a learning environment where students are encouraged to develop their knowledge, curiosity, and critical-thinking skills.

I believe that effective Life Sciences education should go beyond memorising concepts. Students should be encouraged to understand how biological principles relate to the world around them, from human health and genetics to ecosystems, biodiversity, and environmental challenges. My approach to teaching focuses on making these concepts engaging, accessible, and relevant to students' everyday lives.

I am committed to creating a positive and inclusive classroom environment where students feel comfortable asking questions, participating in discussions, and developing confidence in their abilities. I understand the importance of adapting teaching methods to accommodate different learning styles and abilities, while maintaining clear expectations and a strong academic standard.

In addition to delivering quality lessons, I value the importance of building positive relationships with students, colleagues, and parents. I am organised, enthusiastic, and willing to contribute to the broader school community through extracurricular activities and other initiatives.

I would welcome the opportunity to bring my passion for Life Sciences and education to your school. Thank you for considering my application. I look forward to the opportunity to discuss how my skills and enthusiasm could contribute to your school and its students.

Yours sincerely,

[Full Name]
[Phone Number]
[Email Address]
"""

life_sciences_teacher_criteria = {

<<<<<<< HEAD
    response = ai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CandidateEvaluation,
            temperature=0.2,
        ),
    )
    return response.parsed.model_dump()



def extract_pdf_text(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join([page.extract_text() or "" for page in reader.pages])
=======
    "life_sciences_knowledge": {
        "description": "Strong knowledge of Life Sciences, including biology, genetics, ecology, human biology and evolution",
        "keywords": [
            "life sciences",
            "biology",
            "genetics",
            "ecology",
            "human biology",
            "evolution",
            "cell biology"
        ],
        "weight": 20,
        "mandatory": True
    },

    "teaching_qualification": {
        "description": "Recognised teaching qualification or education degree",
        "keywords": [
            "PGCE",
            "BEd",
            "Bachelor of Education",
            "teaching qualification",
            "education degree",
            "teacher qualification"
        ],
        "weight": 20,
        "mandatory": True
    },

    "teaching_experience": {
        "description": "Experience teaching Life Sciences, Biology or a closely related subject",
        "keywords": [
            "teaching experience",
            "life sciences teacher",
            "biology teacher",
            "science teacher",
            "classroom experience",
            "teaching"
        ],
        "weight": 15,
        "mandatory": True
    },

    "curriculum_knowledge": {
        "description": "Knowledge and experience of relevant school curriculum and assessment requirements",
        "keywords": [
            "curriculum",
            "CAPS",
            "assessment",
            "lesson planning",
            "curriculum planning",
            "national curriculum"
        ],
        "weight": 10,
        "mandatory": True
    },

    "lesson_planning": {
        "description": "Ability to develop effective and engaging Life Sciences lesson plans",
        "keywords": [
            "lesson planning",
            "lesson plans",
            "teaching materials",
            "learning activities",
            "lesson preparation"
        ],
        "weight": 8,
        "mandatory": False
    },

    "classroom_management": {
        "description": "Strong classroom management and ability to maintain a positive learning environment",
        "keywords": [
            "classroom management",
            "discipline",
            "student behaviour",
            "classroom environment",
            "learner management"
        ],
        "weight": 7,
        "mandatory": False
    },

    "communication": {
        "description": "Excellent verbal and written communication skills",
        "keywords": [
            "communication",
            "verbal communication",
            "written communication",
            "presentation",
            "interpersonal skills"
        ],
        "weight": 5,
        "mandatory": False
    },

    "student_engagement": {
        "description": "Ability to engage students and make Life Sciences interesting and accessible",
        "keywords": [
            "student engagement",
            "learner engagement",
            "interactive learning",
            "student participation",
            "engaging lessons"
        ],
        "weight": 5,
        "mandatory": False
    },

    "practical_science": {
        "description": "Ability to conduct and supervise practical Life Sciences experiments and laboratory activities",
        "keywords": [
            "laboratory",
            "laboratory experiments",
            "practical experiments",
            "science experiments",
            "laboratory safety",
            "practical science"
        ],
        "weight": 5,
        "mandatory": False
    },

    "technology": {
        "description": "Ability to use educational technology and digital tools to support teaching",
        "keywords": [
            "educational technology",
            "technology in education",
            "digital learning",
            "online learning",
            "Microsoft Office",
            "Google Classroom",
            "interactive technology"
        ],
        "weight": 3,
        "mandatory": False
    },

    "teamwork": {
        "description": "Ability to collaborate with teachers, school management, parents and other stakeholders",
        "keywords": [
            "teamwork",
            "collaboration",
            "teachers",
            "parents",
            "school management",
            "staff collaboration"
        ],
        "weight": 2,
        "mandatory": False
    }
}

pdf = fitz.open("Stadio_hackathon_2026/CVs/Anika_Pillay_CV.pdf")
pdfText = ""
for page in pdf:
    pdfText = pdfText + page.get_text()
pdf.close()

knowledge_base= [cover_letter,pdfText, life_sciences_teacher_criteria ]

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.5-flash",
    input=f"""Evaluate candidates and return a personality summary and a summary of how the candidate fits the requirements. Ignore the wieght of a requirement
        resumes: {pdfText}
        Cover Letter: {cover_letter}
        Requirements: {life_sciences_teacher_criteria}
        """
)

print(interaction.output_text)

for i in range(1_000_000):
    x = i*2
end_time = time.time()
print(f"Ran for: {end_time - start_time:.4f} seconds")

# class CandidateEvaluation(BaseModel):
#     candidate_name: str
#     match_score: int = Field(description="Score between 0 and 100 based on job fit")
#     key_strengths: list[str]
#     missing_skills: list[str]
#     summary_verdict: str



# def evaluate_cv_content(cv_text: str, job_description: str) -> dict:
#     prompt = f"""
#     Evaluate the following candidate CV against the job requirements.
    
#     JOB DESCRIPTION:
#     {job_description}
    
#     CANDIDATE CV:
#     {cv_text}
#     """

#     response = ai_client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=prompt,
#         config=types.GenerateContentConfig(
#             response_mime_type="application/json",
#             response_schema=CandidateEvaluation,
#             temperature=0.2,
#         ),
#     )
#     return response.parsed.model_dump()
>>>>>>> 293890e (Created agent, pdf reader, intepretation and output works)
