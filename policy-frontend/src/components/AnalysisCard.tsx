interface AnalysisCardProps {
  analysis: string | null;
}

const AnalysisCard = ({ analysis }: AnalysisCardProps) => {
  if (!analysis) return null;

  return (
    <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl mb-6 leading-relaxed text-[15.5px]">
      <h2 className="text-xl font-semibold mb-3">AI Analysis</h2>
      <p className="whitespace-pre-wrap text-slate-200">
        {analysis}
      </p>
    </div>
  );
};

export default AnalysisCard;
