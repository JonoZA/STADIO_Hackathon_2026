from google import genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google.genai import types
from typing import List, Optional
import time, requests
import json
from io import BytesIO
from pypdf import PdfReader

start_time = time.time()
load_dotenv()
client = genai.Client()
class WorkExperience(BaseModel):
    job_title: str = Field(description="Role or job title held by the candidate")
    company: str = Field(description="Company or organization name")
    duration: str = Field(description="Dates or duration of employment")
    responsibilities: List[str] = Field(description="Key achievements and duties")

class Education(BaseModel):
    degree: str = Field(description="Degree, diploma, or certificate title")
    institution: str = Field(description="School, college, or university name")
    year: Optional[str] = Field(None, description="Graduation year or date range")

class Project(BaseModel):
    title: str = Field(description="Project name")
    description: str = Field(description="Brief summary of the project and technologies used")

# Main schema for the complete review
class CandidateApplicationReview(BaseModel):
    professional_summary: str = Field(
        description="Extracted overview of professional background from the CV"
    )
    work_experience: List[WorkExperience] = Field(
        description="List of prior employment entries"
    )
    skills: List[str] = Field(
        description="List of technical, domain, and soft skills identified"
    )
    education: List[Education] = Field(
        description="Academic background and educational history"
    )
    certification: List[str] = Field(
        description="Professional certifications, licenses, or accreditations"
    )
    projects: List[Project] = Field(
        description="Notable projects or portfolio work mentioned"
    )
    cover_letter: Optional[str] = Field(
        None, description="Extracted content or analysis of the candidate's cover letter"
    )
    personal_summary: str = Field(
        description="AI-generated qualitative assessment of candidate strengths, fit, and potential red flags"
    )
    candidate_summary: str = Field(
        description="High-level executive summary summarizing overall suitability for the target role"
    )


def agent_resume_coverLetter_parser(resumeURL, cover_letter):
    print("Running agent")
    prompt = f"""
        You are an expert HR reviewer. Analyze the candidate's CV and application materials.
        Extract all requested resume details into their respective structured fields, and synthesize
        a comprehensive 'personal_summary' and 'candidate_summary' evaluating their fit.

        Candidate Resume:
        {resumeURL}

        Cover Letter:
        {cover_letter}
        """
    print("Prompt Loaded")
    req = dict(
        model="gemini-3.5-flash",
        input=prompt,
        # remove response_mime_type for now
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": CandidateApplicationReview.model_json_schema(),
        },
    )

    resp = client.interactions.with_raw_response.create(**req)
    # print("HTTP_REQUEST.CONTENT.DECODE-----------------\n\n\n")
    # print(resp.http_request.content.decode())


    # return server response body as a dict
    return resp.http_request.content.decode()

url="https://qfktrunnikcwulzwnlgi.supabase.co/storage/v1/object/public/cv-uploads/d4c5032c-02ca-4919-856b-fdca3cf81716.pdf"
cover_letter = """Dear Hiring Manager,

# I am writing to express my interest in the Life Sciences Teacher position at your school. I am passionate about education and science, and I am eager to contribute to a learning environment where students are encouraged to develop their knowledge, curiosity, and critical-thinking skills.

# I believe that effective Life Sciences education should go beyond memorising concepts. Students should be encouraged to understand how biological principles relate to the world around them, from human health and genetics to ecosystems, biodiversity, and environmental challenges. My approach to teaching focuses on making these concepts engaging, accessible, and relevant to students' everyday lives.

# I am committed to creating a positive and inclusive classroom environment where students feel comfortable asking questions, participating in discussions, and developing confidence in their abilities. I understand the importance of adapting teaching methods to accommodate different learning styles and abilities, while maintaining clear expectations and a strong academic standard.

# In addition to delivering quality lessons, I value the importance of building positive relationships with students, colleagues, and parents. I am organised, enthusiastic, and willing to contribute to the broader school community through extracurricular activities and other initiatives.

I would welcome the opportunity to bring my passion for Life Sciences and education to your school. Thank you for considering my application. I look forward to the opportunity to discuss how my skills and enthusiasm could contribute to your school and its students.
"""
review = agent_resume_coverLetter_parser(url, cover_letter)
print(review)
