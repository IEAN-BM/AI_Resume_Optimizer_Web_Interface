# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from config import settings

# app = FastAPI(title="Resume Optimizer API")

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/")
# async def root():
#     return {"message": "Resume Optimizer API is running"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

import io
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from models import (
    AnalyseRequest, AnalyseResponse,
    OptimizeRequest, OptimizeResponse,
    SaveRequest, SaveResponse,
    ResumesResponse, ResumeListItem,
)
from services import openai, pdf as pdf_service, supabase as supa
from config import CATEGORIES

import PyPDF2


app = FastAPI(
    title="Resume Optimizer API",
    description="AI-powered resume optimization backend using Gemini",
    version="1.0.0",
)

# ── CORS — open during development ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Tighten this to your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


# ── Resume text extraction from upload ───────────────────────────────────────
@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """
    Accept a .txt or .pdf upload and return the extracted plain text.
    The frontend calls this when the user uploads a file, then stores
    the text locally to pass to /analyse and /optimize.
    """
    ext = file.filename.rsplit(".", 1)[-1].lower()
    content = await file.read()

    if ext == "txt":
        try:
            return {"text": content.decode("utf-8")}
        except UnicodeDecodeError:
            raise HTTPException(400, "Could not decode text file — ensure it is UTF-8.")

    elif ext == "pdf":
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = "\n".join(
                page.extract_text() for page in reader.pages
                if page.extract_text()
            )
            if not text.strip():
                raise HTTPException(
                    422,
                    "PDF appears to be image-based. Please paste the text manually."
                )
            return {"text": text.strip()}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(400, f"Error reading PDF: {e}")

    else:
        raise HTTPException(400, "Unsupported file type. Upload a .txt or .pdf file.")


# ── Analyse ───────────────────────────────────────────────────────────────────
@app.post("/analyse", response_model=AnalyseResponse)
def analyse(req: AnalyseRequest):
    if not req.resume_text.strip():
        raise HTTPException(400, "resume_text is required.")
    if not req.job_description.strip():
        raise HTTPException(400, "job_description is required.")
    try:
        return openai.analyse_resume(req.resume_text, req.job_description)
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {e}")


# ── Optimize ──────────────────────────────────────────────────────────────────
@app.post("/optimize", response_model=OptimizeResponse)
def optimize(req: OptimizeRequest):
    if not req.resume_text.strip():
        raise HTTPException(400, "resume_text is required.")
    if not req.job_description.strip():
        raise HTTPException(400, "job_description is required.")
    if not any([req.selected_skills, req.selected_keywords, req.selected_responsibilities]):
        raise HTTPException(400, "Select at least one skill, keyword, or responsibility.")
    try:
        result = openai.optimize_resume(
            req.resume_text,
            req.job_description,
            req.selected_skills,
            req.selected_keywords,
            req.selected_responsibilities,
        )
        return OptimizeResponse(optimized_resume=result)
    except Exception as e:
        raise HTTPException(500, f"Optimization failed: {e}")


# ── Save ──────────────────────────────────────────────────────────────────────
@app.post("/save", response_model=SaveResponse)
def save(req: SaveRequest):
    if not req.optimized_resume.strip():
        raise HTTPException(400, "optimized_resume is required.")
    if req.category not in CATEGORIES:
        raise HTTPException(400, f"Invalid category. Choose from: {CATEGORIES}")
    if req.format not in ("pdf", "txt"):
        raise HTTPException(400, "format must be 'pdf' or 'txt'.")

    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_cat     = req.category.replace(" ", "_")
    filename     = f"{timestamp}_{safe_cat}.{req.format}"
    storage_path = f"{safe_cat}/{filename}"

    try:
        if req.format == "pdf":
            content      = pdf_service.generate_pdf(req.optimized_resume)
            content_type = "application/pdf"
        else:
            content      = req.optimized_resume.encode("utf-8")
            content_type = "text/plain"

        supa.upload_file(content, storage_path, content_type)
        record      = supa.save_resume_record(filename, req.category, req.format, storage_path)
        public_url  = supa.get_signed_url(storage_path)

        return SaveResponse(
            id           = record["id"],
            filename     = record["filename"],
            category     = record["category"],
            format       = record["format"],
            storage_path = record["storage_path"],
            public_url   = public_url,
            created_at   = record["created_at"],
        )
    except Exception as e:
        raise HTTPException(500, f"Save failed: {e}")


# ── List saved resumes ────────────────────────────────────────────────────────
@app.get("/resumes", response_model=ResumesResponse)
def get_resumes(category: str = None):
    try:
        records = supa.list_resumes()

        if category:
            records = [r for r in records if r["category"] == category]

        items = []
        for r in records:
            signed_url = supa.get_signed_url(r["storage_path"])
            items.append(ResumeListItem(
                id           = r["id"],
                filename     = r["filename"],
                category     = r["category"],
                format       = r["format"],
                storage_path = r["storage_path"],
                public_url   = signed_url,
                created_at   = r["created_at"],
            ))

        return ResumesResponse(total=len(items), resumes=items)
    except Exception as e:
        raise HTTPException(500, f"Could not fetch resumes: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
