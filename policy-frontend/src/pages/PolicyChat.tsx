import { useEffect, useRef, useState } from "react";
import { usePolicyStore } from "../store/usePolicyStore";

import AnalysisCard from "../components/AnalysisCard";
import ChatInput from "../components/ChatInput";
import ErrorBanner from "../components/ErrorBanner";
import SourceList from "../components/SourceList";

const PolicyChat = () => {
  const [input, setInput] = useState("");
  const [lastQuestion, setLastQuestion] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    runQuery,
    analysis,
    sources,
    loading,
    error,
    resetSession,
  } = usePolicyStore();

 
  useEffect(() => {
    if (!analysis) {
      resetSession();
    }
  }, [analysis, resetSession]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [analysis, sources]);

  const handleSend = () => {
    if (!input.trim()) return;

    setLastQuestion(input.trim());
    runQuery({ question: input.trim() });
    setInput("");
  };

  return (
    <div className="max-w-[900px] mx-auto py-8 px-6 text-slate-100">
      <h1 className="text-3xl font-semibold mb-6">
        Policy Chat
      </h1>

      <ChatInput
        input={input}
        setInput={setInput}
        loading={loading}
        onSend={handleSend}
      />

      <ErrorBanner message={error} />

      
      {lastQuestion && !analysis && (
        <>
          <div className="mb-2 text-slate-400 text-sm">
            <span className="text-slate-300 font-medium">Query:</span>{" "}
            {lastQuestion}
          </div>
          <hr className="border-slate-700 mb-4" />
        </>
      )}

     
      {loading && !analysis && (
        <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl mb-6">
          <div className="text-slate-400 text-sm animate-pulse">
            AI is thinking…
          </div>
        </div>
      )}

      
      <AnalysisCard analysis={analysis} />

      <SourceList sources={sources} />

      <div ref={messagesEndRef} />
    </div>
  );
};

export default PolicyChat;
