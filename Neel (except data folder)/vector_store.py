"""
vector_store.py
Legal Case Dataset Management & Vector Store Pipeline

This module handles:
1. Data Cleaning & Normalization (raw_cases -> cleaned -> normalized -> ready_for_embedding)
2. Metadata Preservation (loads case_metadata.csv and attaches attributes to chunks)
3. Data Loading (STRICTLY loads from data/processed_cases/ready_for_embedding/)
4. Text Chunking & HuggingFace Embedding Generation
5. ChromaDB Vector Store Indexing and Querying
"""

import os
import re
import sys
import site
import shutil
import argparse
import pandas as pd

# Ensure user site-packages are accessible
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_CASES_DIR = os.path.join(DATA_DIR, "raw_cases")
PROCESSED_CASES_DIR = os.path.join(DATA_DIR, "processed_cases")

CLEANED_DIR = os.path.join(PROCESSED_CASES_DIR, "cleaned")
NORMALIZED_DIR = os.path.join(PROCESSED_CASES_DIR, "normalized")
READY_FOR_EMBEDDING_DIR = os.path.join(PROCESSED_CASES_DIR, "ready_for_embedding")

METADATA_FILE = os.path.join(DATA_DIR, "metadata", "case_metadata.csv")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")


# ---------------------------------------------------------------------------
# Pipeline Stage 1: Cleaning
# ---------------------------------------------------------------------------
def clean_text(raw_text: str) -> str:
    """
    Performs initial cleaning on raw text:
    - Removes null bytes
    - Normalizes line endings
    - Fixes basic encoding glitches
    """
    text = raw_text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


# ---------------------------------------------------------------------------
# Pipeline Stage 2: Normalization
# ---------------------------------------------------------------------------
def normalize_text(text: str) -> str:
    """
    Normalizes legal text:
    - Removes headers and footers (e.g. --- HEADER: ... ---, --- FOOTER: ... ---)
    - Removes page numbers (e.g. Page 1 of 5, PAGE 3 OF 10)
    - Removes OCR artifacts and invalid characters
    - Deduplicates identical consecutive paragraphs
    - Collapses excessive whitespace and empty lines
    """
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Remove header / footer lines
        if re.match(r"^---?\s*(HEADER|FOOTER):.*---?$", stripped, re.IGNORECASE):
            continue

        # Remove page numbers
        if re.match(r"^(Page|PAGE)\s+\d+\s+(of|OF)\s+\d+$", stripped):
            continue

        # Remove OCR error tags like [OCR ERROR: ...] or [OCR Artifact: ...]
        stripped = re.sub(r"\[OCR\s*(ERROR|Artifact|error|artifact)[^\]]*\]", "", stripped)

        # Remove unprintable non-ASCII symbols while preserving standard punctuation
        stripped = re.sub(r"[^\x20-\x7E\t\n]", "", stripped)

        # Collapse multi-spaces within lines
        stripped = re.sub(r"[ \t]+", " ", stripped)

        cleaned_lines.append(stripped)

    # Reassemble paragraphs
    content = "\n".join(cleaned_lines)
    paragraphs = content.split("\n\n")

    # Deduplicate consecutive identical paragraphs
    deduped_paragraphs = []
    prev_para = None
    for para in paragraphs:
        p_clean = para.strip()
        if not p_clean:
            continue
        if p_clean != prev_para:
            deduped_paragraphs.append(p_clean)
            prev_para = p_clean

    return "\n\n".join(deduped_paragraphs)


