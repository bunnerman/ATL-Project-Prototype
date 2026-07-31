<div align="center">

# ⚖️ ATL Project Prototype
### *AI Legal Evidence Verifier & Precedent Assistant*

[![Streamlit App](https://img.shields.io/badge/Streamlit-App_Live-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://atl-project-prototype-nhrtbq5lkkmffezqjarzkf.streamlit.app)
[![Testing Dashboard](https://img.shields.io/badge/Streamlit-Testing_Dashboard-007ACC?style=for-the-badge&logo=streamlit&logoColor=white)](https://atl-project-prototype-3imqmecugmwxpqzuug6v9s.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-Enabled-1C3C3C?style=for-the-badge)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Enabled-2E7D32?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini_3.1_Flash--Lite-Powered-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)

<p align="center">
  <b>A next-generation AI platform designed to automate legal evidence verification, extract chronological event timelines from case documents, and perform high-precision precedent similarity search.</b>
</p>

---

</div>

## 🌐 Live Deployments


| Environment | Purpose | URL |
| :--- | :--- | :--- |
| 🚀 **Main Application** | Production User Interface | [atl-project-prototype.streamlit.app](https://atl-project-prototype-nhrtbq5lkkmffezqjarzkf.streamlit.app) |
| 🧪 **Testing Dashboard** | Experimental Features & QA | [atl-project-prototype-testing.streamlit.app](https://atl-project-prototype-3imqmecugmwxpqzuug6v9s.streamlit.app) |

---

## 🎯 Target Milestones & Roadmap

> [!CAUTION]
> 🔴🔴 **Project Deadline: Sunday** 🔴🔴  
> All core feature developments must be finalized before Saturday to allow full-system testing and UI polish over the weekend.

```text
📅 MON - FRI                 📅 SATURDAY                   📅 SUNDAY
┌─────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│  Core Module Build      │  │  Integration & QA        │  │  Final Polish & Demo     │
│  - Corpus & Vectors     ├─►│  - End-to-end testing    ├─►│  - UI polish & audit     │
│  - PDF Ingest & Gemini  │  │  - Bug fixing & debug    │  │  - Deployment Freeze     │
└─────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘
```

---

## 👥 Team Roles & Work Division Summary

| Team Member | Core Focus & Responsibilities | Modules & Deliverables |
| :--- | :--- | :--- |
| ⚙️ **Parnil** | **DevOps & Cloud Infrastructure** | Streamlit Community Cloud hosting, repository setup, dependency management, Gemini API secrets. |
| ⚖️ **Neel** | **Vector Store & Corpus Engine** | Case corpus hierarchy, HuggingFace embeddings (`all-MiniLM-L6-v2`), text chunking & ChromaDB / NeonDB index. |
| 📄 **Adarsh** | **Document Processing** | Streamlit file uploader, temporary file storage manager, and PyPDF text extraction engine. |
| 🧠 **Sarthak** | **AI Backend & LangGraph RAG Engine** | `sarthak_brain.py`: Gemini 3.1 Flash-Lite integration, Domain Guardrails, self-correcting ChromaDB retrieval loops, Adversarial Precedent Validator, and IRAC/Timeline Report generation. |
| 📊 **Namya** | **DB Retrieval & UI Integration** | NeonDB database retriever, vector similarity search execution & Streamlit UI response rendering. |

---

## 🏗️ System Architecture & Pipeline

```text
               ┌──────────────────────────────┐
               │   User PDF / Document Input  │  (Adarsh)
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │ PyPDF Text Extractor Engine  │  (Adarsh)
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │ Streamlit Frontend Controller│  (Parnil / Namya)
               └──────────────┬───────────────┘
                              │
                              ▼
    ========================================================
    |      LANGGRAPH AI BACKEND (sarthak_brain.py)         |  (Sarthak)
    |------------------------------------------------------|
    |  1. Domain Guardrail & Fact Extraction               |
    |  2. Self-Correcting Retrieval Loop                   | <=== Queries Indexed Case Corpus
    |  3. Adversarial Precedent Validator                  |      (Neel: ChromaDB Store)
    |  4. Timeline & IRAC Synthesis(Gemini 3.1 Flash-Lite) |
    ========================================================
                              │
                              ▼
               ┌──────────────────────────────┐
               │ Interactive IRAC UI Display  │  (Parnil / Namya)
               └──────────────────────────────┘
```


---
> **💡 LLM Engine Strategy:**  
> Our primary pipeline (`sarthak_brain.py`) utilizes **Gemini 3.1 Flash-Lite** (`gemini-3.1-flash-lite`) for ultra-low-latency, cost-effective fact extraction and rapid self-correcting ChromaDB retrieval loops. For complex appellate cases requiring deeper legal reasoning and multi-step IRAC synthesis, our architecture supports seamless routing to **Gemini 3.1 Pro** via simple `.env` model configuration.
---

## ⚙️ Installation & Local Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-username/ATL-Project-Prototype.git
cd ATL-Project-Prototype
```

### 2. Install Dependencies
Install all required framework dependencies:
```bash
pip install streamlit fastapi uvicorn langchain langgraph langchain-google-genai langchain-huggingface langchain-chroma pypdf chromadb sentence-transformers python-multipart requests
```

### 3. Configure Environment Variables
Create a local `.env` file from `.env.txt`:
```bash
cp .env.txt .env
```
Fill in your credentials:
```env
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://user:password@ep-neon-db.tech/neondb?sslmode=require
```

### 4. Run Locally
Launch the Streamlit application:
```bash
streamlit run streamlit-app.py
```

---

## 📄 Module Documentation Links
- 📖 [Sarthak's AI Brain Documentation](./Sarthak_Work.md) — Technical specification for the LangGraph state graph, self-correcting RAG loop, and adversarial precedent validator.
- 📖 [Neel's Work Document](file:///c:/Users/Neel%20Sonawane/ATL-Project-Prototype/Neel's%20Work%20.md) — Detailed technical specification for the Case Corpus, Text Chunking, HuggingFace Embeddings, and ChromaDB / NeonDB Vector Engine.
- 📖 [Dataset Documentation](file:///c:/Users/Neel%20Sonawane/ATL-Project-Prototype/data/README.md) — Guide to raw case structuring and metadata mappings.

---

<div align="center">

<p align="center">
  
  <b>ATL Project Team • 2026</b>
</p>

</div>
