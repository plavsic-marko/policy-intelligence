import { useEffect, useRef, useState } from "react";
import { usePolicyStore } from "../store/usePolicyStore";

import AnalysisCard from "../components/AnalysisCard";
import ChatInput from "../components/ChatInput";
import ErrorBanner from "../components/ErrorBanner";
import SourceList from "../components/SourceList";

const PolicyChat = () => {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { runQuery, analysis, sources, loading, error } = usePolicyStore();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [analysis, sources]);

  const handleSend = () => {
    if (!input.trim()) return;
    runQuery({ question: input });
    setInput("");
  };

  return (
    <div className="max-w-[900px] mx-auto py-8 px-6 text-slate-100">

      
      <h1 className="text-3xl font-semibold mb-6">
        Policy Intelligence Chat
      </h1>

    
      <ChatInput
        input={input}
        setInput={setInput}
        loading={loading}
        onSend={handleSend}
      />

      
      <ErrorBanner message={error} />

      
      <AnalysisCard analysis={analysis} />

      
      <SourceList sources={sources} />

      <div ref={messagesEndRef} />
    </div>
  );
};

export default PolicyChat;