# ---------------------------------------------------------------------------
# Full Preprocessing Pipeline
# ---------------------------------------------------------------------------
def run_dataset_pipeline():
    """
    Executes dataset pipeline across all category subdirectories in raw_cases:
    raw_cases/*/*.txt -> cleaned/ -> normalized/ -> ready_for_embedding/
    """
    print("=" * 60)
    print("STARTING DATASET PREPROCESSING PIPELINE")
    print("=" * 60)

    # Ensure directories exist
    os.makedirs(CLEANED_DIR, exist_ok=True)
    os.makedirs(NORMALIZED_DIR, exist_ok=True)
    os.makedirs(READY_FOR_EMBEDDING_DIR, exist_ok=True)

    processed_count = 0

    # Walk raw_cases directory dynamically (category agnostic for scalability)
    for root, subdirs, files in os.walk(RAW_CASES_DIR):
        for file in files:
            if file.endswith(".txt") and not file.startswith("."):
                raw_file_path = os.path.join(root, file)

                # Determine category relative path
                rel_path = os.path.relpath(raw_file_path, RAW_CASES_DIR)
                print(f"\n[Processing] Raw File: {rel_path}")

                # Read raw text
                with open(raw_file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_content = f.read()

                # Stage 1: Clean
                cleaned_content = clean_text(raw_content)
                cleaned_target = os.path.join(CLEANED_DIR, file)
                with open(cleaned_target, "w", encoding="utf-8") as f:
                    f.write(cleaned_content)
                print(f"  -> Stage 1 (Cleaned)              -> {os.path.relpath(cleaned_target, BASE_DIR)}")

                # Stage 2: Normalize
                normalized_content = normalize_text(cleaned_content)
                normalized_target = os.path.join(NORMALIZED_DIR, file)
                with open(normalized_target, "w", encoding="utf-8") as f:
                    f.write(normalized_content)
                print(f"  -> Stage 2 (Normalized)           -> {os.path.relpath(normalized_target, BASE_DIR)}")

                # Stage 3: Ready for Embedding
                ready_target = os.path.join(READY_FOR_EMBEDDING_DIR, file)
                with open(ready_target, "w", encoding="utf-8") as f:
                    f.write(normalized_content)
                print(f"  -> Stage 3 (Ready for Embedding)  -> {os.path.relpath(ready_target, BASE_DIR)}")

                processed_count += 1

    print("\n" + "=" * 60)
    print(f"PIPELINE COMPLETE: Processed {processed_count} judgments successfully.")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Metadata Loader
# ---------------------------------------------------------------------------
def load_metadata_lookup() -> dict:
    """Loads metadata CSV and returns a dictionary indexed by file name."""
    if not os.path.exists(METADATA_FILE):
        print(f"Warning: Metadata file not found at {METADATA_FILE}")
        return {}

    try:
        df = pd.read_csv(METADATA_FILE)
        metadata_map = {}
        for _, row in df.iterrows():
            filename = str(row.get("File Name", "")).strip()
            if filename:
                metadata_map[filename.lower()] = {
                    "case_id": str(row.get("Case ID", "")),
                    "case_title": str(row.get("Case Title", "")),
                    "court": str(row.get("Court", "")),
                    "state": str(row.get("State", "")),
                    "year": int(row.get("Year")) if pd.notnull(row.get("Year")) and str(row.get("Year")).isdigit() else None,
                    "case_type": str(row.get("Case Type", "")),
                    "citation": str(row.get("Citation", "")),
                    "source_dataset": str(row.get("Source Dataset", "")),
                    "file_name": filename,
                    "keywords": str(row.get("Keywords", "")),
                }
        return metadata_map
    except Exception as e:
        print(f"Error reading metadata CSV: {e}")
        return {}


# ---------------------------------------------------------------------------
# Document Loading & Text Chunking
# ---------------------------------------------------------------------------
def load_and_chunk_documents(target_dir: str = READY_FOR_EMBEDDING_DIR, chunk_size: int = 500, chunk_overlap: int = 50):
    """
    Loads documents exclusively from data/processed_cases/ready_for_embedding/,
    attaches metadata, and splits into chunks.
    """
    # Strict validation rule: Never index raw_cases directly
    abs_target = os.path.abspath(target_dir)
    abs_raw = os.path.abspath(RAW_CASES_DIR)

    if abs_target.startswith(abs_raw) or abs_raw.startswith(abs_target):
        raise ValueError("SECURITY DISALLOWED: Loading directly from raw_cases folder is prohibited! Documents must be loaded from ready_for_embedding.")

    if not abs_target.endswith("ready_for_embedding"):
        print(f"Notice: Target directory is {abs_target}. Ensure this is a sanitized directory.")

    print(f"\nLoading documents from: {abs_target}")

    from langchain_community.document_loaders import DirectoryLoader, TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    loader = DirectoryLoader(
        abs_target,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    raw_docs = loader.load()
    print(f"Loaded {len(raw_docs)} document(s) from ready_for_embedding.")

    # Load metadata lookup map
    metadata_map = load_metadata_lookup()

    # Enrich documents with metadata
    enriched_docs = []
    for doc in raw_docs:
        source_path = doc.metadata.get("source", "")
        basename = os.path.basename(source_path).lower()

        # Retrieve metadata or set defaults
        meta_attributes = metadata_map.get(basename, {
            "case_id": "UNKNOWN",
            "case_title": os.path.basename(source_path),
            "court": "Unknown Court",
            "state": "Unknown",
            "year": None,
            "case_type": "General",
            "citation": "N/A",
            "source_dataset": "Processed Cases",
            "file_name": os.path.basename(source_path),
            "keywords": "",
        })

        # Merge metadata attributes
        for key, val in meta_attributes.items():
            doc.metadata[key] = val

        enriched_docs.append(doc)

    # Perform text chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(enriched_docs)
    print(f"Split {len(enriched_docs)} document(s) into {len(chunks)} text chunk(s).")
    return chunks


# ---------------------------------------------------------------------------
# ChromaDB Vector Store Indexing
# ---------------------------------------------------------------------------
def build_vector_store():
    """
    Loads normalized ready_for_embedding documents, generates HuggingFace embeddings,
    and stores chunks into persistent ChromaDB.
    """
    print("=" * 60)
    print("BUILDING CHROMADB VECTOR STORE")
    print("=" * 60)

    try:
        from langchain_huggingface import HuggingFaceEmbeddings
    except ImportError:
        from langchain_community.embeddings import HuggingFaceEmbeddings

    try:
        from langchain_chroma import Chroma
    except ImportError:
        from langchain_community.vectorstores import Chroma

    # 1. Load & Chunk
    chunks = load_and_chunk_documents()

    if not chunks:
        print("No document chunks found to index. Run --process first.")
        return None

    # 2. Embeddings Model
    embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"Initializing HuggingFace Embedding model: '{embedding_model_name}'...")
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

    # 3. Initialize / Update Chroma Vector Store
    print(f"Persisting vector store to: {CHROMA_DB_DIR}")

    batch_size = 500
    vector_store = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings,
        collection_name="legal_cases"
    )

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        print(f"Indexing batch {i // batch_size + 1} / {(len(chunks) - 1) // batch_size + 1} ({len(batch)} chunks)...")
        vector_store.add_documents(batch)

    print("Successfully indexed chunks into ChromaDB.")
    return vector_store


