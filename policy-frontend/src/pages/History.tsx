import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { usePolicyStore } from "../store/usePolicyStore";

const History = () => {
  const navigate = useNavigate();

  const {
    history,
    clearHistory,
    loadFromHistory,
    resetSession,

    // ⬇⬇⬇ NEWSLETTER
    newsletterHistory,
    loadNewsletterFromHistory,
  } = usePolicyStore();

  useEffect(() => {
    resetSession();
  }, [resetSession]);

  return (
    <div className="max-w-[900px] mx-auto py-8 px-6 text-slate-100">
      {/* ======================
          SEARCH HISTORY
         ====================== */}
      <h1 className="text-3xl font-semibold mb-6">Search History</h1>

      {history.length === 0 && (
        <p className="text-slate-400 text-lg">
          Nema sačuvanih upita.
        </p>
      )}

      <ul className="space-y-4">
        {history.map((h) => (
          <li
            key={h.id}
            onClick={() => {
              loadFromHistory(h);
              navigate("/");
            }}
            className="
              bg-slate-800 border border-slate-700 
              p-4 rounded-lg text-[15px]
              cursor-pointer hover:bg-slate-700
              transition
            "
          >
            <div className="text-slate-400 text-xs mb-2">
              {new Date(h.timestamp).toLocaleString()}
            </div>

            <div className="text-slate-100 font-medium">
              {h.question}
            </div>

            <div className="text-slate-400 text-xs mt-2">
              Sources: {h.sources?.length ?? 0}
            </div>
          </li>
        ))}
      </ul>

      {history.length > 0 && (
        <button
          onClick={clearHistory}
          className="
            mt-6 px-5 py-3 rounded-lg 
            bg-red-600 hover:bg-red-500 
            text-white text-sm font-medium
          "
        >
          Clear History
        </button>
      )}

      {/* ======================
          NEWSLETTER HISTORY
         ====================== */}
      <h2 className="text-2xl font-semibold mt-12 mb-6">
        Newsletter History
      </h2>

      {newsletterHistory.length === 0 && (
        <p className="text-slate-400 text-sm">
          Nema generisanih newsletter-a.
        </p>
      )}

      <ul className="space-y-4">
        {newsletterHistory.map((n) => (
          <li
            key={n.id}
            onClick={() => {
              loadNewsletterFromHistory(n);
              navigate("/newsletters");
            }}
            className="
              bg-slate-800 border border-slate-700 
              p-4 rounded-lg cursor-pointer
              hover:bg-slate-700 transition
            "
          >
            <div className="text-slate-400 text-xs mb-1">
              {new Date(n.timestamp).toLocaleString()}
            </div>

            <div className="text-slate-100 font-medium">
              {n.title}
            </div>

            <div className="text-slate-400 text-xs mt-1">
              Period: {n.period}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default History;
