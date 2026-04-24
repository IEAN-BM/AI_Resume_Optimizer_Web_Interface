const steps = ["Input", "Analyse", "Optimize", "Save"];

export default function ProgressBar({ currentStep }) {
  return (
    <div className="flex items-center justify-center gap-0 mb-10">
      {steps.map((label, i) => (
        <div key={label} className="flex items-center">
          <div className="flex flex-col items-center">
            <div className={`
              w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold
              transition-all duration-300
              ${i < currentStep
                ? "bg-navy-800 text-white"
                : i === currentStep
                ? "bg-navy-600 text-white ring-4 ring-navy-800/40"
                : "bg-slate-800 text-slate-500"}
            `}>
              {i < currentStep ? "✓" : i + 1}
            </div>
            <span className={`
              text-xs mt-1 font-medium
              ${i === currentStep ? "text-navy-400" : "text-slate-500"}
            `}>
              {label}
            </span>
          </div>
          {i < steps.length - 1 && (
            <div className={`
              w-16 h-0.5 mb-4 mx-1 transition-all duration-300
              ${i < currentStep ? "bg-navy-800" : "bg-slate-800"}
            `} />
          )}
        </div>
      ))}
    </div>
  );
}