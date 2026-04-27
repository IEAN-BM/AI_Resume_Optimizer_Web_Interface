import { useState } from "react";
import CheckboxGroup from "./CheckboxGroup";

export default function AnalysisStep({ analysis, onNext, onBack, loading }) {
  const [selectedSkills, setSelectedSkills]   = useState([
    ...analysis.required_skills,
    ...analysis.nice_to_have_skills,
  ]);
  const [selectedKeywords, setSelectedKeywords]             = useState([...analysis.ats_keywords]);
  const [selectedResponsibilities, setSelectedResponsibilities] = useState([...analysis.responsibilities]);

  const allSkills = [
    ...new Set([...analysis.required_skills, ...analysis.nice_to_have_skills]),
  ];

  const scoreColor =
    analysis.match_score >= 70
      ? "text-green-400"
      : analysis.match_score >= 40
      ? "text-yellow-400"
      : "text-red-400";

  const barColor =
    analysis.match_score >= 70
      ? "bg-green-500"
      : analysis.match_score >= 40
      ? "bg-yellow-500"
      : "bg-red-500";

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Match score card */}
      <div className="glass-card p-8 relative overflow-hidden">
        {/* Abstract background glow */}
        <div className={`absolute top-0 right-0 w-32 h-32 blur-3xl opacity-20 rounded-full ${barColor}`} />

        <div className="flex items-center justify-between mb-4">
          <div className="space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">Analysis Result</span>
            <h3 className="font-bold text-xl text-white">
              🎯 {analysis.job_title}
            </h3>
          </div>
          <div className="text-right">
            <span className={`text-4xl font-black ${scoreColor}`}>
              {analysis.match_score}
            </span>
            <span className="text-sm text-slate-500 font-bold ml-1">/100</span>
          </div>
        </div>

        {/* Score bar */}
        <div className="w-full h-3 bg-navy-950 rounded-full mb-6 overflow-hidden border border-white/5">
          <div
            className={`h-full rounded-full transition-all duration-1000 ${barColor} shadow-[0_0_15px_rgba(34,211,238,0.2)]`}
            style={{ width: `${analysis.match_score}%` }}
          />
        </div>

        <p className="text-sm text-slate-300 leading-relaxed mb-8 border-l-2 border-cyan-500/30 pl-4">
          {analysis.match_summary}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
          <div className="bg-navy-950/40 p-4 rounded-xl border border-green-500/10">
            <p className="text-xs font-bold uppercase tracking-widest text-green-400 mb-3 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              Matching Skills ({analysis.candidate_matching_skills.length})
            </p>
            <ul className="space-y-2">
              {analysis.candidate_matching_skills.map((s) => (
                <li key={s} className="text-xs text-slate-400 flex items-center gap-2">
                  <span className="text-green-500/50">✦</span>
                  {s}
                </li>
              ))}
            </ul>
          </div>
          <div className="bg-navy-950/40 p-4 rounded-xl border border-red-500/10">
            <p className="text-xs font-bold uppercase tracking-widest text-red-400 mb-3 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
              Skill Gaps ({analysis.candidate_missing_skills.length})
            </p>
            <ul className="space-y-2">
              {analysis.candidate_missing_skills.map((s) => (
                <li key={s} className="text-xs text-slate-400 flex items-center gap-2">
                  <span className="text-red-500/50">✦</span>
                  {s}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Checkbox groups */}
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="h-[1px] flex-1 bg-white/5" />
          <p className="text-[10px] font-bold uppercase tracking-[0.3em] text-slate-500">
            Optimization Strategy
          </p>
          <div className="h-[1px] flex-1 bg-white/5" />
        </div>
        
        <p className="text-xs text-center text-slate-400 max-w-lg mx-auto leading-relaxed">
          Select the specific items you want the AI to emphasize. We've pre-selected everything for maximum impact.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <CheckboxGroup
            label="Skills"
            icon="⚙️"
            items={allSkills}
            selected={selectedSkills}
            onChange={setSelectedSkills}
          />
          <CheckboxGroup
            label="Keywords"
            icon="🔑"
            items={analysis.ats_keywords}
            selected={selectedKeywords}
            onChange={setSelectedKeywords}
          />
          <CheckboxGroup
            label="Responsibilities"
            icon="📋"
            items={analysis.responsibilities}
            selected={selectedResponsibilities}
            onChange={setSelectedResponsibilities}
          />
        </div>
      </div>

      <div className="flex gap-4 pt-4">
        <button
          onClick={onBack}
          className="btn-secondary flex-none"
        >
          ← Back
        </button>
        <button
          onClick={() =>
            onNext(selectedSkills, selectedKeywords, selectedResponsibilities)
          }
          disabled={
            (!selectedSkills.length &&
            !selectedKeywords.length &&
            !selectedResponsibilities.length) ||
            loading
          }
          className="btn-primary flex-1 py-4 flex items-center justify-center gap-3"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Optimizing...
            </>
          ) : (
            "✨ Generate Optimized Resume"
          )}
        </button>
      </div>
    </div>
  );
}