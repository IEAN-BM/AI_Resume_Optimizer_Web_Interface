# 🚀 Resume Optimizer

The **Resume Optimizer** is an AI-powered tool designed to help job seekers tailor their resumes to specific job descriptions. Using Google's **Gemini Pro**, it analyzes the gap between your current resume and a target role, suggests improvements, and generates an optimized version that is ATS-friendly.

---

## 🛠️ How It Works

1.  **Extraction**: Upload your resume (PDF or TXT). The system extracts the plain text using `PyPDF2`.
2.  **Analysis**: Provide a Job Description. Gemini compares your skills, keywords, and responsibilities against the requirements.
3.  **Gap Assessment**: The tool identifies "Required Skills," "Nice-to-Have Skills," and "Missing Keywords."
4.  **Optimization**: Select which skills and keywords to incorporate. Gemini rewrites your resume to highlight these elements naturally.
5.  **Persistence**: Save your optimized resumes to a secure database (Supabase) and download them as clean PDF or TXT files.

---

## 🚀 Getting Started

You can get your own Resume Optimizer running in two ways:

### 1. Quick Start (Running the Script)
If you just want to run the tool locally:
1.  **Clone the Repo**: `git clone <your-repo-url>`
2.  **Set API Keys**: Create a `.env` file in the `backend/` folder with your `OPENAI_API_KEY`.
3.  **Launch Backend**:
    ```bash
    cd resume_optimizer_backend
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    python main.py
    ```
4.  **Launch Frontend**:
    ```bash
    cd resume-optimizer-frontend
    npm install
    npm run dev
    ```

### 2. Building from Scratch (Development)
If you want to modify or extend the project:
- **Frontend**: Built with **React**, **Vite**, and **Tailwind CSS v4**. Located in `resume-optimizer-frontend/`.
- **Backend**: Built with **FastAPI** and **Python**. Located in `resume_optimizer_backend/`.
- **Database**: Integrated with **Supabase** for file storage and record management.
- **AI Engine**: Leverages `generativeai` (openai) for analysis and optimization.

---

## 📋 Prerequisites
- Python 3.10+
- Node.js 18+
- An Openai API Key ([Get one on their site])
- A Supabase Project (Optional for local testing)

---

## 📄 License
MIT License - Feel free to use and modify for your own career growth!

## Very relevant Limitations
To have this work for you, you have two options:
Update the backend files with you valid gemini API key and that will work
If not do what I did
##
I had to switch to OpenAI API key, and so it could work. If you see the files where I changed the API, 
T commented the gemini API_Key.
The focus was on gemini until I couldn't test because the API_Keys were not working at all.