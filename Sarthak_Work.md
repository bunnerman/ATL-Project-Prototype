# The Brain: AI Backend Architecture (`sarthak_brain.py`)

This document outlines the complete backend architecture, state management, and defensive logic I engineered for the ATL Legal Prototype. 

The `sarthak_brain.py` module acts as the core engine. It takes raw text (either typed user queries, extracted PDF text, or a combination of both), searches a local vector database for Supreme Court precedents, and generates a structured legal report using the IRAC (Issue, Rule, Application, Conclusion) framework.

Instead of relying on a linear, single-shot LLM call, I implemented a **LangGraph State Machine**. This allows the backend to loop, self-correct, and actively block out-of-bounds queries before they waste computing resources or crash the frontend.

---

## 1. Core Tech Stack
* **LLM Engine:** Google Gemini 3.1 Flash-Lite (Set to `temperature=0` to ensure strict, deterministic, and factual outputs).
* **Embeddings:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (Running locally on the CPU for cost-efficiency).
* **Vector Database:** ChromaDB (Stored locally in the `./chroma_db` directory).
* **Framework:** LangGraph (for state routing) & LangChain.

---

## 2. State Management (`GraphState`)
Data moves through the LangGraph pipeline using a shared `TypedDict` state. Every node reads from and updates this dictionary. The guaranteed output contract prevents UI `KeyError` crashes.

* `pdf_text`: The raw input string passed from the UI.
* `is_legal_document`: Boolean flag set by the gatekeeper to determine if the query is valid.
* `timeline`: Extracted facts from a document, or a summary of a plain legal question.
* `search_query`: The optimized query string sent to ChromaDB.
* `retrieved_cases`: The raw text chunks of the top 5 precedents fetched from the database.
* `final_report`: **(Target Output)** The formatted Markdown string containing the IRAC report.
* `retry_count`: Tracks how many times the search query has been broadened and retried.

---

## 3. Pipeline Nodes (The Logic Steps)

The backend executes across four primary nodes:

### A. `extract_facts_node` (The Gatekeeper)
* **Function:** Validates the user input and structures the data for search.
* **Mechanism:** Uses Gemini's `.with_structured_output()` to force a strict Pydantic JSON response. 
* **Domain Guardrail:** If a user asks a math question (e.g., "What is 2+2?"), a coding query, or general trivia, the prompt strictly classifies it as "OUT OF BOUNDS". The node flags `is_legal_document` as `False`, which kills the pipeline early and returns a predefined rejection message.

### B. `retrieve_cases_node` (The Searcher)
* **Function:** Pulls relevant case law from our local dataset.
* **Mechanism:** Converts the search query into vector embeddings and retrieves the `k=5` closest chunks from ChromaDB. 
* **Metadata Extraction:** Appends strict citation headers (Case Title, Court, Year, File Name) to the chunks so the LLM has exact, non-hallucinated references.

### C. `validate_and_format_node` (The Advisor)
* **Function:** Formats the final response and acts as an adversarial validator.
* **Mechanism:** Evaluates the retrieved Supreme Court chunks against the user's timeline. It explicitly filters out irrelevant precedents. 
* **Formatting:** Generates the final output using the IRAC legal framework and attaches the strict metadata citations.

### D. `reformulate_query_node` (The Self-Corrector)
* **Function:** Handles cases where the initial search fails.
* **Mechanism:** If the Validator determines that *none* of the retrieved cases apply to the user's scenario, it rewrites the search query using broader contract/property law concepts and triggers a retry loop (capped at 2 retries).

---

## 4. Conditional Routers (The Traffic Cops)
To connect the nodes, I built two conditional edge routers:
1. **`domain_check_router`:** Checks the `is_legal_document` flag after Node 1. If `False`, it routes directly to `END`. If `True`, it routes to Node 2 (Retrieval).
2. **`should_retry_router`:** Checks the `final_report` text after Node 3. If it contains "no relevant precedents found" and `retry_count < 2`, it routes to Node 4 (Reformulate). Otherwise, it routes to `END`.

---

## 5. Defensive Engineering & Failsafes
To ensure the backend is "bulletproof" against frontend glitches or missing files, I implemented 4 specific defensive layers:

1. **Hybrid Key Authentication:** The script first checks for `st.secrets` (for Streamlit Cloud deployment). If it fails, it gracefully falls back to `os.getenv` for local VS Code testing.
2. **`NoneType` & Empty Input Guard:** If the frontend PDF OCR fails or sends a literal `None` object, the backend catches it immediately, bypasses the LLM, and returns a safe error string.
3. **Database Crash Handler:** The ChromaDB invocation is wrapped in a `try/except` block. If the local `./chroma_db` folder is missing or corrupted, it returns a safe string ("Database unavailable") instead of throwing a fatal terminal traceback.
4. **Guaranteed Key Returns:** Error states and success states return the exact same dictionary structure, guaranteeing the UI never crashes looking for a missing key.

---

## 6. UI Integration Guide (For Frontend Team)

To connect the Streamlit frontend to this backend, import the compiled `ai_brain_app`. Combine both the chat input and PDF text into a single string to ensure the backend has full context.

```python
from sarthak_brain import ai_brain_app

def get_legal_analysis(user_prompt: str, pdf_content: str):
    # Combine inputs for full context
    combined_input = f"User Query: {user_prompt}\n\nDocument Data: {pdf_content}"
    
    # Invoke the LangGraph state machine
    response = ai_brain_app.invoke({"pdf_text": combined_input})
    
    # Extract the final Markdown report safely
    return response.get("final_report", "Error generating report.")