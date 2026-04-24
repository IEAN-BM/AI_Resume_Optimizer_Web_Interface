# import google.generativeai as genai
# from config import settings

# class GeminiService:
#     def __init__(self):
#         genai.configure(api_key=settings.GEMINI_API_KEY)
#         self.model = genai.GenerativeModel('gemini-pro')

#     async def optimize_resume(self, resume_text: str, job_description: str):
#         prompt = f"Optimize this resume for the following job description:\n\nResume:\n{resume_text}\n\nJob Description:\n{job_description}"
#         response = self.model.generate_content(prompt)
#         return response.text

########################################


import json
from google import genai
from config import GEMINI_API_KEY, MOCK_MODE
from models import AnalyseResponse

if not MOCK_MODE:
    client = genai.Client(api_key=GEMINI_API_KEY)
    MODEL  = "gemini-1.5-flash"


def analyse_resume(resume_text: str, job_description: str) -> AnalyseResponse:
    if MOCK_MODE:
        return AnalyseResponse(
            job_title="Software Engineer",
            match_score=85,
            match_summary="Candidate has strong Python skills but lacks direct experience with cloud deployment.",
            required_skills=["Python", "FastAPI", "PostgreSQL"],
            nice_to_have_skills=["Docker", "AWS", "CI/CD"],
            ats_keywords=["Scalability", "Microservices", "API Design"],
            responsibilities=["Develop backend services", "Optimize database queries"],
            candidate_matching_skills=["Python", "FastAPI"],
            candidate_missing_skills=["PostgreSQL", "Docker"]
        )

    prompt = f"""
You are an expert ATS and recruitment analyst.

Analyze the job description and the candidate's resume below.
Return ONLY a valid JSON object with exactly this structure.
No explanation, no markdown, no code fences — raw JSON only:

{{
  "job_title": "string — the target role title",
  "required_skills": ["skill1", "skill2"],
  "nice_to_have_skills": ["skill1", "skill2"],
  "ats_keywords": ["keyword1", "keyword2"],
  "responsibilities": ["responsibility1", "responsibility2"],
  "candidate_matching_skills": ["skill1", "skill2"],
  "candidate_missing_skills": ["skill1", "skill2"],
  "match_score": integer between 0 and 100,
  "match_summary": "One sentence summary of how well the candidate fits"
}}

Job Description:
{job_description}

Candidate Resume:
{resume_text}
"""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    raw = response.text.strip()

    # Strip markdown fences if Gemini adds them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    return AnalyseResponse(**data)


def optimize_resume(
    resume_text: str,
    job_description: str,
    selected_skills: list[str],
    selected_keywords: list[str],
    selected_responsibilities: list[str],
) -> str:
    if MOCK_MODE:
        return f"OPTIMIZED RESUME (MOCK MODE)\n\nName: John Doe\nRole: Software Engineer\n\nSkills: {', '.join(selected_skills)}\nKeywords: {', '.join(selected_keywords)}\n\nExperience:\n- Rewrote backend services using FastAPI and PostgreSQL to improve performance by 40%.\n- Implemented CI/CD pipelines to streamline deployment."

    focus_blocks = []
    if selected_skills:
        focus_blocks.append(
            "SKILLS & REQUIREMENTS TO EMPHASIZE:\n" +
            "\n".join(f"- {s}" for s in selected_skills)
        )
    if selected_keywords:
        focus_blocks.append(
            "ATS KEYWORDS TO WEAVE IN:\n" +
            "\n".join(f"- {k}" for k in selected_keywords)
        )
    if selected_responsibilities:
        focus_blocks.append(
            "RESPONSIBILITIES TO ALIGN WITH:\n" +
            "\n".join(f"- {r}" for r in selected_responsibilities)
        )

    focus_block = "\n\n".join(focus_blocks)

    prompt = f"""
You are a professional resume writer and ATS optimization expert.

Rewrite the candidate's resume to be perfectly tailored to the target job.

STRICT RULES:
- Keep all information truthful — do NOT invent experience, skills, or credentials
- Naturally weave in the ATS keywords listed below
- Rewrite the professional summary to match the target role
- Emphasize the skills and achievements listed below
- Use strong action verbs and quantify achievements where the original supports it
- Do NOT add metrics or numbers that are not in the original resume
- Output the COMPLETE rewritten resume as clean, readable text
- Maintain all original sections (Education, Experience, etc.)

{focus_block}

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION (for context):
{job_description}
"""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text