interface AnalysisCardProps {
  analysis: string | null;
}

const SPLIT_MARKER = "Why this matters for Swiss cantons:";

// Helper: kapitalizuje prvo slovo (UI polish)
const capitalizeFirst = (text: string) =>
  text.charAt(0).toUpperCase() + text.slice(1);

const AnalysisCard = ({ analysis }: AnalysisCardProps) => {
  if (!analysis) return null;

  // 🔹 razdvajanje glavnog teksta i zaključka
  const [mainText, conclusionText] = analysis.split(SPLIT_MARKER);

  // 🔹 razbijanje glavnog teksta u paragrafe (3 rečenice po bloku)
  const paragraphs = mainText
    .split(". ")
    .reduce<string[]>((acc, sentence, idx) => {
      const groupIndex = Math.floor(idx / 3);
      if (!acc[groupIndex]) acc[groupIndex] = "";
      acc[groupIndex] += (acc[groupIndex] ? ". " : "") + sentence;
      return acc;
    }, []);

  return (
    <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl mb-6 leading-relaxed text-[15.5px]">
      <h2 className="text-xl font-semibold mb-4">Policy analysis</h2>

      {/* Glavni deo analize */}
      <div className="text-slate-200 mb-6 space-y-4">
        {paragraphs.map((para, idx) => (
          <p key={idx} className="whitespace-pre-wrap">
            {para}
          </p>
        ))}
      </div>

      {/* Izdvojeni zaključak */}
      {conclusionText && (
        <>
          <hr className="border-slate-700 mb-4" />

          <div className="bg-slate-900 border border-slate-700 p-4 rounded-lg">
            <h3 className="text-sm font-semibold text-slate-300 mb-1">
              Why this matters for Swiss cantons
            </h3>

            <p className="whitespace-pre-wrap text-slate-200 text-sm">
              {capitalizeFirst(conclusionText.trim())}
            </p>
          </div>
        </>
      )}
    </div>
  );
};

export default AnalysisCard;
