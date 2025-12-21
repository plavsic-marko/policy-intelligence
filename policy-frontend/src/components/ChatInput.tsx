interface ChatInputProps {
  input: string;
  loading: boolean;
  setInput: (val: string) => void;
  onSend: () => void;
}

const ChatInput = ({ input, setInput, loading, onSend }: ChatInputProps) => {
  return (
    <div className="flex gap-3 mb-6">
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSend()}
        placeholder="Ask about global digital policy, e.g. 'AI regulation in Q3 2025'"
        disabled={loading}
        className="
          flex-1 px-4 py-3 
          rounded-lg border border-slate-700 
          bg-slate-900 text-slate-200 text-[15px]
          outline-none transition focus:border-slate-500
          disabled:opacity-60 disabled:cursor-not-allowed
        "
      />

      <button
        onClick={onSend}
        disabled={loading}
        className={`
          px-5 py-3 rounded-lg font-medium text-[15px]
          ${loading 
            ? "bg-slate-700 cursor-wait" 
            : "bg-blue-600 hover:bg-blue-500 cursor-pointer"}
          text-white transition
        `}
      >
        {loading ? "Running…" : "Run query"}
      </button>
    </div>
  );
};

export default ChatInput;
