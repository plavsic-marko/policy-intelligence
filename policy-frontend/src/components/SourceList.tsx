interface SourceItem {
  origin_site?: string;
  date?: string;
  title?: string;
  url?: string;
}

interface SourceListProps {
  sources: SourceItem[];
}

const SourceList = ({ sources }: SourceListProps) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="bg-slate-900 border border-slate-700 p-6 rounded-xl mb-6">
      <h2 className="text-xl font-semibold mb-4">Sources</h2>

      <ul className="space-y-4">
        {sources.map((s, i) => (
          <li key={i} className="pb-3 border-b border-slate-700">
            <div className="text-sm opacity-70 mb-1">
              {s.origin_site || "unknown"} • {s.date || "no date"}
            </div>

            <div className="text-[16px] font-medium mb-1">
              {s.title}
            </div>

            <a
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 text-sm hover:underline"
            >
              Open source →
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SourceList;
