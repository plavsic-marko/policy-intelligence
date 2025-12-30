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


export interface HistoryEntry {
  id: string;
  timestamp: string;
  question: string;
  analysis: string | null;
  sources: PolicySource[];
}


export interface NewsletterEntry {
  id: string;
  timestamp: string;
  period: string; 
  title: string;
  html: string;
}

interface GenerateNewsletterPayload {
  year: number;
  quarter: string;
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

  
  newsletterHtml: string | null;
  loadingNewsletter: boolean;

  newsletterHistory: NewsletterEntry[];
  addNewsletterSnapshot: (entry: NewsletterEntry) => void;
  loadNewsletterFromHistory: (entry: NewsletterEntry) => void;

  generateNewsletter: (
    payload: GenerateNewsletterPayload
  ) => Promise<void>;
}


const N8N_CHAT_WEBHOOK_URL =
  process.env.REACT_APP_N8N_CHAT_WEBHOOK_URL ||
  "https://diplo.app.n8n.cloud/webhook/2cc87e08-36db-468f-94da-c7aecc3938ea";


const N8N_NEWSLETTER_WEBHOOK_URL =
  process.env.REACT_APP_N8N_NEWSLETTER_WEBHOOK_URL ||
  "https://diplo.app.n8n.cloud/webhook/16808ba7-0f2e-461c-beeb-bec5a3571bdd";

const HISTORY_KEY = "policy_history_v1";
const HISTORY_LIMIT = 10;

const NEWSLETTER_HISTORY_KEY = "newsletter_history_v1";
const NEWSLETTER_HISTORY_LIMIT = 8;



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
  } catch {}
};



const loadNewsletterHistory = (): NewsletterEntry[] => {
  try {
    const raw = localStorage.getItem(NEWSLETTER_HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

const saveNewsletterHistory = (items: NewsletterEntry[]) => {
  try {
    localStorage.setItem(
      NEWSLETTER_HISTORY_KEY,
      JSON.stringify(items)
    );
  } catch {}
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
    } catch {}
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
      const response = await fetch(N8N_CHAT_WEBHOOK_URL, {
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
        if (response.status === 503)
          message = "Server privremeno nedostupan (503).";
        throw new Error(message);
      }

      const data = await response.json();

      const analysis = data.analysis || null;
      const sources: PolicySource[] = data.sources || [];

      set({ analysis, sources, loading: false });

      get().addSnapshot({
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        question: payload.question,
        analysis,
        sources,
      });
    } catch (err: any) {
      clearTimeout(timeout);

      if (err?.name === "AbortError") {
        return set({
          error: "Server predugo odgovara (timeout).",
          loading: false,
        });
      }

      set({
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



  newsletterHtml: null,
  loadingNewsletter: false,

  newsletterHistory: loadNewsletterHistory(),

  addNewsletterSnapshot: (entry: NewsletterEntry) => {
    const next = [entry, ...get().newsletterHistory].slice(
      0,
      NEWSLETTER_HISTORY_LIMIT
    );
    set({ newsletterHistory: next });
    saveNewsletterHistory(next);
  },

  loadNewsletterFromHistory: (entry: NewsletterEntry) => {
    set({
      newsletterHtml: entry.html,
      error: null,
    });
  },

  generateNewsletter: async ({ year, quarter }) => {
    set({
      loadingNewsletter: true,
      error: null,
      newsletterHtml: null,
    });

    try {
      const period = `${year}-${quarter}`;

      const response = await fetch(
        N8N_NEWSLETTER_WEBHOOK_URL,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ quarter: period }),
        }
      );

      if (!response.ok) {
        throw new Error("Neuspešno generisanje newsletter-a.");
      }

      const html = await response.text();

      set({
        newsletterHtml: html,
        loadingNewsletter: false,
      });

      get().addNewsletterSnapshot({
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        period,
        title: `Newsletter ${period}`,
        html,
      });
    } catch (err: any) {
      set({
        error: err?.message || "Greška pri generisanju newsletter-a.",
        loadingNewsletter: false,
      });
    }
  },
});

export const usePolicyStore = create<PolicyState>(storeCreator);
