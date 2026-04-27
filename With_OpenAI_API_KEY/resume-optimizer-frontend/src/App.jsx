// From claude //
import { useState } from "react";
import { analyseResume, optimizeResume } from "./api";
import ProgressBar    from "./components/ProgressBar";
import ApiKeySetup    from "./components/ApiKeySetup";
import InputStep      from "./components/InputStep";
import AnalysisStep   from "./components/AnalysisStep";
import OptimizeStep   from "./components/OptimizeStep";
import SavedResumes   from "./components/SavedResumes";

export default function App() {
  const [step, setStep]                 = useState(0);  // 0=Input 1=Analyse 2=Optimize
  const [apiKey, setApiKey]             = useState("");
  const [loading, setLoading]           = useState(false);
  const [error, setError]               = useState("");
  const [showSaved, setShowSaved]       = useState(false);
  const [savedRefresh, setSavedRefresh] = useState(0);

  // Shared state passed between steps
  const [resumeText, setResumeText]         = useState("");
  const [jobDesc, setJobDesc]               = useState("");
  const [analysis, setAnalysis]             = useState(null);
  const [optimizedResume, setOptimizedResume] = useState("");

  // Step 1 → Step 2: Analyse
  const handleAnalyse = async (resume, jd) => {
    if (!apiKey) { setError("Please set your OpenAI API key first."); return; }
    setError("");
    setLoading(true);
    setResumeText(resume);
    setJobDesc(jd);
    try {
      const result = await analyseResume(resume, jd);
      setAnalysis(result);
      setStep(1);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed. Check your API key.");
    } finally {
      setLoading(false);
    }
  };

  // Step 2 → Step 3: Optimize
  const handleOptimize = async (skills, keywords, responsibilities) => {
    setError("");
    setLoading(true);
    try {
      const result = await optimizeResume(
        resumeText, jobDesc, skills, keywords, responsibilities
      );
      setOptimizedResume(result);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || "Optimization failed.");
    } finally {
      setLoading(false);
    }
  };

  // After save — refresh the saved list
  const handleSaved = () => {
    setSavedRefresh((n) => n + 1);
    setShowSaved(true);
  };

  return (
    <div className="min-h-screen bg-navy-950 text-slate-100">
      {/* Top nav */}
      <nav className="glass-nav px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl drop-shadow-[0_0_8px_rgba(34,211,238,0.4)]">🚀</span>
          <span className="font-bold text-xl tracking-tight text-white">Resume Optimizer</span>
          <span className="text-xs text-slate-400 hidden sm:block">
            powered by OpenAI
          </span>
        </div>
        <button
          onClick={() => setShowSaved(!showSaved)}
          className="btn-secondary text-sm"
        >
          {showSaved ? "← Back to Optimizer" : "📂 Saved Resumes"}
        </button>
      </nav>

      <main className="max-w-5xl mx-auto px-4 py-10">
        {showSaved ? (
          <SavedResumes refresh={savedRefresh} />
        ) : (
          <>
            <ApiKeySetup apiKey={apiKey} onApiKeyChange={setApiKey} />
            <ProgressBar currentStep={step} />

            {error && (
              <div className="mb-6 px-4 py-3 bg-red-50 border border-red-200
                              rounded-xl text-red-600 text-sm">
                ❌ {error}
              </div>
            )}

            {step === 0 && (
              <InputStep
                onNext={handleAnalyse}
                loading={loading}
                setLoading={setLoading}
              />
            )}
            {step === 1 && analysis && (
              <AnalysisStep
                analysis={analysis}
                onNext={handleOptimize}
                onBack={() => setStep(0)}
                loading={loading}
              />
            )}
            {step === 2 && (
              <OptimizeStep
                optimizedResume={optimizedResume}
                onBack={() => setStep(1)}
                onSaved={handleSaved}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

// ################Initial #############
// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from './assets/vite.svg'
// import heroImg from './assets/hero.png'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <section id="center">
//         <div className="hero">
//           <img src={heroImg} className="base" width="170" height="179" alt="" />
//           <img src={reactLogo} className="framework" alt="React logo" />
//           <img src={viteLogo} className="vite" alt="Vite logo" />
//         </div>
//         <div>
//           <h1>Get started</h1>
//           <p>
//             Edit <code>src/App.jsx</code> and save to test <code>HMR</code>
//           </p>
//         </div>
//         <button
//           type="button"
//           className="counter"
//           onClick={() => setCount((count) => count + 1)}
//         >
//           Count is {count}
//         </button>
//       </section>

//       <div className="ticks"></div>

//       <section id="next-steps">
//         <div id="docs">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#documentation-icon"></use>
//           </svg>
//           <h2>Documentation</h2>
//           <p>Your questions, answered</p>
//           <ul>
//             <li>
//               <a href="https://vite.dev/" target="_blank">
//                 <img className="logo" src={viteLogo} alt="" />
//                 Explore Vite
//               </a>
//             </li>
//             <li>
//               <a href="https://react.dev/" target="_blank">
//                 <img className="button-icon" src={reactLogo} alt="" />
//                 Learn more
//               </a>
//             </li>
//           </ul>
//         </div>
//         <div id="social">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#social-icon"></use>
//           </svg>
//           <h2>Connect with us</h2>
//           <p>Join the Vite community</p>
//           <ul>
//             <li>
//               <a href="https://github.com/vitejs/vite" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#github-icon"></use>
//                 </svg>
//                 GitHub
//               </a>
//             </li>
//             <li>
//               <a href="https://chat.vite.dev/" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#discord-icon"></use>
//                 </svg>
//                 Discord
//               </a>
//             </li>
//             <li>
//               <a href="https://x.com/vite_js" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#x-icon"></use>
//                 </svg>
//                 X.com
//               </a>
//             </li>
//             <li>
//               <a href="https://bsky.app/profile/vite.dev" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#bluesky-icon"></use>
//                 </svg>
//                 Bluesky
//               </a>
//             </li>
//           </ul>
//         </div>
//       </section>

//       <div className="ticks"></div>
//       <section id="spacer"></section>
//     </>
//   )
// }

// export default App
