# AI Backend Pipeline (sarthak_brain.py)

This module serves as the primary backend for the ATL Legal Prototype. It takes raw text input (from user prompts or parsed PDF files), queries our local ChromaDB vector store (`legal_cases`), and generates structured legal analyses using an IRAC (Issue, Rule, Application, Conclusion) framework.

Instead of a basic linear RAG call, `sarthak_brain.py` uses LangGraph to implement domain-checking, self-correcting search loops, and adversarial validation to prevent hallucinated citations.

---

## 1. Pipeline Architecture

The execution flow is structured as a LangGraph state machine with three core nodes:

* **Domain Guardrail (`domain_check_node`):** Filters out non-legal queries before querying the database. If a prompt is unrelated to Indian law or property/contract disputes, the pipeline terminates early to save token costs and prevent junk output.
* **Self-Correcting Retrieval (`retrieve_cases_node`):** Searches the local `chroma_db` store (collection name: `legal_cases`). If the retrieved chunks have low relevance scores, the node automatically rewrites the search query and retries (maximum 2 retries).
* **Adversarial Validator (`adversarial_validator_node`):** Evaluates the retrieved Supreme Court precedents against the user's facts. Any retrieved case law that does not directly match the legal issue is discarded before generating the final report.

---

## 2. Output Structure

When the pipeline succeeds, it returns a state dictionary containing:
* `final_report`: A formatted string broken into **Timeline**, **Legal Validation (IRAC Framework)**, and citation footnotes matching Neel's `case_metadata.csv` tags (`[Citation: ... | Court: ... | Ref: ...]`).
* `retry_count`: The number of query reformulations triggered during retrieval.
* `status`: Pipeline execution status (`SUCCESS`, `OUT_OF_DOMAIN`, or `NO_PRECEDENTS`).

---

## 3. UI Integration Guide (for Streamlit App)

To integrate the AI backend into `streamlit-app.py`, import the compiled graph (`ai_brain_app`) and invoke it with a single key-value dictionary containing `pdf_text`.

### Example Usage
```python
from sarthak_brain import ai_brain_app

def get_legal_analysis(user_text: str):
    # Pass the raw or extracted PDF text into the LangGraph pipeline
    response = ai_brain_app.invoke({"pdf_text": user_text})
    
    # Extract the rendered markdown report
    return response.get("final_report", "Error generating report.")