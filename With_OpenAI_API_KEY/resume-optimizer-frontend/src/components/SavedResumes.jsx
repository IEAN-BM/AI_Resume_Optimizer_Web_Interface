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
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-800">
          📂 Saved Resumes
          <span className="ml-2 text-xs text-slate-500 font-normal">
            ({resumes.length} total)
          </span>
        </h3>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${filter === cat
                ? "bg-navy-600 text-white shadow-sm"
                : "bg-white text-slate-600 hover:text-slate-900 border border-slate-200 hover:border-slate-300"
              }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading && (
        <p className="text-slate-500 text-sm text-center py-10">Loading...</p>
      )}

      {error && (
        <p className="text-red-600 text-sm">{error}</p>
      )}

      {!loading && !error && resumes.length === 0 && (
        <div className="text-center py-12 text-slate-400">
          <div className="text-5xl mb-3">📭</div>
          <p>No saved resumes yet in this category.</p>
        </div>
      )}

      <div className="space-y-3">
        {resumes.map((r) => (
          <div
            key={r.id}
            className="bg-white border border-slate-200 rounded-xl px-5 py-4 shadow-sm
                       flex items-center justify-between hover:border-slate-300
                       transition-colors"
          >
            <div>
              <p className="text-sm font-medium text-slate-800">{r.filename}</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {r.category} ·{" "}
                {new Date(r.created_at).toLocaleDateString("en-GB", {
                  day: "numeric", month: "short", year: "numeric",
                  hour: "2-digit", minute: "2-digit",
                })}
              </p>
            </div>
            <a
              href={r.public_url}
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 bg-navy-600 hover:bg-navy-700 rounded-lg
                         text-xs font-medium text-white transition-colors flex-shrink-0 shadow-sm"
            >
              {r.format === "pdf" ? "📄 Download PDF" : "💾 Download TXT"}
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}