import os
import time
from typing import TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

# load env variables
load_dotenv()

# check streamlit cloud secrets first, fallback to local .env
api_key = None
try:
    import streamlit as st
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
else:
    print("[WARN] GOOGLE_API_KEY is not properly set.")

# init models
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# setup local vector db
vector_store = Chroma(
    collection_name="legal_cases",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
retriever = vector_store.as_retriever(search_kwargs={"k": 5})


# data structures for graph state
class ExtractedData(BaseModel):
    is_legal_document: bool = Field(description="True if document is a legal contract, dispute, or a plain text legal question. False if out of bounds (math, trivia, etc).")
    timeline: str = Field(description="Chronological bullet points of factual events, or a summary of the user's legal question.")
    search_query: str = Field(description="Concise legal search query for Indian Supreme Court precedents.")

structured_llm = llm.with_structured_output(ExtractedData)

class GraphState(TypedDict):
    pdf_text: str
    is_legal_document: bool
    timeline: str
    search_query: str
    retrieved_cases: str
    final_report: str
    retry_count: int


# --- graph nodes ---

def extract_facts_node(state: GraphState):
    # catch absolute None values as well as empty strings
    raw_input = state.get("pdf_text") or ""
    input_text = str(raw_input).strip()
    
    print("[INFO] Executing Step 1: Fact extraction and domain validation...")
    
    # catch empty input to prevent crashes
    if not input_text:
        print("[WARN] Empty input received.")
        return {
            "is_legal_document": False,
            "timeline": "No input provided.",
            "search_query": "NONE",
            "final_report": "Error: No text received. If you uploaded an image-based PDF, the OCR may have failed. Please type your query in the chat.",
            "retry_count": 0
        }

    # strict prompt to block math/trivia and handle both docs and questions
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a highly specialized Indian Legal AI Assistant. Your exclusive purpose is to analyze legal documents and answer legal queries based on Indian law.
        
        STRICT GUARDRAILS (YOU MUST OBEY THESE):
        1. Legal Documents: If the text is a legal document/contract/dispute, extract core facts and build a timeline. Set is_legal_document to True.
        2. Legal Questions: If the text is a plain legal question (no document), summarize the query as the timeline. Set is_legal_document to True.
        3. OUT OF BOUNDS: If the user asks a math question (e.g., 2+2), coding question, trivia, or anything unrelated to law, YOU MUST REFUSE TO ANSWER. Set is_legal_document to False, and in the 'timeline' field write EXACTLY: "OUT OF BOUNDS".
        """),
        ("human", "{text}")
    ])
    
    chain = prompt | structured_llm
    
    try:
        res = chain.invoke({"text": input_text})
        
        if not res.is_legal_document:
            print("[WARN] Non-legal or out-of-bounds input detected. Halting pipeline.")
            
            # handle out of bounds vs invalid doc
            if "OUT OF BOUNDS" in res.timeline.upper():
                report = "I am a specialized Legal AI Assistant. I can only assist with legal document analysis and questions related to Indian law."
            else:
                report = "Invalid Document/Query\n\nThe provided input is not recognized as a legal query, contract, or dispute file. Please ask a legal question or upload a valid legal document."
            
            return {
                "is_legal_document": False,
                "timeline": res.timeline,
                "search_query": "NONE",
                "final_report": report, 
                "retry_count": 0
            }
            
        timeline_text = res.timeline
        search_query_text = res.search_query
        is_legal = True
        
    except Exception as exc:
        print(f"[ERROR] Structured output parsing failed: {exc}")
        is_legal = True
        timeline_text = "Unable to auto-extract timeline. Please refer to source text."
        search_query_text = input_text[:150]
        
    return {
        "is_legal_document": is_legal,
        "timeline": timeline_text,
        "search_query": search_query_text,
        "retry_count": 0
    }


def retrieve_cases_node(state: GraphState):
    query = state["search_query"]
    attempt = state.get("retry_count", 0) + 1
    print(f"[INFO] Executing Step 2 (Attempt {attempt}): Querying Chroma DB...")
    
    if not os.path.exists("./chroma_db"):
        return {"retrieved_cases": "[ERROR] Chroma DB directory not found."}
    
    # try/except block just in case chromadb acts up
    try:
        docs = retriever.invoke(query)
        
        if not docs:
            cases_text = "No direct Supreme Court precedents were found for this specific scenario."
        else:
            formatted_chunks = []
            for i, doc in enumerate(docs):
                title = doc.metadata.get("case_title", "Unknown Case Title")
                court = doc.metadata.get("court", "Unknown Court")
                year = doc.metadata.get("year", "N/A")
                citation = doc.metadata.get("citation", "No Official Citation")
                file_name = doc.metadata.get("file_name", "Unknown File")
                
                header = f"[Citation: {title} ({year}) | Court: {court} | Ref: {citation} | File: {file_name} | Chunk {i+1}]"
                formatted_chunks.append(f"{header}\n{doc.page_content}")
                
            cases_text = "\n\n---\n\n".join(formatted_chunks)
            
        return {"retrieved_cases": cases_text}
        
    except Exception as e:
        print(f"[ERROR] Database fetch failed: {e}")
        return {"retrieved_cases": "The legal database is currently unavailable or encountered an error. Please try again later."}


def validate_and_format_node(state: GraphState):
    print("[INFO] Executing Step 3: Validating precedent relevance and generating report...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an Expert Indian Legal Advisor and Validator. Evaluate the user's situation against the retrieved Supreme Court cases.
        
        INSTRUCTIONS:
        1. If the user provided a legal document/timeline: Apply relevant cases using the IRAC (Issue, Rule, Application, Conclusion) framework.
        2. If the user asked a general legal question: Answer the question directly and professionally, citing the retrieved cases as your basis.
        3. ALWAYS cite the full case title and citation provided in the '[Citation: ...]' headers of the retrieved cases.
        4. Filter out any completely irrelevant precedents.
        
        If no retrieved cases apply or the database is unavailable, explicitly state 'No relevant precedents found in database.' and provide general legal guidance based on Indian law."""),
        ("human", "SITUATION / TIMELINE:\n{timeline}\n\nRETRIEVED CASES:\n{retrieved_cases}")
    ])
    
    chain = prompt | llm
    res = chain.invoke({
        "timeline": state["timeline"],
        "retrieved_cases": state["retrieved_cases"]
    })
    
    # handle different output formats safely
    report_text = res.content
    if isinstance(report_text, list) and report_text:
        item = report_text[0]
        report_text = item.get("text", str(item)) if isinstance(item, dict) else str(item)
    elif isinstance(report_text, dict):
        report_text = report_text.get("text", str(report_text))
        
    return {"final_report": str(report_text)}


