export default function CheckboxGroup({ label, icon, items, selected, onChange }) {
  const toggleAll = () => {
    onChange(selected.length === items.length ? [] : [...items]);
  };

  const toggle = (item) => {
    onChange(
      selected.includes(item)
        ? selected.filter((s) => s !== item)
        : [...selected, item]
    );
  };

  if (!items.length) return null;

  return (
    <div className="glass-card p-5 hover:bg-white/[0.02] transition-colors group/card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-200 flex items-center gap-2">
          <span>{icon}</span> {label}
          <span className="text-[10px] text-slate-500 font-bold ml-1">
            {selected.length}/{items.length}
          </span>
        </h3>
        <button
          onClick={toggleAll}
          className="text-[10px] font-black uppercase tracking-tighter text-cyan-500 hover:text-cyan-400 transition-colors"
        >
          {selected.length === items.length ? "Clear" : "All"}
        </button>
      </div>
      <div className="flex flex-col gap-3 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
        {items.map((item) => (
          <label
            key={item}
            className="flex items-start gap-3 cursor-pointer group/item"
          >
            <div className="relative flex items-center">
              <input
                type="checkbox"
                checked={selected.includes(item)}
                onChange={() => toggle(item)}
                className="peer w-4 h-4 rounded border border-white/20 bg-navy-950 appearance-none 
                           checked:bg-cyan-600 checked:border-cyan-500 transition-all cursor-pointer"
              />
              <span className="absolute text-white scale-0 peer-checked:scale-100 transition-transform pointer-events-none left-0.5 top-0.5 text-[10px]">
                ✓
              </span>
            </div>
            <span className="text-xs text-slate-400 group-hover/item:text-slate-100 transition-colors leading-relaxed">
              {item}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}