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
    <div className="space-y-6">
      {/* Match score card */}
      <div className="bg-slate-900 border border-slate-700 rounded-xl p-5">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-slate-200">
            🎯 {analysis.job_title}
          </h3>
          <span className={`text-2xl font-bold ${scoreColor}`}>
            {analysis.match_score}
            <span className="text-sm text-slate-500 font-normal">/100</span>
          </span>
        </div>

        {/* Score bar */}
        <div className="w-full h-2.5 bg-slate-800 rounded-full mb-3 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${barColor}`}
            style={{ width: `${analysis.match_score}%` }}
          />
        </div>

        <p className="text-sm text-slate-400 mb-4">{analysis.match_summary}</p>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-green-400 mb-2">
              ✅ Skills you have ({analysis.candidate_matching_skills.length})
            </p>
            <ul className="space-y-1">
              {analysis.candidate_matching_skills.map((s) => (
                <li key={s} className="text-xs text-slate-400 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500 flex-shrink-0" />
                  {s}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-xs font-semibold text-red-400 mb-2">
              ❌ Skill gaps ({analysis.candidate_missing_skills.length})
            </p>
            <ul className="space-y-1">
              {analysis.candidate_missing_skills.map((s) => (
                <li key={s} className="text-xs text-slate-400 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-500 flex-shrink-0" />
                  {s}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Checkbox groups */}
      <p className="text-sm text-slate-400">
        All items are pre-selected. Uncheck anything you don't want emphasized in your optimized resume.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <CheckboxGroup
          label="Skills & Requirements"
          icon="⚙️"
          items={allSkills}
          selected={selectedSkills}
          onChange={setSelectedSkills}
        />
        <CheckboxGroup
          label="ATS Keywords"
          icon="🔑"
          items={analysis.ats_keywords}
          selected={selectedKeywords}
          onChange={setSelectedKeywords}
        />
        <CheckboxGroup
          label="Key Responsibilities"
          icon="📋"
          items={analysis.responsibilities}
          selected={selectedResponsibilities}
          onChange={setSelectedResponsibilities}
        />
      </div>

      <div className="flex gap-3">
        <button
          onClick={onBack}
          className="px-6 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl
                     font-medium text-slate-300 transition-colors"
        >
          ← Back
        </button>
        <button
          onClick={() =>
            onNext(selectedSkills, selectedKeywords, selectedResponsibilities)
          }
          disabled={
            !selectedSkills.length &&
            !selectedKeywords.length &&
            !selectedResponsibilities.length ||
            loading
          }
          className="flex-1 py-3 bg-navy-800 hover:bg-navy-700 disabled:opacity-40
                     disabled:cursor-not-allowed rounded-xl font-semibold text-white
                     transition-all flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <span className="animate-spin">⏳</span> Optimizing...
            </>
          ) : (
            "✨ Optimize Resume →"
          )}
        </button>
      </div>
    </div>
  );
}