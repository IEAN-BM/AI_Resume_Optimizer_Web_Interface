import { useState } from "react";

export default function ApiKeySetup({ apiKey, onApiKeyChange }) {
  const [open, setOpen] = useState(!apiKey);
  const [input, setInput] = useState(apiKey || "");
  const [saved, setSaved] = useState(!!apiKey);

  const handleSave = () => {
    if (!input.trim()) return;
    onApiKeyChange(input.trim());
    setSaved(true);
    setOpen(false);
  };

  return (
    <div className="glass-card mb-6 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">🔑</span>
          <span className="font-medium text-slate-100">OpenAI API Key</span>
          {saved && (
            <span className="text-xs bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-0.5 rounded-full">
              ✓ Set
            </span>
          )}
        </div>
        <span className="text-slate-500 text-sm">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="px-5 pb-5 border-t border-white/5">
          <p className="text-xs text-slate-400 mt-3 mb-3">
            Get your API key at{" "}
            <a
              href="https://platform.openai.com/api-keys"
              target="_blank"
              rel="noreferrer"
              className="text-cyan-400 hover:underline font-medium"
            >
              platform.openai.com
            </a>
          </p>
          <div className="flex gap-3">
            <input
              type="password"
              value={input}
              onChange={(e) => { setInput(e.target.value); setSaved(false); }}
              placeholder="sk-..."
              className="flex-1 bg-navy-950/50 border border-white/10 rounded-lg px-4 py-2.5
                         text-slate-100 placeholder-slate-500 text-sm
                         focus:outline-none focus:border-cyan-500/50 transition-colors"
            />
            <button
              onClick={handleSave}
              disabled={!input.trim()}
              className="btn-primary py-2.5 px-5 disabled:opacity-40 disabled:cursor-not-allowed">
              Save Key
            </button>
          </div>
        </div>
      )}
    </div>
  );
}