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
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <span>{icon}</span> {label}
          <span className="text-xs text-slate-500 font-normal">
            ({selected.length}/{items.length} selected)
          </span>
        </h3>
        <button
          onClick={toggleAll}
          className="text-xs text-navy-400 hover:text-navy-300 transition-colors"
        >
          {selected.length === items.length ? "Deselect all" : "Select all"}
        </button>
      </div>
      <div className="flex flex-col gap-2 max-h-52 overflow-y-auto pr-1">
        {items.map((item) => (
          <label
            key={item}
            className="flex items-start gap-3 cursor-pointer group"
          >
            <input
              type="checkbox"
              checked={selected.includes(item)}
              onChange={() => toggle(item)}
              className="mt-0.5 w-4 h-4 rounded accent-navy-600 cursor-pointer flex-shrink-0"
            />
            <span className="text-sm text-slate-300 group-hover:text-white transition-colors leading-snug">
              {item}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}