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
    <div className="bg-white border border-slate-200 shadow-sm rounded-xl mb-6 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">🔑</span>
          <span className="font-medium text-slate-800">OpenAI API Key</span>
          {saved && (
            <span className="text-xs bg-green-50 text-green-600 border border-green-200 px-2 py-0.5 rounded-full">
              ✓ Set
            </span>
          )}
        </div>
        <span className="text-slate-400 text-sm">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="px-5 pb-5 border-t border-slate-100">
          <p className="text-xs text-slate-500 mt-3 mb-3">
            Get your API key at{" "}
            <a
              href="https://platform.openai.com/api-keys"
              target="_blank"
              rel="noreferrer"
              className="text-navy-600 hover:underline font-medium"
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
              className="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5
                         text-slate-800 placeholder-slate-400 text-sm
                         focus:outline-none focus:border-navy-500 transition-colors"
            />
            <button
              onClick={handleSave}
              disabled={!input.trim()}
              className="px-5 py-2.5 bg-navy-600 hover:bg-navy-700 disabled:opacity-40
                         disabled:cursor-not-allowed rounded-lg text-sm font-medium
                         text-white transition-colors">Save Key
            </button>
          </div>
        </div>
      )}
    </div>
  );
}