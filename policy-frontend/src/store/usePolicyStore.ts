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

interface PolicyState {
  query: string;
  analysis: string | null;
  sources: PolicySource[];
  loading: boolean;
  error: string | null;

  history: string[];                     
  addHistory: (prompt: string) => void;  
  clearHistory: () => void;              

  runQuery: (payload: RunQueryPayload) => Promise<void>;
  reset: () => void;
}



const N8N_WEBHOOK_URL =
  process.env.REACT_APP_N8N_WORKFLOW_URL ||
  "https://diplo.app.n8n.cloud/webhook/2cc87e08-36db-468f-94da-c7aecc3938ea";

console.log(" N8N WEBHOOK URL =", N8N_WEBHOOK_URL);



const storeCreator: StateCreator<PolicyState> = (set) => ({
  query: "",
  analysis: null,
  sources: [],
  loading: false,
  error: null,

  
  history: [],

  addHistory: (prompt: string) =>
    set((state) => ({
      history: [prompt, ...state.history].slice(0, 10), 
    })),

  clearHistory: () => set({ history: [] }),

  
  runQuery: async (payload: RunQueryPayload) => {
    console.log(" Sending payload to n8n:", payload);

  
    set({ loading: true, error: null, query: payload.question });

    
    set((state) => ({
      history: [payload.question, ...state.history].slice(0, 10),
    }));

    
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);

    try {
      const response = await fetch(N8N_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      clearTimeout(timeout);
      console.log("📡 HTTP Status:", response.status);

      
      if (!response.ok) {
        let message = "Neuspješan upit.";

        if (response.status === 400) message = "Neispravan upit (400).";
        if (response.status === 404) message = "Nema rezultata za ovaj upit (404).";
        if (response.status === 500) message = "Greška na serveru (500). N8N workflow se srušio.";
        if (response.status === 503) message = "Server privremeno nedostupan (503).";

        throw new Error(message);
      }

      
      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error("Neočekivan format odgovora (nije JSON).");
      }

      console.log(" n8n RESPONSE:", data);

      set({
        analysis: data.analysis || null,
        sources: data.sources || [],
        loading: false,
      });
    } catch (err: any) {
      clearTimeout(timeout);
      console.error(" Policy query error:", err);

      
      if (err.name === "AbortError") {
        return set({
          error: "Server predugo odgovara (timeout). Pokušajte ponovo.",
          loading: false,
        });
      }

      
      if (
        err.message.includes("Failed to fetch") ||
        err.message.includes("NetworkError") ||
        err.message.includes("ECONNREFUSED")
      ) {
        return set({
          error: "Server nije dostupan. Provjerite internet vezu.",
          loading: false,
        });
      }

      
      if (err.message) {
        return set({
          error: err.message,
          loading: false,
        });
      }

     
      set({
        error: "Došlo je do neočekivane greške.",
        loading: false,
      });
    }
  },

  
  reset: () => {
    set({
      query: "",
      analysis: null,
      sources: [],
      loading: false,
      error: null,
      history: [],
    });
  },
});

export const usePolicyStore = create<PolicyState>(storeCreator);
