import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// Upload a file and get back plain text
export const extractText = async (file) => {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/extract-text", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data.text;
};

// Analyse resume vs job description
export const analyseResume = async (resumeText, jobDescription) => {
  const res = await api.post("/analyse", {
    resume_text: resumeText,
    job_description: jobDescription,
  });
  return res.data;
};

// Optimize resume with selected skills/keywords/responsibilities
export const optimizeResume = async (
  resumeText,
  jobDescription,
  selectedSkills,
  selectedKeywords,
  selectedResponsibilities
) => {
  const res = await api.post("/optimize", {
    resume_text: resumeText,
    job_description: jobDescription,
    selected_skills: selectedSkills,
    selected_keywords: selectedKeywords,
    selected_responsibilities: selectedResponsibilities,
  });
  return res.data.optimized_resume;
};

// Save resume to Supabase
export const saveResume = async (optimizedResume, category, format) => {
  const res = await api.post("/save", {
    optimized_resume: optimizedResume,
    category,
    format,
  });
  return res.data;
};

// Get all saved resumes
export const getSavedResumes = async (category = null) => {
  const params = category ? { category } : {};
  const res = await api.get("/resumes", { params });
  return res.data;
};