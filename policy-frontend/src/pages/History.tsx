import { usePolicyStore } from "../store/usePolicyStore";

const History = () => {
  const { history, clearHistory } = usePolicyStore();

  return (
    <div className="max-w-[900px] mx-auto py-8 px-6 text-slate-100">
      <h1 className="text-3xl font-semibold mb-6">Search History</h1>

      
      {history.length === 0 && (
        <p className="text-slate-400 text-lg">
          Nema sačuvanih upita.
        </p>
      )}

      
      <ul className="space-y-4">
        {history.map((q, i) => (
          <li
            key={i}
            className="
              bg-slate-800 border border-slate-700 
              p-4 rounded-lg text-[15px]
            "
          >
            {q}
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
    </div>
  );
};

export default History;
