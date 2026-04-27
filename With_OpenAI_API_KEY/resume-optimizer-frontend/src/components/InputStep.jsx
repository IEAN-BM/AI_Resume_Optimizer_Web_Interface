import { useState, useRef } from "react";
import { extractText } from "../api";

export default function InputStep({ onNext, loading, setLoading }) {
  const [resumeText, setResumeText]     = useState("");
  const [jobDesc, setJobDesc]           = useState("");
  const [uploadStatus, setUploadStatus] = useState("");
  const [activeTab, setActiveTab]       = useState("paste");
  const fileRef = useRef();

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploadStatus("⏳ Extracting text...");
    setLoading(true);
    try {
      const text = await extractText(file);
      setResumeText(text);
      setActiveTab("paste");
      setUploadStatus(`✅ "${file.name}" loaded — ${text.length} characters`);
    } catch (err) {
      setUploadStatus(`❌ ${err.response?.data?.detail || "Failed to read file"}`);
    } finally {
      setLoading(false);
    }
  };

  const canProceed = resumeText.trim() && jobDesc.trim();

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Resume input */}
      <div className="glass-card p-6">
        <label className="block text-xs font-bold uppercase tracking-widest text-cyan-500 mb-4">
          📄 Step 1: Your Resume
        </label>

        {/* Tabs */}
        <div className="flex gap-1 mb-4 bg-navy-950 p-1 rounded-xl w-fit border border-white/5">
          {["paste", "upload"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-2 rounded-lg text-sm font-semibold transition-all ${
                activeTab === tab
                  ? "bg-cyan-600 text-white shadow-lg"
                  : "text-slate-500 hover:text-slate-300"
              }`}
            >
              {tab === "paste" ? "✏️ Paste" : "📎 Upload"}
            </button>
          ))}
        </div>

        {activeTab === "paste" ? (
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Paste your resume text here..."
            rows={8}
            className="w-full bg-navy-950/50 border border-white/10 rounded-xl px-4 py-4
                       text-slate-100 placeholder-slate-600 text-sm resize-none
                       focus:outline-none focus:border-cyan-500/30 transition-all focus:ring-1 focus:ring-cyan-500/20"
          />
        ) : (
          <div
            onClick={() => fileRef.current.click()}
            className="border-2 border-dashed border-white/10 hover:border-cyan-500/50 hover:bg-cyan-500/5
                       rounded-2xl p-12 text-center cursor-pointer transition-all group"
          >
            <div className="text-5xl mb-4 grayscale group-hover:grayscale-0 transition-all">📁</div>
            <p className="text-slate-400 group-hover:text-slate-200 transition-colors font-medium">
              Click to upload <span className="text-cyan-400">.pdf</span> or{" "}
              <span className="text-cyan-400">.txt</span>
            </p>
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.txt"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>
        )}

        {uploadStatus && (
          <p className="text-xs mt-3 text-cyan-400/80 font-medium">{uploadStatus}</p>
        )}
      </div>

      {/* Job description */}
      <div className="glass-card p-6">
        <label className="block text-xs font-bold uppercase tracking-widest text-cyan-500 mb-4">
          💼 Step 2: Job Description
        </label>
        <textarea
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
          placeholder="Paste the job description here..."
          rows={8}
          className="w-full bg-navy-950/50 border border-white/10 rounded-xl px-4 py-4
                     text-slate-100 placeholder-slate-600 text-sm resize-none
                     focus:outline-none focus:border-cyan-500/30 transition-all focus:ring-1 focus:ring-cyan-500/20"
        />
      </div>

      <button
        onClick={() => onNext(resumeText, jobDesc)}
        disabled={!canProceed || loading}
        className="btn-primary w-full py-4 text-base tracking-wide flex items-center justify-center gap-3"
      >
        {loading ? (
          <>
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Analysing...
          </>
        ) : (
          <>🔍 Analyse Resume vs Job Description</>
        )}
      </button>
    </div>
  );
}