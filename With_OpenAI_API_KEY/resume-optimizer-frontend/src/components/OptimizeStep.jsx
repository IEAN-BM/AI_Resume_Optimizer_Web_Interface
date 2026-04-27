import { useState } from "react";
import { saveResume } from "../api";

const CATEGORIES = [
  "ML Engineer", "Data Scientist", "AI Engineer", "Computer Vision",
  "Software Engineer", "Biomedical Science", "Arts & Literature", "Others",
];

export default function OptimizeStep({ optimizedResume, onBack, onSaved }) {
  const [resume, setResume]       = useState(optimizedResume);
  const [category, setCategory]   = useState("ML Engineer");
  const [saving, setSaving]       = useState(false);
  const [saveStatus, setSaveStatus] = useState("");

  const handleSave = async (format) => {
    if (!resume.trim()) return;
    setSaving(true);
    setSaveStatus("");
    try {
      const record = await saveResume(resume, category, format);
      setSaveStatus(`✅ Saved as ${format.toUpperCase()}!`);
      onSaved(record);
    } catch (err) {
      setSaveStatus(`❌ ${err.response?.data?.detail || "Save failed"}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between px-2">
        <div className="space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-500">Final Result</span>
          <h3 className="font-bold text-xl text-white">✨ Optimized Resume</h3>
        </div>
        <p className="text-xs text-slate-500 font-medium">You can edit the text below before saving</p>
      </div>

      <div className="relative group">
        <div className="absolute -inset-1 bg-gradient-to-b from-cyan-500/20 to-transparent rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        <textarea
          value={resume}
          onChange={(e) => setResume(e.target.value)}
          rows={15}
          className="relative w-full bg-navy-900 border border-white/10 rounded-xl px-6 py-6
                     text-slate-200 text-sm resize-none font-mono leading-relaxed
                     focus:outline-none focus:border-cyan-500/30 transition-all focus:ring-1 focus:ring-cyan-500/10 shadow-2xl"
        />
      </div>

      {/* Save controls */}
      <div className="glass-card p-6 border-cyan-500/10 bg-cyan-500/[0.02]">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-lg">💾</span>
          <h4 className="text-sm font-bold text-slate-200 uppercase tracking-widest">Export & Save</h4>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 space-y-1">
            <span className="text-[10px] font-bold text-slate-500 ml-1 uppercase">Category</span>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-navy-950 border border-white/10 rounded-xl px-4 py-3
                         text-slate-200 text-sm focus:outline-none focus:border-cyan-500/50
                         transition-all cursor-pointer appearance-none"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-row gap-3 pt-5">
            <button
              onClick={() => handleSave("pdf")}
              disabled={saving}
              className="btn-primary flex items-center gap-2"
            >
              {saving ? "⏳ Saving..." : <>📄 <span className="hidden sm:inline">Save as</span> PDF</>}
            </button>

            <button
              onClick={() => handleSave("txt")}
              disabled={saving}
              className="btn-secondary flex items-center gap-2"
            >
              {saving ? "⏳ Saving..." : <>💾 <span className="hidden sm:inline">Save as</span> TXT</>}
            </button>
          </div>
        </div>

        {saveStatus && (
          <div className={`mt-4 text-xs font-bold p-3 rounded-lg border flex items-center gap-2 ${
            saveStatus.includes("✅") 
            ? "bg-green-500/10 text-green-400 border-green-500/20" 
            : "bg-red-500/10 text-red-400 border-red-500/20"
          }`}>
            {saveStatus}
          </div>
        )}
      </div>

      <div className="flex pt-2">
        <button
          onClick={onBack}
          className="btn-secondary"
        >
          ← Back to Analysis
        </button>
      </div>
    </div>
  );
}