# ---------------------------------------------------------------------------
# Vector Store Query Interface
# ---------------------------------------------------------------------------
def query_vector_store(query_text: str, k: int = 3):
    """Queries persistent ChromaDB for top matching chunks."""
    print("=" * 60)
    print(f"QUERYING VECTOR STORE: '{query_text}'")
    print("=" * 60)

    try:
        from langchain_huggingface import HuggingFaceEmbeddings
    except ImportError:
        from langchain_community.embeddings import HuggingFaceEmbeddings

    try:
        from langchain_chroma import Chroma
    except ImportError:
        from langchain_community.vectorstores import Chroma

    embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

    vector_store = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings,
        collection_name="legal_cases"
    )

    results = vector_store.similarity_search(query_text, k=k)

    print(f"\nFound {len(results)} matching document chunk(s):\n")
    for idx, doc in enumerate(results, start=1):
        print(f"--- [Result {idx}] ---")
        print(f"Case ID    : {doc.metadata.get('case_id')}")
        print(f"Case Title : {doc.metadata.get('case_title')}")
        print(f"Court      : {doc.metadata.get('court')}")
        print(f"Year       : {doc.metadata.get('year')}")
        print(f"Case Type  : {doc.metadata.get('case_type')}")
        print(f"Citation   : {doc.metadata.get('citation')}")
        print(f"File Name  : {doc.metadata.get('file_name')}")
        print(f"Content Snippet:\n{doc.page_content.strip()}")
        print("-" * 40 + "\n")

    return results


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Legal Dataset Pipeline & Chroma Vector Store Utility")
    parser.add_argument("--ingest", action="store_true", help="Ingest real dataset from CSV file")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of real cases to ingest")
    parser.add_argument("--process", action="store_true", help="Run raw -> cleaned -> normalized -> ready_for_embedding pipeline")
    parser.add_argument("--index", action="store_true", help="Chunk ready_for_embedding documents and build ChromaDB index")
    parser.add_argument("--query", type=str, help="Search the vector store with a text query")

    args = parser.parse_args()

    if not any([args.ingest, args.process, args.index, args.query]):
        parser.print_help()
        return

    if args.ingest:
        from ingest_real_dataset import ingest_real_dataset
        ingest_real_dataset(limit=args.limit)

    if args.process:
        run_dataset_pipeline()

    if args.index:
        build_vector_store()

    if args.query:
        query_vector_store(args.query)


if __name__ == "__main__":
    main()
