# PolicyChunksUnified — Multi-Source Policy Intelligence Pipeline

This repository implements a **stable, multi-source ingestion and retrieval pipeline**
for policy-related content, unified into a single Weaviate collection:

    PolicyChunksUnified

The system is designed for **hybrid search (BM25 + vector embeddings)** and serves as
a backend foundation for policy analysis, RAG systems, n8n workflows, and frontend UIs.

---

##  Core Concept

Instead of maintaining separate databases per source, all sources are:

- crawled
- normalized
- chunked at paragraph level
- ingested

into **one unified collection** with a consistent schema and metadata.

This enables:
- cross-source semantic search
- relevance comparison across origins
- time-based and thematic filtering
- stable RAG context generation

---

##  Supported Sources

Currently integrated sources include:

- **DigWatch**
- **IETF**
- **EU Digital Strategy**
- **ITU**
- **UN (ODET / policy-related content)**

All sources are ingested into the same Weaviate class:

    PolicyChunksUnified

---

##  High-Level Architecture

    [ Crawlers / Raw data ]
              ↓
    [ Normalization & cleaning ]
              ↓
    [ Paragraph-level chunking ]
              ↓
    [ Source-specific ingest pipelines ]
              ↓
    [ PolicyChunksUnified (Weaviate) ]
              ↓
    [ Hybrid search / RAG / UI / n8n ]

---

##  Repository Structure (relevant parts)

    project-root/
    │
    ├── scripts/
    │   ├── digwatch/                # DigWatch normalization & preparation
    │   ├── eu_digital_strategy/     # EU Digital Strategy prep & helpers
    │   ├── ietf/                    # IETF prep & helpers
    │   ├── itu/                     # ITU prep & helpers
    │   ├── un/                      # UN prep & helpers
    │   │
    │   ├── ingest_digwatch_unified.py
    │   ├── ingest_ietf_unified.py
    │   ├── ingest_eu_digital.py
    │   ├── ingest_itu_unified.py
    │   ├── ingest_un_unified.py
    │   │
    │   ├── weaviate_client.py
    │   └── delete_ietf_from_weaviate.py
    │
    ├── data/
    │   ├── raw/                     # crawler outputs
    │   └── processed/               # cleaned / chunked JSONL files
    │
    ├── policy-frontend/             # frontend UI (separate README)
    │
    ├── .env.example
    └── README.md

---

##  Ingestion Pipeline

Each source has its own dedicated ingestion script.

Examples:

    python scripts/ingest_digwatch_unified.py
    python scripts/ingest_ietf_unified.py
    python scripts/ingest_eu_digital.py
    python scripts/ingest_itu_unified.py
    python scripts/ingest_un_unified.py

All ingestion scripts:
- write exclusively to `PolicyChunksUnified`
- use stable UUIDs
- do not delete existing data

---

##  Testing / Sanity Checks

A minimal smoke test to verify the system:

    python scripts/test_hybrid_unified.py

This confirms:
- the collection exists
- hybrid search returns results
- metadata fields (`origin_site`, `date`, `quarter`) are populated

---

##  Weaviate Configuration

Create a `.env` file in the project root:

    WEAVIATE_URL=https://<cluster>.weaviate.network
    WEAVIATE_API_KEY=<api_key>

The project uses **Weaviate Cloud** with the `text2vec-weaviate`
(Snowflake Arctic Embed) embedding model.

---

##  Frontend

The frontend application lives in:

    policy-frontend/

It has its own `README.md` with setup and usage instructions.

---

## 👤 Author

Marko Plavšić
