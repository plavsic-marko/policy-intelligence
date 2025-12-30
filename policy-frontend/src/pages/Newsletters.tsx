import { useState } from "react";
import { usePolicyStore } from "../store/usePolicyStore";

const YEARS = [2023, 2024, 2025];
const QUARTERS = ["Q1", "Q2", "Q3", "Q4"];

const Newsletters = () => {
  const [year, setYear] = useState(2025);
  const [quarter, setQuarter] = useState("Q4");

  const {
    newsletterHtml,
    loadingNewsletter,
    error,
    generateNewsletter,
  } = usePolicyStore();

  const handleGenerate = () => {
    generateNewsletter({ year, quarter });
  };

  const handleDownload = () => {
    if (!newsletterHtml) return;

    const blob = new Blob([newsletterHtml], { type: "text/html" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `newsletter_${year}_${quarter}.html`;
    a.click();

    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-[1000px] mx-auto py-8 px-6 text-slate-100">
      <h1 className="text-3xl font-semibold mb-6">Newsletters</h1>

      {/* Controls */}
      <div className="flex gap-4 mb-6 items-end">
        <div>
          <label className="block text-sm text-slate-400 mb-1">Year</label>
          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2"
          >
            {YEARS.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm text-slate-400 mb-1">Quarter</label>
          <select
            value={quarter}
            onChange={(e) => setQuarter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2"
          >
            {QUARTERS.map((q) => (
              <option key={q} value={q}>{q}</option>
            ))}
          </select>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loadingNewsletter}
          className="
            ml-4 px-5 py-3 rounded-lg font-medium
            bg-blue-600 hover:bg-blue-500
            disabled:bg-slate-700
          "
        >
          {loadingNewsletter ? "Generating…" : "Generate newsletter"}
        </button>

        {newsletterHtml && (
          <button
            onClick={handleDownload}
            className="
              px-5 py-3 rounded-lg font-medium
              bg-slate-700 hover:bg-slate-600
            "
          >
            Download
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-900/40 text-red-300 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      
      {newsletterHtml && (
        <iframe
          srcDoc={newsletterHtml}
          title="Newsletter preview"
          className="w-full h-[70vh] rounded-xl border border-slate-700 bg-white"
        />
      )}
    </div>
  );
};

export default Newsletters;
