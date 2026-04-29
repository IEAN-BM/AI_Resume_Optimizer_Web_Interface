"""
Resume Optimizer
================
Run from command line:
    python resume_optimizer.py                  # opens in browser, local only
    python resume_optimizer.py --share          # opens with public Gradio link
    python resume_optimizer.py --port 8080      # custom port

Import as a library:
    from resume_optimizer import build_app
    app = build_app(base_dir="my/custom/path")
    app.launch()
"""
###########################################
# !pip install gradio openai pypdf2 fpdf2 requests -q <= Run in command line
import argparse
import json
import os
from datetime import datetime
import gradio as gr


# ── Config ────────────────────────────────────────────────────────────────────

DEFAULT_BASE_DIR = os.path.join(os.path.expanduser("~"), "AI_Resume_Optimizer", "resumes")

CATEGORIES = [
    "ML Engineer",
    "Data Scientist",
    "AI Engineer",
    "Computer Vision",
    "Software Engineer",
    "Biomedical Science",
    "Arts & Literature",
    "Others",
]


import openai # Changed from google.generativeai as genai

client = None # Global variable to hold OpenAI client instance

def set_api_key(api_key):
  global client
  if not api_key.strip():
    client = None
    return "⚠️ Please enter a valid API key."
  try:
    client = openai.OpenAI(api_key=api_key.strip())
    # A simple call to check if the key is valid
    client.models.list()
    return "✅ OpenAI API key set successfully!"
  except Exception as e:
    client = None
    return f"❌ Error: {e}\n\nPlease check your key and ensure it has access to OpenAI models."


from fpdf import FPDF
import requests

# ── Resume text extractor ─────────────────────────────────────────────────────
def extract_resume_text(pasted_text, uploaded_file):
    if uploaded_file is not None:
        filepath = uploaded_file.name if hasattr(uploaded_file, "name") else uploaded_file
        ext = os.path.splitext(filepath)[-1].lower()
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip(), None
        elif ext == ".pdf":
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(filepath)
                text = "\n".join(
                    page.extract_text() for page in reader.pages if page.extract_text()
                )
                if not text.strip():
                    return None, "⚠️ PDF appears to be image-based and could not be read as text."
                return text.strip(), None
            except Exception as e:
                return None, f"❌ Error reading PDF: {e}"
        else:
            return None, "⚠️ Unsupported file type. Please upload a .txt or .pdf file."
    if pasted_text and pasted_text.strip():
        return pasted_text.strip(), None
    return None, "⚠️ Please paste your resume or upload a file."


# ── Step 1: Analyse JD and resume ────────────────────────────────────────────
def analyse(pasted_resume, uploaded_resume, job_description):
    global client # Using global client for OpenAI
    if client is None: # Check if client is initialized
        empty = (
            gr.CheckboxGroup(choices=[], value=[]),
            gr.CheckboxGroup(choices=[], value=[]),
            gr.CheckboxGroup(choices=[], value=[]),
        )
        return ("⚠️ Please set your OpenAI API key first.", *empty)

    resume_text, error = extract_resume_text(pasted_resume, uploaded_resume)
    if error:
        return error, gr.CheckboxGroup(choices=[], value=[]), gr.CheckboxGroup(choices=[], value=[]), gr.CheckboxGroup(choices=[], value=[])

    if not job_description.strip():
        return "⚠️ Please paste a job description.", gr.CheckboxGroup(choices=[], value=[]), gr.CheckboxGroup(choices=[], value=[]), gr.CheckboxGroup(choices=[], value=[])

    analysis_prompt = f"""
You are a expert ATS and recruitment analyst.

Analyze the job description and the candidate's resume below.
Return ONLY a valid JSON object with exactly this structure — no explanation, no markdown, no code fences:

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

    try:
        response = client.chat.completions.create(
            model="gpt-4o", # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a expert ATS and recruitment analyst. Return ONLY a valid JSON object with exactly this structure — no explanation, no markdown, no code fences."},
                {"role": "user", "content": analysis_prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if LLM adds them anyway
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)

        # Build readable analysis summary
        match_score = data.get("match_score", 0)
        match_summary = data.get("match_summary", "")
        job_title = data.get("job_title", "Target Role")
        matching = data.get("candidate_matching_skills", [])
        missing = data.get("candidate_missing_skills", [])

        score_bar = "█" * (match_score // 10) + "░" * (10 - match_score // 10)

        summary_text = f"""🎯 Target Role: {job_title}

📊 Match Score: {match_score}/100
{score_bar}

{match_summary}

✅ Skills you already have ({len(matching)}):
{chr(10).join(f"  • {s}" for s in matching) if matching else "  None detected"}

