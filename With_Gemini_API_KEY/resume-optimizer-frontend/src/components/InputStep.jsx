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
    <div className="space-y-6">
      {/* Resume input */}
      <div>
        <label className="block text-sm font-semibold text-slate-300 mb-3">
          📄 Your Resume
        </label>

        {/* Tabs */}
        <div className="flex gap-1 mb-3 bg-slate-900 p-1 rounded-lg w-fit">
          {["paste", "upload"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                activeTab === tab
                  ? "bg-navy-800 text-white"
                  : "text-slate-400 hover:text-slate-200"
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
            rows={10}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3
                       text-slate-200 placeholder-slate-600 text-sm resize-none
                       focus:outline-none focus:border-navy-600 transition-colors"
          />
        ) : (
          <div
            onClick={() => fileRef.current.click()}
            className="border-2 border-dashed border-slate-700 hover:border-navy-600
                       rounded-xl p-10 text-center cursor-pointer transition-colors group"
          >
            <div className="text-4xl mb-3">📁</div>
            <p className="text-slate-400 group-hover:text-slate-200 transition-colors">
              Click to upload <span className="text-navy-400">.pdf</span> or{" "}
              <span className="text-navy-400">.txt</span>
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
          <p className="text-xs mt-2 text-slate-400">{uploadStatus}</p>
        )}
      </div>

      {/* Job description */}
      <div>
        <label className="block text-sm font-semibold text-slate-300 mb-3">
          💼 Job Description
        </label>
        <textarea
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
          placeholder="Paste the job description here..."
          rows={10}
          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3
                     text-slate-200 placeholder-slate-600 text-sm resize-none
                     focus:outline-none focus:border-navy-600 transition-colors"
        />
      </div>

      <button
        onClick={() => onNext(resumeText, jobDesc)}
        disabled={!canProceed || loading}
        className="w-full py-3.5 bg-navy-800 hover:bg-navy-700 disabled:opacity-40
                   disabled:cursor-not-allowed rounded-xl font-semibold text-white
                   transition-all duration-200 flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <span className="animate-spin">⏳</span> Analysing...
          </>
        ) : (
          "🔍 Analyse Resume vs Job Description →"
        )}
      </button>
    </div>
  );
}