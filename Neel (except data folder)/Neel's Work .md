# ⚖️ Neel's Work — Legal Case Corpus & Vector Index Engine

> **Module Owner:** Neel  
> **Role:** Case Corpus Architecture, Dataset Pipeline, HuggingFace Embeddings, Text Chunking & Vector Store

---

## 📌 Executive Summary

This document details the architectural design, implementation, and operational workflow of the **Legal Case Corpus & Vector Store Engine** developed for the **AI Legal Evidence Verifier**.

The engine transforms raw Indian legal judgment files into a high-dimensional vector search index, enabling semantic retrieval, metadata-filtered queries, and seamless retrieval-augmented generation (RAG).

---

## 📁 1. Corpus Hierarchy & Directory Design

The dataset is organized into 10 key Indian legal domains with strict separation between raw input files and embedding-ready outputs:

```text
data/
├── raw_cases/                       # Raw input files (never indexed directly)
│   ├── civil/                       # Civil disputes & land suits
│   ├── property/                    # Title, partition, & possession
│   ├── criminal/                    # IPC & CrPC proceedings
│   ├── contracts/                   # Breach, specific performance
│   ├── consumer/                    # Consumer protection forum orders
│   ├── family/                      # Matrimonial & custody matters
│   ├── labour/                      # Employment & industrial disputes
│   ├── taxation/                    # Direct & indirect tax appeals
│   ├── commercial/                  # Commercial courts & arbitration
│   └── constitutional/              # Writs & fundamental rights
│
├── processed_cases/                 # Multi-stage cleaning pipeline
│   ├── cleaned/                     # Sanitized raw text
│   ├── normalized/                  # Standardized legal formats & OCR fixes
│   └── ready_for_embedding/         # Final target directory for DirectoryLoader
│
└── metadata/
    └── case_metadata.csv            # Structured metadata database
```

> [!IMPORTANT]
> **Data Loading Policy**: The ingestion engine strictly loads documents from `data/processed_cases/ready_for_embedding/`. The `raw_cases` directory remains immutable to ensure reproducibility.

---

## 🔄 2. Dataset Processing Pipeline

The judgment processing engine operates through four automated stages:

```text
┌────────────────────────────────────────────────────────┐
│  Raw Judgments (data/raw_cases/*/*.txt)                │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Cleaning & Preprocessing                              │
│  - Strip non-ASCII noise, extra line breaks            │
│  - Sanitize header/footer artifacts                    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Normalization                                         │
│  - Standardize case citations & legal abbreviations    │
│  - Remove duplicate paragraphs & page numbers          │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Embedding-Ready Stage                                 │
│  - Write finalized text to ready_for_embedding/        │
│  - Sync entry in case_metadata.csv                     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Chunking & Indexing                                   │
│  - RecursiveCharacterTextSplitter (Size: 500, Ov: 50)  │
│  - HuggingFace sentence-transformers/all-MiniLM-L6-v2  │
│  - ChromaDB Vector Store & NeonDB Integration          │
└────────────────────────────────────────────────────────┘
```

---

## 🏷️ 3. Metadata Schema Architecture

Every document chunk retains rich metadata to support filtered vector queries:

| Metadata Field | Description | Example |
| :--- | :--- | :--- |
| **`case_id`** | Unique Identifier | `CIV-2023-101` |
| **`case_title`** | Title of Cause List | `Ramesh Sharma v. State of Maharashtra` |
| **`court`** | Adjudicating Authority | `Supreme Court of India` |
| **`state`** | Jurisdiction State | `Maharashtra` |
| **`year`** | Year of Judgment | `2023` |
| **`case_type`** | Legal Domain Category | `Civil` |
| **`citation`** | Official Law Reporter Citation | `2023 SCC 451` |
| **`source_dataset`**| Archive Origin | `District Court Archives` |
| **`file_name`** | Relative File Name | `civil_case_001.txt` |
| **`keywords`** | Extracted Legal Taxonomy | `civil, land dispute, damages` |

---

## ⚡ 4. HuggingFace Embeddings & Vector Index Configuration

- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` via `HuggingFaceEmbeddings`
- **Vector Database**: `ChromaDB` (Local Persistent Storage at `chroma_db/`)
- **Cloud Database Integration**: `NeonDB` (PostgreSQL + pgvector connection string ready)
- **Text Splitter Parameters**:
  - `chunk_size`: 500 characters
  - `chunk_overlap`: 50 characters

---

## 🛠️ 5. Execution Guide (`vector_store.py` & `ingest_real_dataset.py`)

### Run Processing Pipeline
```bash
python vector_store.py --process
```

### Build / Update Vector Index
```bash
python vector_store.py --index
```

### Ingest Real Legal Dataset & Ingestion Benchmarks
```bash
python ingest_real_dataset.py
```

### Perform Vector Similarity Query
```bash
python vector_store.py --query "property partition deed title dispute"
```

---

## 📊 Status & Deliverables Summary

- [x] Case Corpus Directory Structure (10 Categories)
- [x] Multi-stage Text Cleaning & Normalization Pipeline
- [x] HuggingFace Embeddings Integration (`all-MiniLM-L6-v2`)
- [x] Text Chunking Engine with Metadata Preservation
- [x] ChromaDB Vector Database Persistence
- [x] NeonDB Environment Integration (`DATABASE_URL` configured)
- [x] Ingestion & Batch Indexing Utility (`ingest_real_dataset.py`)
