import { useState, useEffect } from "react";
import { getSavedResumes } from "../api";

const CATEGORIES = [
  "All", "ML Engineer", "Data Scientist", "AI Engineer", "Computer Vision",
  "Software Engineer", "Biomedical Science", "Arts & Literature", "Others",
];

export default function SavedResumes({ refresh }) {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("All");
  const [error, setError] = useState("");

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const data = await getSavedResumes(filter === "All" ? null : filter);
        setResumes(data.resumes);
      } catch {
        setError("Failed to load saved resumes.");
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [filter, refresh]);

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-500">Repository</span>
          <h3 className="font-bold text-xl text-white">
            📂 Saved Resumes
            <span className="ml-3 text-xs text-slate-500 font-bold bg-white/5 px-2 py-0.5 rounded-full">
              {resumes.length}
            </span>
          </h3>
        </div>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2 bg-navy-900/30 p-2 rounded-2xl border border-white/5">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${filter === cat
                ? "bg-cyan-600 text-white shadow-lg shadow-cyan-900/40"
                : "text-slate-500 hover:text-slate-300 hover:bg-white/5"
              }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <div className="w-8 h-8 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin" />
          <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">Accessing Database...</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm text-center font-medium">
          ⚠️ {error}
        </div>
      )}

      {!loading && !error && resumes.length === 0 && (
        <div className="text-center py-20 glass-card">
          <div className="text-6xl mb-4 opacity-20">📭</div>
          <p className="text-slate-500 font-medium">No saved resumes found in this category.</p>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4">
        {resumes.map((r) => (
          <div
            key={r.id}
            className="glass-card px-6 py-5 flex items-center justify-between hover:border-cyan-500/30 
                       hover:bg-cyan-500/[0.02] transition-all group/item"
          >
            <div className="space-y-1">
              <p className="text-sm font-bold text-white group-hover/item:text-cyan-400 transition-colors">{r.filename}</p>
              <div className="flex items-center gap-3 text-[10px] font-bold uppercase tracking-widest text-slate-500">
                <span className="text-cyan-500/50">{r.category}</span>
                <span>•</span>
                <span>
                  {new Date(r.created_at).toLocaleDateString("en-GB", {
                    day: "numeric", month: "short", year: "numeric"
                  })}
                </span>
              </div>
            </div>
            <a
              href={r.public_url}
              target="_blank"
              rel="noreferrer"
              className="btn-secondary py-2 px-4 text-xs font-bold hover:bg-cyan-600 hover:text-white hover:border-cyan-600 group-hover/item:shadow-lg transition-all"
            >
              {r.format === "pdf" ? "📄 PDF" : "💾 TXT"}
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}