❌ Skills gaps ({len(missing)}):
{chr(10).join(f"  • {s}" for s in missing) if missing else "  None — great fit!"}
"""

        all_skills = list(dict.fromkeys(
            data.get("required_skills", []) + data.get("nice_to_have_skills", [])
        ))
        ats_keywords = data.get("ats_keywords", [])
        responsibilities = data.get("responsibilities", [])

        return (
            summary_text,
            gr.CheckboxGroup(choices=all_skills, value=all_skills, label="Skills & Requirements"),
            gr.CheckboxGroup(choices=ats_keywords, value=ats_keywords, label="ATS Keywords"),
            gr.CheckboxGroup(choices=responsibilities, value=responsibilities, label="Key Responsibilities"),
        )

    except json.JSONDecodeError as e:
        return (
            f"❌ Failed to parse analysis response. Raw output:\n\n{raw}\n\nError: {e}",
            gr.CheckboxGroup(choices=[], value=[]),
            gr.CheckboxGroup(choices=[], value=[]),
            gr.CheckboxGroup(choices=[], value=[]),
        )
    except Exception as e:
        return (
            f"❌ Error during analysis: {e}",
            gr.CheckboxGroup(choices=[], value=[]),
            gr.CheckboxGroup(choices=[], value=[]),
            gr.CheckboxGroup(choices=[], value=[]),
        )


# ── Step 2: Optimize resume with selected skills ──────────────────────────────
def optimize_resume(pasted_resume, uploaded_resume, job_description,
                    selected_skills, selected_keywords, selected_responsibilities):

    global client # Using global client for OpenAI
    if client is None: # Check if client is initialized
        return "⚠️ Please set your OpenAI API key first."

    resume_text, error = extract_resume_text(pasted_resume, uploaded_resume)
    if error:
        return error

    if not job_description.strip():
        return "⚠️ Please paste a job description."

    if not selected_skills and not selected_keywords and not selected_responsibilities:
        return "⚠️ Please run Analyse first, then select at least one skill or keyword to optimize for."

    selected_focus = []
    if selected_skills:
        selected_focus.append("SKILLS & REQUIREMENTS TO EMPHASIZE:\n" + "\n".join(f"- {s}" for s in selected_skills))
    if selected_keywords:
        selected_focus.append("ATS KEYWORDS TO WEAVE IN:\n" + "\n".join(f"- {k}" for k in selected_keywords))
    if selected_responsibilities:
        selected_focus.append("RESPONSIBILITIES TO ALIGN WITH:\n" + "\n".join(f"- {r}" for r in selected_responsibilities))

    focus_block = "\n\n".join(selected_focus)

    rewrite_prompt = f"""
You are a professional resume writer and ATS optimization expert.

Rewrite the candidate's resume to be perfectly tailored to the target job.

STRICT RULES:
- Keep all information truthful — do NOT invent experience, skills, or credentials
- Naturally weave in the ATS keywords listed below
- Rewrite the professional summary to match the target role
- Emphasize the skills and achievements listed below
- Use strong action verbs and quantify achievements where the original resume supports it
- Do NOT add metrics or numbers that are not in the original resume
- Output the COMPLETE rewritten resume as clean, readable text
- Maintain all original sections (Education, Experience, etc.)

