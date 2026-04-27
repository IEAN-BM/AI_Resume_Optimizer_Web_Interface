const steps = ["Input", "Analyse", "Optimize", "Save"];

export default function ProgressBar({ currentStep }) {
  return (
    <div className="flex items-center justify-center gap-0 mb-12">
      {steps.map((label, i) => (
        <div key={label} className="flex items-center">
          <div className="flex flex-col items-center">
            <div className={`
              w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold
              transition-all duration-500
              ${i < currentStep
                ? "bg-cyan-600 text-white shadow-[0_0_15px_rgba(8,145,178,0.3)]"
                : i === currentStep
                ? "bg-navy-700 text-white ring-4 ring-cyan-500/20 border-2 border-cyan-500/50"
                : "bg-navy-900 text-slate-600 border border-white/5"}
            `}>
              {i < currentStep ? "✓" : i + 1}
            </div>
            <span className={`
              text-[10px] uppercase tracking-widest mt-2 font-bold
              ${i === currentStep ? "text-cyan-400" : "text-slate-600"}
            `}>
              {label}
            </span>
          </div>
          {i < steps.length - 1 && (
            <div className={`
              w-12 h-[2px] mb-6 mx-1 transition-all duration-500
              ${i < currentStep ? "bg-cyan-600" : "bg-navy-900"}
            `} />
          )}
        </div>
      ))}
    </div>
  );
}