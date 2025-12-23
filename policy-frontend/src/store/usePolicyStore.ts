import { create, StateCreator } from "zustand";

interface PolicySource {
  id?: string;
  title?: string;
  date?: string;
  quarter?: string;
  origin_site?: string;
  text?: string;
  url?: string;
}

interface RunQueryPayload {
  question: string;
  sources?: string[];
  start_date?: string;
  end_date?: string;
  quarter?: string;
}

/** Snapshot history entry */
export interface HistoryEntry {
  id: string;
  timestamp: string;
  question: string;
  analysis: string | null;
  sources: PolicySource[];
}

interface PolicyState {
  query: string;
  analysis: string | null;
  sources: PolicySource[];
  loading: boolean;
  error: string | null;

  history: HistoryEntry[];
  addSnapshot: (entry: HistoryEntry) => void;
  clearHistory: () => void;

  loadFromHistory: (entry: HistoryEntry) => void;

  runQuery: (payload: RunQueryPayload) => Promise<void>;
  resetSession: () => void;
}

const N8N_WEBHOOK_URL =
  process.env.REACT_APP_N8N_WORKFLOW_URL ||
  "https://diplo.app.n8n.cloud/webhook/2cc87e08-36db-468f-94da-c7aecc3938ea";

const HISTORY_KEY = "policy_history_v1";
const HISTORY_LIMIT = 10;

const loadHistory = (): HistoryEntry[] => {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

const saveHistory = (history: HistoryEntry[]) => {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  } catch {
    
  }
};

const storeCreator: StateCreator<PolicyState> = (set, get) => ({
  query: "",
  analysis: null,
  sources: [],
  loading: false,
  error: null,

  history: loadHistory(),

  addSnapshot: (entry: HistoryEntry) => {
    const next = [entry, ...get().history].slice(0, HISTORY_LIMIT);
    set({ history: next });
    saveHistory(next);
  },

  clearHistory: () => {
    set({ history: [] });
    try {
      localStorage.removeItem(HISTORY_KEY);
    } catch {
      
    }
  },

  
  loadFromHistory: (entry: HistoryEntry) => {
    set({
      query: entry.question,
      analysis: entry.analysis,
      sources: entry.sources,
      loading: false,
      error: null,
    });
  },

  runQuery: async (payload: RunQueryPayload) => {
    set({
      loading: true,
      error: null,
      query: payload.question,
    });

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 45000);

    try {
      const response = await fetch(N8N_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (!response.ok) {
        let message = "Neuspešan upit.";
        if (response.status === 400) message = "Neispravan upit (400).";
        if (response.status === 404) message = "Nema rezultata (404).";
        if (response.status === 500) message = "Greška na serveru (500).";
        if (response.status === 503) message = "Server privremeno nedostupan (503).";
        throw new Error(message);
      }

      const data = await response.json();

      const analysis = data.analysis || null;
      const sources: PolicySource[] = data.sources || [];

      
      set({
        analysis,
        sources,
        loading: false,
      });

      
      const snapshot: HistoryEntry = {
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        question: payload.question,
        analysis,
        sources,
      };

      get().addSnapshot(snapshot);
    } catch (err: any) {
      clearTimeout(timeout);

      if (err?.name === "AbortError") {
        return set({
          error: "Server predugo odgovara (timeout).",
          loading: false,
        });
      }

      return set({
        error: err?.message || "Neočekivana greška.",
        loading: false,
      });
    }
  },

  resetSession: () => {
    set({
      query: "",
      analysis: null,
      sources: [],
      loading: false,
      error: null,
    });
  },
});

export const usePolicyStore = create<PolicyState>(storeCreator);