def reformulate_query_node(state: GraphState):
    current_retries = state.get("retry_count", 0) + 1
    old_query = state["search_query"]
    print(f"[INFO] Reformulating query (Retry {current_retries}/2)...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a legal research assistant. The prior search returned no applicable precedents. Generate a broader search query using core Indian property/contract law concepts. Return only the new query string."),
        ("human", "FAILED QUERY: {query}\nTIMELINE:\n{timeline}")
    ])
    
    chain = prompt | llm
    res = chain.invoke({"query": old_query, "timeline": state["timeline"]})
    
    new_query = res.content
    if isinstance(new_query, list) and new_query:
        item = new_query[0]
        new_query = item.get("text", str(item)) if isinstance(item, dict) else str(item)
    elif isinstance(new_query, dict):
        new_query = new_query.get("text", str(new_query))
        
    return {
        "search_query": str(new_query).strip(),
        "retry_count": current_retries
    }


# routers
def domain_check_router(state: GraphState):
    if state.get("is_legal_document") is False:
        return "invalid_domain"
    return "valid_domain"


def should_retry_router(state: GraphState):
    report = state.get("final_report", "").lower()
    retries = state.get("retry_count", 0)
    
    if "no relevant precedents found" in report and retries < 2:
        return "retry"
    return "end"


# build workflow
graph = StateGraph(GraphState)

graph.add_node("extract", extract_facts_node)
graph.add_node("retrieve", retrieve_cases_node)
graph.add_node("validate", validate_and_format_node)
graph.add_node("reformulate", reformulate_query_node)

graph.add_edge(START, "extract")

graph.add_conditional_edges(
    "extract",
    domain_check_router,
    {
        "valid_domain": "retrieve",
        "invalid_domain": END
    }
)

graph.add_edge("retrieve", "validate")

graph.add_conditional_edges(
    "validate",
    should_retry_router,
    {
        "retry": "reformulate",
        "end": END
    }
)

graph.add_edge("reformulate", "retrieve")

ai_brain_app = graph.compile()


# local testing
if __name__ == "__main__":
    sample_lease_dispute = """
    IN THE COURT OF THE RENT CONTROLLER, DELHI
    CASE REF: RC/2024/881 - EVICTION DISPUTE UNDER SLUM AREAS ACT

    FACTS OF THE CASE:
    1. The petitioner, Municipal Corporation of Delhi (Estate Officer), issued an eviction order on 12th February 2024 against the respondent, Mr. Vijay Kumar, who occupies a residential tenement in a notified Slum Area in Old Delhi.
    2. The Estate Officer initiated summary eviction proceedings without seeking permission from the Competent Authority under Section 19 of the Slum Areas (Improvement and Clearance) Act.
    3. The tenant (Respondent) contends that under Supreme Court precedents, no tenant in a notified slum area can be evicted without assessing whether alternative accommodation has been provided or whether eviction would create homelessness.
    4. The petitioner Corporation argues that as a public body managing public premises, it is exempt from the Slum Areas Act restrictions.
    """
    
    print("\n[INFO] Initializing Legal RAG Pipeline...")
    start_time = time.time()
    
    output = ai_brain_app.invoke({"pdf_text": sample_lease_dispute})
    
    duration = round(time.time() - start_time, 2)
    print("\n================ LEGAL REPORT ================\n")
    print(output["final_report"])
    print(f"\n[INFO] Pipeline execution completed in {duration}s (Total Retries: {output.get('retry_count', 0)}).")