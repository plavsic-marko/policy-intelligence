import { useEffect, useState } from "react";

interface AnalysisCardProps {
  analysis: string | null;
}

const AnalysisCard = ({ analysis }: AnalysisCardProps) => {
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!analysis) return;

    setIsTyping(true);
    let index = 0;

    const interval = setInterval(() => {
      index++;

      if (index <= analysis.length) {
        setDisplayedText(analysis.slice(0, index));
      } else {
        clearInterval(interval);
        setIsTyping(false);
      }
    }, 15);

    return () => clearInterval(interval);
  }, [analysis]);

  if (!analysis) return null;

  return (
    <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl mb-6 leading-relaxed text-[15.5px]">
      <h2 className="text-xl font-semibold mb-3">Policy analysis</h2>

      <p className="whitespace-pre-wrap text-slate-200">
        {displayedText}
        {isTyping && <span className="animate-pulse">▍</span>}
      </p>
    </div>
  );
};

export default AnalysisCard;