{focus_block}

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION (for context):
{job_description}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o", # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a professional resume writer and ATS optimization expert."},
                {"role": "user", "content": rewrite_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error optimizing resume: {e}"


# ── Save and view ─────────────────────────────────────────────────────────────
def save_resume(optimized_resume, category):
    if not optimized_resume.strip():
        return "⚠️ No optimized resume to save. Run Optimize Resume first."
    category_folder = os.path.join(BASE_DIR, category.replace(" ", "_"))
    os.makedirs(category_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{category.replace(' ', '_')}.txt"
    filepath = os.path.join(category_folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(optimized_resume)
    return f"✅ Resume saved to:\n{filepath}"


def view_saved_resumes():
    if not os.path.exists(BASE_DIR):
        return "⚠️ No resumes saved yet."
    lines = []
    total = 0
    for category in CATEGORIES:
        folder = os.path.join(BASE_DIR, category.replace(" ", "_"))
        if not os.path.exists(folder):
            continue
        files = sorted([f for f in os.listdir(folder) if f.endswith(".txt")], reverse=True)
        if not files:
            continue
        lines.append(f"📁 {category} ({len(files)} file{'s' if len(files) != 1 else ''})")
        for fname in files:
            try:
                dt = datetime.strptime(fname[:15], "%Y%m%d_%H%M%S")
                readable_date = dt.strftime("%b %d, %Y at %H:%M:%S")
            except ValueError:
                readable_date = "Unknown date"
            lines.append(f"   • {fname}  —  {readable_date}")
        total += len(files)
    if not lines:
        return "📭 No saved resumes found yet."
    lines.insert(0, f"📊 {total} total saved resume{'s' if total != 1 else ''}\n")
    return "\n".join(lines)


# ── PDF Generator ────────────────────────────────────────────────────────────
def save_resume_pdf(optimized_resume, category):
    if not optimized_resume.strip():
        return "⚠️ No optimized resume to save. Run Optimize Resume first."

    category_folder = os.path.join(BASE_DIR, category.replace(" ", "_"))
    os.makedirs(category_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{category.replace(' ', '_')}.pdf"
    filepath = os.path.join(category_folder, filename)

    # ── Constants ─────────────────────────────────────────────────────────────
    ACCENT       = (44, 62, 122)
    BLACK        = (30, 30, 30)
    LIGHT_GRAY   = (120, 120, 120)
    PAGE_W       = 210
    MARGIN       = 18
    CONTENT_W    = PAGE_W - 2 * MARGIN

    class ResumePDF(FPDF):
        def footer(self):
            self.set_y(-12)
            self.set_font("DejaVu", size=8)
            self.set_text_color(*LIGHT_GRAY)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = ResumePDF(format="A4")
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Load fonts ────────────────────────────────────────────────────────────
    pdf.add_font("DejaVu", fname="DejaVuSansCondensed.ttf")
    pdf.add_font("DejaVu", style="B", fname="DejaVuSansCondensed-Bold.ttf")
    pdf.add_font("DejaVu", style="I", fname="DejaVuSansCondensed-Oblique.ttf")

    pdf.add_page()

    # ── Clean text (prevents encoding crashes) ────────────────────────────────
    def clean_text(text):
        return text.encode("utf-8", "ignore").decode("utf-8")

    lines = clean_text(optimized_resume).splitlines()

    # ── Detect name ───────────────────────────────────────────────────────────
    name_line = ""
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip():
            name_line = line.strip()
            body_start = i + 1
            break

    # ── Detect contact line ───────────────────────────────────────────────────
    contact_line = ""
    contact_indicators = ["|", "•", "@", "linkedin", "github", "phone", "+", "http"]

    for i, line in enumerate(lines[body_start:], start=body_start):
        if line.strip():
            low = line.lower()
            if any(ind in low for ind in contact_indicators):
                contact_line = line.strip()
                body_start = i + 1
            break

    # ── Header ────────────────────────────────────────────────────────────────
    pdf.set_font("DejaVu", "B", 22)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 10, name_line, ln=True, align="C")

    if contact_line:
        pdf.set_font("DejaVu", size=9)
        pdf.set_text_color(*LIGHT_GRAY)
        pdf.cell(0, 5, contact_line, ln=True, align="C")

    pdf.ln(3)
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.8)
    pdf.line(MARGIN, pdf.get_y(), PAGE_W - MARGIN, pdf.get_y())
    pdf.ln(5)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def is_section_header(text):
        return (
            text == text.upper()
            and len(text) < 50
            and not text.startswith(("-", "•", "*"))
        )

    def is_bullet(text):
        return text.strip().startswith(("-", "•", "*"))

    def clean_bullet(text):
        return text.lstrip("-•* ").strip()

    # ── Body ──────────────────────────────────────────────────────────────────
    for line in lines[body_start:]:
        stripped = line.strip()

        if not stripped:
            pdf.ln(2)
            continue

        if is_section_header(stripped):
            pdf.ln(3)
            pdf.set_font("DejaVu", "B", 11)
            pdf.set_text_color(*ACCENT)
            pdf.cell(0, 6, stripped, ln=True)

            pdf.set_draw_color(*ACCENT)
            pdf.line(MARGIN, pdf.get_y(), PAGE_W - MARGIN, pdf.get_y())
            pdf.ln(3)

        elif is_bullet(stripped):
            pdf.set_font("DejaVu", size=10)
            pdf.set_text_color(*BLACK)

            pdf.set_x(MARGIN + 4)
            pdf.cell(4, 5, "•")

            pdf.set_x(MARGIN + 9)
            pdf.multi_cell(CONTENT_W - 9, 5, clean_bullet(stripped))

        else:
            pdf.set_font("DejaVu", size=10)
            pdf.set_text_color(*BLACK)
            pdf.multi_cell(CONTENT_W, 5, stripped)

    # ── Save PDF ──────────────────────────────────────────────────────────────
    try:
        pdf.output(filepath)
        return f"✅ PDF saved to:\n{filepath}"
    except Exception as e:
        return f"❌ PDF save failed: {e}"


############################################################
# Gradio App
import gradio as gr

with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🚀 AI Resume Optimizer")
    gr.Markdown("Analyse your resume against a job description, select the skills to target, then optimize.")

    # ── API Key ───────────────────────────────────────────────────────────────
    with gr.Accordion("🔑 API Key Setup", open=True):
        with gr.Row():
            api_key_input = gr.Textbox(
                label="OpenAI API Key", placeholder="Paste your OpenAI API key here...", # Label changed
                type="password", scale=4
            )
            set_key_btn = gr.Button("Set API Key", scale=1)
        api_key_status = gr.Textbox(label="Status", interactive=False, lines=1)
        set_key_btn.click(fn=set_api_key, inputs=[api_key_input], outputs=[api_key_status])

    # ── Step 1: Inputs ────────────────────────────────────────────────────────
    gr.Markdown("## Step 1 — Paste or Upload Your Resume & Job Description")
    with gr.Row():
        with gr.Column():
            with gr.Tabs():
                with gr.Tab("✏️ Paste Resume"):
                    resume_paste = gr.Textbox(
                        label="Your Resume", lines=12,
                        placeholder="Paste your resume text here..."
                    )
                with gr.Tab("📎 Upload Resume (.txt or .pdf)"):
                    resume_upload = gr.File(
                        label="Upload Resume", file_types=[".txt", ".pdf"]
                    )
        with gr.Column():
            job_input = gr.Textbox(
                label="Job Description", lines=12,
                placeholder="Paste the job description here..."
            )

    # ── Step 2: Analyse ───────────────────────────────────────────────────────
    gr.Markdown("## Step 2 — Analyse")
    analyse_btn = gr.Button("🔍 Analyse Resume vs Job Description", variant="primary")

    analysis_output = gr.Textbox(
        label="Match Analysis", lines=14, interactive=False
    )

    gr.Markdown("### Select what to optimize for — uncheck anything you want to exclude:")
    with gr.Row():
        skills_checkboxes = gr.CheckboxGroup(
            choices=[], value=[], label="⚙️ Skills & Requirements"
        )
        keywords_checkboxes = gr.CheckboxGroup(
            choices=[], value=[], label="🔑 ATS Keywords"
        )
        responsibilities_checkboxes = gr.CheckboxGroup(
            choices=[], value=[], label="📋 Key Responsibilities"
        )

    analyse_btn.click(
        fn=analyse,
        inputs=[resume_paste, resume_upload, job_input],
        outputs=[analysis_output, skills_checkboxes, keywords_checkboxes, responsibilities_checkboxes]
    )

    # ── Step 3: Optimize ──────────────────────────────────────────────────────
    gr.Markdown("## Step 3 — Optimize")
    optimize_btn = gr.Button("✨ Optimize Resume", variant="primary")
    optimized_output = gr.Textbox(label="Optimized Resume", lines=18, interactive=True)

    optimize_btn.click(
        fn=optimize_resume,
        inputs=[
            resume_paste, resume_upload, job_input,
            skills_checkboxes, keywords_checkboxes, responsibilities_checkboxes
        ],
        outputs=[optimized_output]
    )

    # ── Step 4: Save ──────────────────────────────────────────────────────────
    gr.Markdown("## Step 4 — Save")
    with gr.Row():
        category_dropdown = gr.Dropdown(
            label="Job Category", choices=CATEGORIES, value="ML Engineer", scale=3
        )
        save_txt_btn = gr.Button("💾 Save as .txt", scale=1)
        save_pdf_btn = gr.Button("📄 Save as PDF", scale=1, variant="primary")

    save_status = gr.Textbox(label="Save Status", interactive=False, lines=2)

    save_txt_btn.click(
        fn=save_resume,
        inputs=[optimized_output, category_dropdown],
        outputs=[save_status]
    )
    save_pdf_btn.click(
        fn=save_resume_pdf,
        inputs=[optimized_output, category_dropdown],
        outputs=[save_status]
    )

    gr.Markdown("---")
    view_btn = gr.Button("📂 View Saved Resumes")
    saved_list = gr.Textbox(label="Saved Resumes", interactive=False, lines=10)
    view_btn.click(fn=view_saved_resumes, inputs=[], outputs=[saved_list])

app.launch(share=True)




########################################################################################################

#!pip install gradio openai pypdf2 fpdf2 -q # Uncomment if you need to install packages locally

# from google.colab import drive # Colab-specific - remove for local execution
# import os
# # drive.mount('/content/drive') # Colab-specific - remove for local execution

# # Adjust these paths for local execution
# APP_DIR = "./GUI_Resume_Optimizer" # Example: a local directory
# BASE_DIR = os.path.join(APP_DIR, 'resumes')

# CATEGORIES = [
#      "ML Engineer", "Data Scientist", "AI Engineer", "Computer Vision",
#     "Software Engineer", "Biomedical Science", "Arts & Literature", "Others"
# ]

# os.makedirs(APP_DIR, exist_ok = True)
# for category in CATEGORIES:
#   os.makedirs(os.path.join(BASE_DIR, category.replace(" ", "_")), exist_ok=True)

# print(f"✅ Folders ready at: {BASE_DIR}")

# import openai

# client = None # Global variable to hold OpenAI client instance

# def set_api_key(api_key):
#   global client
#   if not api_key.strip():
#     client = None
#     return "⚠️ Please enter a valid API key."
#   try:
#     client = openai.OpenAI(api_key=api_key.strip())
#     client.models.list() # Test the API key
#     return "✅ OpenAI API key set successfully!"
#   except Exception as e:
#     client = None
#     return f"❌ Error: {e}\n\nPlease check your key and ensure it has access to OpenAI models."


# import json
# from datetime import datetime
# from fpdf import FPDF
# import requests
# import gradio as gr # Keep gradio import here for the app section

# # ── Download fonts if not present ─────────────────────────────────────────────
# def download_font(url, filename):
#     if not os.path.exists(filename):
#         print(f"Downloading {filename}...")
#         try:
#             r = requests.get(url, stream=True)
#             r.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
#             with open(filename, "wb") as f:
#                 for chunk in r.iter_content(chunk_size=8192):
#                     f.write(chunk)
#             print(f"Downloaded {filename}")
#         except requests.exceptions.RequestException as e:
#             print(f"Error downloading {filename}: {e}")
#             # Handle the error, perhaps by falling back to a default font or exiting
#             raise

# download_font(
#     "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSansCondensed.ttf",
#     "DejaVuSansCondensed.ttf"
# )
# download_font(
#     "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSansCondensed-Bold.ttf",
#     "DejaVuSansCondensed-Bold.ttf"
# )
# download_font(
#     "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSansCondensed-Oblique.ttf",
#     "DejaVuSansCondensed-Oblique.ttf"
# )

# # ── Resume text extractor ─────────────────────────────────────────────────────
# def extract_resume_text(pasted_text, uploaded_file):
#     if uploaded_file is not None:
#         # For local execution, uploaded_file will be a string path
#         filepath = uploaded_file if isinstance(uploaded_file, str) else uploaded_file.name
#         ext = os.path.splitext(filepath)[-1].lower()
#         if ext == ".txt":
#             with open(filepath, "r", encoding="utf-8") as f:
#                 return f.read().strip(), None
#         elif ext == ".pdf":
#             try:
#                 from PyPDF2 import PdfReader
#                 reader = PdfReader(filepath)
#                 text = "\n".join(
#                     page.extract_text() for page in reader.pages if page.extract_text()
#                 )
#                 if not text.strip():
#                     return None, "⚠️ PDF appears to be image-based and could not be read as text."
#                 return text.strip(), None
#             except Exception as e:
#                 return None, f"❌ Error reading PDF: {e}"
#         else:
#             return None, "⚠️ Unsupported file type. Please upload a .txt or .pdf file."
#     if pasted_text and pasted_text.strip():
#         return pasted_text.strip(), None
#     return None, "⚠️ Please paste your resume or upload a file."


# # ── Step 1: Analyse JD and resume ────────────────────────────────────────────
# def analyse(pasted_resume, uploaded_resume, job_description):
#     global client # Using global client for OpenAI
#     if client is None: # Check if client is initialized
#         return (
#             "⚠️ Please set your OpenAI API key first.",
#             gr.CheckboxGroup(choices=[], value=[]),
#             gr.CheckboxGroup(choices=[], value=[]),
#             gr.CheckboxGroup(choices=[], value=[]),
#         )

#     resume_text, error = extract_resume_text(pasted_resume, uploaded_resume)
#     if error:
#         return error, gr.CheckboxGroup(choices=[], value=[]), gr.CheckboxGroup(choices=[], value=[]), gr.CheckboxGroup(choices=[], value=[])

#     if not job_description.strip():
#         return "⚠️ Please paste a job description.", gr.CheckboxGroup(choices=[], value=[]), gr.CheckboxGroup(choices=[], value=[]), gr.CheckboxGroup(choices=[], value=[])

#     analysis_prompt = f"""
# You are a expert ATS and recruitment analyst.

# Analyze the job description and the candidate's resume below.
# Return ONLY a valid JSON object with exactly this structure — no explanation, no markdown, no code fences:

# {{
#   "job_title": "string — the target role title",
#   "required_skills": ["skill1", "skill2"],
#   "nice_to_have_skills": ["skill1", "skill2"],
#   "ats_keywords": ["keyword1", "keyword2"],
#   "responsibilities": ["responsibility1", "responsibility2"],
#   "candidate_matching_skills": ["skill1", "skill2"],
#   "candidate_missing_skills": ["skill1", "skill2"],
#   "match_score": integer between 0 and 100,
#   "match_summary": "One sentence summary of how well the candidate fits"
# }}

# Job Description:
# {job_description}

# Candidate Resume:
# {resume_text}
# """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o", # or "gpt-3.5-turbo"
#             messages=[
#                 {"role": "system", "content": "You are a expert ATS and recruitment analyst. Return ONLY a valid JSON object with exactly this structure — no explanation, no markdown, no code fences."},
#                 {"role": "user", "content": analysis_prompt}
#             ]
#         )
#         raw = response.choices[0].message.content.strip()

#         if raw.startswith("```"):
#             raw = raw.split("```")[1]
#             if raw.startswith("json"):
#                 raw = raw[4:]
#         raw = raw.strip()

#         data = json.loads(raw)

#         match_score = data.get("match_score", 0)
#         match_summary = data.get("match_summary", "")
#         job_title = data.get("job_title", "Target Role")
#         matching = data.get("candidate_matching_skills", [])
#         missing = data.get("candidate_missing_skills", [])

#         score_bar = "█" * (match_score // 10) + "░" * (10 - match_score // 10)

#         summary_text = f"""🎯 Target Role: {job_title}

# 📊 Match Score: {match_score}/100
# {score_bar}

# {match_summary}

# ✅ Skills you already have ({len(matching)}):
# {chr(10).join(f"  • {s}" for s in matching) if matching else "  None detected"}

# ❌ Skills gaps ({len(missing)}):
# {chr(10).join(f"  • {s}" for s in missing) if missing else "  None — great fit!"}
# """

#         all_skills = list(dict.fromkeys(
#             data.get("required_skills", []) + data.get("nice_to_have_skills", [])
#         ))
#         ats_keywords = data.get("ats_keywords", [])
#         responsibilities = data.get("responsibilities", [])

#         return (
#             summary_text,
#             gr.CheckboxGroup(choices=all_skills, value=all_skills, label="Skills & Requirements"),
#             gr.CheckboxGroup(choices=ats_keywords, value=ats_keywords, label="ATS Keywords"),
#             gr.CheckboxGroup(choices=responsibilities, value=responsibilities, label="Key Responsibilities"),
#         )

#     except json.JSONDecodeError as e:
#         return (
#             f"❌ Failed to parse analysis response. Raw output:\n\n{raw}\n\nError: {e}",
#             gr.CheckboxGroup(choices=[], value=[]),
#             gr.CheckboxGroup(choices=[], value=[]),
#             gr.CheckboxGroup(choices=[], value=[]),
#         )
#     except Exception as e:
#         return (
#             f"❌ Error during analysis: {e}",
#             gr.CheckboxGroup(choices=[], value=[]),
#             gr.CheckboxGroup(choices=[], value=[]),
#             gr.CheckboxGroup(choices=[], value=[]),
#         )


# # ── Step 2: Optimize resume with selected skills ──────────────────────────────
# def optimize_resume(pasted_resume, uploaded_resume, job_description,
#                     selected_skills, selected_keywords, selected_responsibilities):

#     global client # Using global client for OpenAI
#     if client is None:
#         return "⚠️ Please set your OpenAI API key first."

#     resume_text, error = extract_resume_text(pasted_resume, uploaded_resume)
#     if error:
#         return error

#     if not job_description.strip():
#         return "⚠️ Please paste a job description."

#     if not selected_skills and not selected_keywords and not selected_responsibilities:
#         return "⚠️ Please run Analyse first, then select at least one skill or keyword to optimize for."

#     selected_focus = []
#     if selected_skills:
#         selected_focus.append("SKILLS & REQUIREMENTS TO EMPHASIZE:\n" + "\n".join(f"- {s}" for s in selected_skills))
#     if selected_keywords:
#         selected_focus.append("ATS KEYWORDS TO WEAVE IN:\n" + "\n".join(f"- {k}" for k in selected_keywords))
#     if selected_responsibilities:
#         selected_focus.append("RESPONSIBILITIES TO ALIGN WITH:\n" + "\n".join(f"- {r}" for r in selected_responsibilities))

#     focus_block = "\n\n".join(selected_focus)

#     rewrite_prompt = f"""
# You are a professional resume writer and ATS optimization expert.

# Rewrite the candidate's resume to be perfectly tailored to the target job.

# STRICT RULES:
# - Keep all information truthful — do NOT invent experience, skills, or credentials
# - Naturally weave in the ATS keywords listed below
# - Rewrite the professional summary to match the target role
# - Emphasize the skills and achievements listed below
# - Use strong action verbs and quantify achievements where the original resume supports it
# - Do NOT add metrics or numbers that are not in the original resume
# - Output the COMPLETE rewritten resume as clean, readable text
# - Maintain all original sections (Education, Experience, etc.)

# {focus_block}

# ORIGINAL RESUME:
# {resume_text}

# JOB DESCRIPTION (for context):
# {job_description}
# """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o", # or "gpt-3.5-turbo"
#             messages=[
#                 {"role": "system", "content": "You are a professional resume writer and ATS optimization expert."},
#                 {"role": "user", "content": rewrite_prompt}
#             ]
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         return f"❌ Error optimizing resume: {e}"


# # ── Save and view ─────────────────────────────────────────────────────────────
# def save_resume(optimized_resume, category):
#     if not optimized_resume.strip():
#         return "⚠️ No optimized resume to save. Run Optimize Resume first."
#     category_folder = os.path.join(BASE_DIR, category.replace(" ", "_"))
#     os.makedirs(category_folder, exist_ok=True)
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"{timestamp}_{category.replace(' ', '_')}.txt"
#     filepath = os.path.join(category_folder, filename)
#     with open(filepath, "w", encoding="utf-8") as f:
#         f.write(optimized_resume)
#     return f"✅ Resume saved to:\n{filepath}"


# def view_saved_resumes():
#     if not os.path.exists(BASE_DIR):
#         return "⚠️ No resumes saved yet."
#     lines = []
#     total = 0
#     for category in CATEGORIES:
#         folder = os.path.join(BASE_DIR, category.replace(" ", "_"))
#         if not os.path.exists(folder):
#             continue
#         files = sorted([f for f in os.listdir(folder) if f.endswith(".txt")], reverse=True)
#         if not files:
#             continue
#         lines.append(f"📁 {category} ({len(files)} file{'s' if len(files) != 1 else ''})")
#         for fname in files:
#             try:
#                 dt = datetime.strptime(fname[:15], "%Y%m%d_%H%M%S")
#                 readable_date = dt.strftime("%b %d, %Y at %H:%M:%S")
#             except ValueError:
#                 readable_date = "Unknown date"
#             lines.append(f"   • {fname}  —  {readable_date}")
#         total += len(files)
#     if not lines:
#         return "📭 No saved resumes found yet."
#     lines.insert(0, f"📊 {total} total saved resume{'s' if total != 1 else ''}\n")
#     return "\n".join(lines)


# # ── PDF Generator ────────────────────────────────────────────────────────────
# def save_resume_pdf(optimized_resume, category):
#     if not optimized_resume.strip():
#         return "⚠️ No optimized resume to save. Run Optimize Resume first."

#     category_folder = os.path.join(BASE_DIR, category.replace(" ", "_"))
#     os.makedirs(category_folder, exist_ok=True)

#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"{timestamp}_{category.replace(' ', '_')}.pdf"
#     filepath = os.path.join(category_folder, filename)

#     # ── Constants ─────────────────────────────────────────────────────────────
#     ACCENT       = (44, 62, 122)
#     BLACK        = (30, 30, 30)
#     LIGHT_GRAY   = (120, 120, 120)
#     PAGE_W       = 210
#     MARGIN       = 18
#     CONTENT_W    = PAGE_W - 2 * MARGIN

#     class ResumePDF(FPDF):
#         def footer(self):
#             self.set_y(-12)
#             self.set_font("DejaVu", size=8)
#             self.set_text_color(*LIGHT_GRAY)
#             self.cell(0, 10, f"Page {self.page_no()}", align="C")

#     pdf = ResumePDF(format="A4")
#     pdf.set_margins(MARGIN, MARGIN, MARGIN)
#     pdf.set_auto_page_break(auto=True, margin=15)

#     # ── Load fonts ────────────────────────────────────────────────────────────
#     pdf.add_font("DejaVu", fname="DejaVuSansCondensed.ttf")
#     pdf.add_font("DejaVu", style="B", fname="DejaVuSansCondensed-Bold.ttf")
#     pdf.add_font("DejaVu", style="I", fname="DejaVuSansCondensed-Oblique.ttf")

#     pdf.add_page()

#     # ── Clean text (prevents encoding crashes) ────────────────────────────────
#     def clean_text(text):
#         return text.encode("utf-8", "ignore").decode("utf-8")

#     lines = clean_text(optimized_resume).splitlines()

#     # ── Detect name ───────────────────────────────────────────────────────────
#     name_line = ""
#     body_start = 0
#     for i, line in enumerate(lines):
#         if line.strip():
#             name_line = line.strip()
#             body_start = i + 1
#             break

#     # ── Detect contact line ───────────────────────────────────────────────────
#     contact_line = ""
#     contact_indicators = ["|", "•", "@", "linkedin", "github", "phone", "+", "http"]

#     for i, line in enumerate(lines[body_start:], start=body_start):
#         if line.strip():
#             low = line.lower()
#             if any(ind in low for ind in contact_indicators):
#                 contact_line = line.strip()
#                 body_start = i + 1
#             break

#     # ── Header ────────────────────────────────────────────────────────────────
#     pdf.set_font("DejaVu", "B", 22)
#     pdf.set_text_color(*ACCENT)
#     pdf.cell(0, 10, name_line, ln=True, align="C")

#     if contact_line:
#         pdf.set_font("DejaVu", size=9)
#         pdf.set_text_color(*LIGHT_GRAY)
#         pdf.cell(0, 5, contact_line, ln=True, align="C")

#     pdf.ln(3)
#     pdf.set_draw_color(*ACCENT)
#     pdf.set_line_width(0.8)
#     pdf.line(MARGIN, pdf.get_y(), PAGE_W - MARGIN, pdf.get_y())
#     pdf.ln(5)

#     # ── Helpers ───────────────────────────────────────────────────────────────
#     def is_section_header(text):
#         return (
#             text == text.upper()
#             and len(text) < 50
#             and not text.startswith(("-", "•", "*"))
#         )

#     def is_bullet(text):
#         return text.strip().startswith(("-", "•", "*"))

#     def clean_bullet(text):
#         return text.lstrip("-•* ").strip()

#     # ── Body ──────────────────────────────────────────────────────────────────
#     for line in lines[body_start:]:
#         stripped = line.strip()

#         if not stripped:
#             pdf.ln(2)
#             continue

#         if is_section_header(stripped):
#             pdf.ln(3)
#             pdf.set_font("DejaVu", "B", 11)
#             pdf.set_text_color(*ACCENT)
#             pdf.cell(0, 6, stripped, ln=True)

#             pdf.set_draw_color(*ACCENT)
#             pdf.line(MARGIN, pdf.get_y(), PAGE_W - MARGIN, pdf.get_y())
#             pdf.ln(3)

#         elif is_bullet(stripped):
#             pdf.set_font("DejaVu", size=10)
#             pdf.set_text_color(*BLACK)

#             pdf.set_x(MARGIN + 4)
#             pdf.cell(4, 5, "•")

#             pdf.set_x(MARGIN + 9)
#             pdf.multi_cell(CONTENT_W - 9, 5, clean_bullet(stripped))

#         else:
#             pdf.set_font("DejaVu", size=10)
#             pdf.set_text_color(*BLACK)
#             pdf.multi_cell(CONTENT_W, 5, stripped)

#     # ── Save PDF ──────────────────────────────────────────────────────────────
#     try:
#         pdf.output(filepath)
#         return f"✅ PDF saved to:\n{filepath}"
#     except Exception as e:
#         return f"❌ PDF save failed: {e}"


# ############################################################
# # Gradio App

# with gr.Blocks(theme=gr.themes.Soft()) as app:
#     gr.Markdown("# 🚀 AI Resume Optimizer")
#     gr.Markdown("Analyse your resume against a job description, select the skills to target, then optimize.")

#     # ── API Key ───────────────────────────────────────────────────────────────
#     with gr.Accordion("🔑 API Key Setup", open=True):
#         with gr.Row():
#             api_key_input = gr.Textbox(
#                 label="OpenAI API Key", placeholder="Paste your OpenAI API key here...",
#                 type="password", scale=4
#             )
#             set_key_btn = gr.Button("Set API Key", scale=1)
#         api_key_status = gr.Textbox(label="Status", interactive=False, lines=1)
#         set_key_btn.click(fn=set_api_key, inputs=[api_key_input], outputs=[api_key_status])

#     # ── Step 1: Inputs ────────────────────────────────────────────────────────
#     gr.Markdown("## Step 1 — Paste or Upload Your Resume & Job Description")
#     with gr.Row():
#         with gr.Column():
#             with gr.Tabs():
#                 with gr.Tab("✏️ Paste Resume"):
#                     resume_paste = gr.Textbox(
#                         label="Your Resume", lines=12,
#                         placeholder="Paste your resume text here..."
#                     )
#                 with gr.Tab("📎 Upload Resume (.txt or .pdf)"):
#                     # For local execution, Gradio's File component handles file uploads to a temporary path
#                     resume_upload = gr.File(
#                         label="Upload Resume", file_types=[".txt", ".pdf"]
#                     )
#         with gr.Column():
#             job_input = gr.Textbox(
#                 label="Job Description", lines=12,
#                 placeholder="Paste the job description here..."
#             )

#     # ── Step 2: Analyse ───────────────────────────────────────────────────────
#     gr.Markdown("## Step 2 — Analyse")
#     analyse_btn = gr.Button("🔍 Analyse Resume vs Job Description", variant="primary")

#     analysis_output = gr.Textbox(
#         label="Match Analysis", lines=14, interactive=False
#     )

#     gr.Markdown("### Select what to optimize for — uncheck anything you want to exclude:")
#     with gr.Row():
#         skills_checkboxes = gr.CheckboxGroup(
#             choices=[], value=[], label="⚙️ Skills & Requirements"
#         )
#         keywords_checkboxes = gr.CheckboxGroup(
#             choices=[], value=[], label="🔑 ATS Keywords"
#         )
#         responsibilities_checkboxes = gr.CheckboxGroup(
#             choices=[], value=[], label="📋 Key Responsibilities"
#         )

#     analyse_btn.click(
#         fn=analyse,
#         inputs=[resume_paste, resume_upload, job_input],
#         outputs=[analysis_output, skills_checkboxes, keywords_checkboxes, responsibilities_checkboxes]
#     )

#     # ── Step 3: Optimize ──────────────────────────────────────────────────────
#     gr.Markdown("## Step 3 — Optimize")
#     optimize_btn = gr.Button("✨ Optimize Resume", variant="primary")
#     optimized_output = gr.Textbox(label="Optimized Resume", lines=18, interactive=True)

#     optimize_btn.click(
#         fn=optimize_resume,
#         inputs=[
#             resume_paste, resume_upload, job_input,
#             skills_checkboxes, keywords_checkboxes, responsibilities_checkboxes
#         ],
#         outputs=[optimized_output]
#     )

#     # ── Step 4: Save ──────────────────────────────────────────────────────────
#     gr.Markdown("## Step 4 — Save")
#     with gr.Row():
#         category_dropdown = gr.Dropdown(
#             label="Job Category", choices=CATEGORIES, value="ML Engineer", scale=3
#         )
#         save_txt_btn = gr.Button("💾 Save as .txt", scale=1)
#         save_pdf_btn = gr.Button("📄 Save as PDF", scale=1, variant="primary")

#     save_status = gr.Textbox(label="Save Status", interactive=False, lines=2)

#     save_txt_btn.click(
#         fn=save_resume,
#         inputs=[optimized_output, category_dropdown],
#         outputs=[save_status]
#     )
#     save_pdf_btn.click(
#         fn=save_resume_pdf,
#         inputs=[optimized_output, category_dropdown],
#         outputs=[save_status]
#     )

#     gr.Markdown("---")
#     view_btn = gr.Button("📂 View Saved Resumes")
#     saved_list = gr.Textbox(label="Saved Resumes", interactive=False, lines=10)
#     view_btn.click(fn=view_saved_resumes, inputs=[], outputs=[saved_list])

# app.launch(share=False) # share=False for local execution for privacy
