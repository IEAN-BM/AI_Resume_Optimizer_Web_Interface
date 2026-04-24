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
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-200">✨ Optimized Resume</h3>
        <p className="text-xs text-slate-500">You can edit the text below before saving</p>
      </div>

      <textarea
        value={resume}
        onChange={(e) => setResume(e.target.value)}
        rows={20}
        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3
                   text-slate-200 text-sm resize-none font-mono leading-relaxed
                   focus:outline-none focus:border-navy-600 transition-colors"
      />

      {/* Save controls */}
      <div className="bg-slate-900 border border-slate-700 rounded-xl p-4">
        <h4 className="text-sm font-semibold text-slate-300 mb-3">💾 Save Resume</h4>
        <div className="flex flex-col sm:flex-row gap-3">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-3 py-2.5
                       text-slate-200 text-sm focus:outline-none focus:border-navy-600
                       transition-colors cursor-pointer"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>

          <button
            onClick={() => handleSave("pdf")}
            disabled={saving}
            className="px-5 py-2.5 bg-navy-800 hover:bg-navy-700 disabled:opacity-40
                       disabled:cursor-not-allowed rounded-lg text-sm font-medium
                       text-white transition-colors"
          >
            {saving ? "⏳ Saving..." : "📄 Save as PDF"}
          </button>

          <button
            onClick={() => handleSave("txt")}
            disabled={saving}
            className="px-5 py-2.5 bg-slate-700 hover:bg-slate-600 disabled:opacity-40
                       disabled:cursor-not-allowed rounded-lg text-sm font-medium
                       text-white transition-colors"
          >
            {saving ? "⏳ Saving..." : "💾 Save as TXT"}
          </button>
        </div>

        {saveStatus && (
          <p className="text-sm mt-3 text-slate-300">{saveStatus}</p>
        )}
      </div>

      <button
        onClick={onBack}
        className="px-6 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl
                   font-medium text-slate-300 transition-colors"
      >
        ← Back to Analysis
      </button>
    </div>
  );
}