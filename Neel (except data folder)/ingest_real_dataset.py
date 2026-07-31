"""
ingest_real_dataset.py
Real Legal Dataset Ingestion & Preprocessing Utility

Ingests case judgments from F:\\Neel\\Projects\\Law\\jud-pl\\case_files_total.csv,
populates raw_cases directory structure, extracts metadata to case_metadata.csv,
and executes the dataset normalization pipeline.
"""

import os
import re
import argparse
import pandas as pd
from vector_store import (
    BASE_DIR, DATA_DIR, RAW_CASES_DIR, CLEANED_DIR, NORMALIZED_DIR,
    READY_FOR_EMBEDDING_DIR, METADATA_FILE, run_dataset_pipeline, clean_text, normalize_text
)

CSV_DEFAULT_PATH = r"F:\Neel\Projects\Law\jud-pl\case_files_total.csv"


def classify_legal_domain(case_category: str, case_type: str, case_info: str, judgement: str) -> str:
    """Classifies a legal case into a specific domain folder based on content keywords."""
    text = f"{case_category} {case_type} {case_info} {judgement[:800]}".lower()

    if re.search(r"\b(tax|excise|customs|income tax|vat|gst|assessment|revenue)\b", text):
        return "taxation"
    if re.search(r"\b(contract|arbitration|agreement|indemnity|breach of contract|guarantee)\b", text):
        return "contracts"
    if re.search(r"\b(property|land|tenancy|eviction|partition|mortgage|possession|title deed|real estate|lease)\b", text):
        return "property"
    if re.search(r"\b(consumer|deficiency|consumer forum|compensation|negligence)\b", text):
        return "consumer"
    if re.search(r"\b(family|marriage|divorce|matrimonial|maintenance|custody|guardianship|adoption)\b", text):
        return "family"
    if re.search(r"\b(labour|labor|workmen|industrial dispute|gratuity|provident fund|wages|factory)\b", text):
        return "labour"
    if re.search(r"\b(commercial|company|shares|insolvency|ibc|banking|cheque|negotiable instrument)\b", text):
        return "commercial"
    if re.search(r"\b(constitutional|article 32|article 226|fundamental right|writ petition)\b", text):
        return "constitutional"
    if "criminal" in text or "ipc" in text or "bail" in text or "accused" in text or "penal code" in text:
        return "criminal"
    return "civil"


def extract_metadata_from_row(row, idx: int) -> dict:
    """Extracts structured metadata fields from a row of case_files_total.csv."""
    raw_name = str(row.get("name", "")).strip()
    if not raw_name or raw_name.lower() == "nan":
        file_name = f"case_{idx:05d}.txt"
        case_id = f"CASE-{idx:05d}"
    else:
        file_name = raw_name if raw_name.endswith(".txt") else f"{raw_name}.txt"
        case_id = raw_name.replace(".txt", "")

    case_category = str(row.get("case_category", "")).strip()
    case_type = str(row.get("case_type", "")).strip()
    case_info = str(row.get("case_info", "")).strip()
    judgement = str(row.get("judgement", "")).strip()
    label = str(row.get("label", "")).strip()

    # Determine specific domain folder
    domain = classify_legal_domain(case_category, case_type, case_info, judgement)

    # Extract title from case_info or default
    title = ""
    if case_info and case_info.lower() != "nan":
        # Look for vs / versus pattern
        vs_match = re.search(r"([A-Za-z0-9\.\s]+(?:versus|vs\.?|v\.?)[A-Za-z0-9\.\s]+)", case_info, re.IGNORECASE)
        if vs_match:
            title = vs_match.group(1).strip()
            title = re.sub(r"\s+", " ", title)[:120]

    if not title:
        # Take first 100 characters of case_info or judgement
        text_source = case_info if case_info and case_info.lower() != "nan" else judgement
        first_line = text_source.split("\n")[0].strip()
        title = first_line[:100] if first_line else f"Legal Case {case_id}"

    # Extract court name
    combined_header = f"{case_info}\n{judgement[:500]}".lower()
    if "supreme court of india" in combined_header:
        court = "Supreme Court of India"
    elif "high court of delhi" in combined_header or "delhi high court" in combined_header:
        court = "High Court of Delhi"
    elif "high court of bombay" in combined_header or "bombay high court" in combined_header:
        court = "High Court of Bombay"
    elif "high court of karnataka" in combined_header:
        court = "High Court of Karnataka"
    elif "high court" in combined_header:
        court = "High Court of Judicature"
    else:
        court = "Apex Legal Tribunal"

    # Extract state
    state = "India"
    states_list = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "West Bengal", "Gujarat", "Kerala", "Punjab", "Rajasthan"]
    for st in states_list:
        if st.lower() in combined_header:
            state = st
            break

    # Extract year
    year = None
    year_matches = re.findall(r"\b(19[5-9]\d|20[0-2]\d)\b", combined_header)
    if year_matches:
        year = int(year_matches[-1])  # Take recent matched year

    # Generate keywords
    keywords_list = [k for k in [case_category, case_type, label] if k and k.lower() != "nan"]
    keywords = ", ".join(keywords_list)

    return {
        "Case ID": case_id,
        "Case Title": title.replace('"', "'"),
        "Court": court,
        "State": state,
        "Year": year if year else 2023,
        "Case Type": case_type.title() if case_type and case_type.lower() != "nan" else domain.title(),
        "Citation": f"{year if year else 2023} IND {case_id}",
        "Source Dataset": "jud-pl Real Dataset",
        "File Name": file_name,
        "Keywords": keywords if keywords else domain,
        "_category": domain.lower(),
        "_case_info": case_info if case_info.lower() != "nan" else "",
        "_judgement": judgement if judgement.lower() != "nan" else "",
    }


def ingest_real_dataset(csv_path: str = CSV_DEFAULT_PATH, limit: int = None):
    """
    Reads the CSV, extracts raw files to data/raw_cases/<category>/<filename>,
    writes metadata to case_metadata.csv, and runs the dataset pipeline.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Real dataset CSV not found at: {csv_path}")

    print("=" * 60)
    print(f"INGESTING REAL DATASET FROM: {csv_path}")
    print("=" * 60)

    # Read CSV
    print("Reading CSV dataset...")
    df = pd.read_csv(csv_path)
    total_rows = len(df)
    print(f"Total rows in dataset: {total_rows}")

    # Filter out rows missing judgment content
    valid_df = df.dropna(subset=["judgement"]).copy()
    print(f"Valid judgment rows: {len(valid_df)}")

    if limit and limit > 0:
        valid_df = valid_df.head(limit)
        print(f"Processing limit set to: {limit} cases.")

    metadata_records = []
    extracted_count = 0

    # Ensure directories
    os.makedirs(RAW_CASES_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)

    for idx, row in valid_df.iterrows():
        meta = extract_metadata_from_row(row, idx)

        category = meta["_category"]
        category_dir = os.path.join(RAW_CASES_DIR, category)
        os.makedirs(category_dir, exist_ok=True)

        # Assemble full text
        case_info = meta["_case_info"]
        judgement = meta["_judgement"]

        full_text_parts = []
        if case_info:
            full_text_parts.append("--- PREAMBLE & CASE INFO ---")
            full_text_parts.append(case_info)
        full_text_parts.append("--- JUDGMENT BODY ---")
        full_text_parts.append(judgement)

        raw_text = "\n\n".join(full_text_parts)
        file_path = os.path.join(category_dir, meta["File Name"])

        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(raw_text)

        # Prepare CSV record (excluding internal underscore keys)
        clean_record = {k: v for k, v in meta.items() if not k.startswith("_")}
        metadata_records.append(clean_record)

        extracted_count += 1
        if extracted_count % 500 == 0:
            print(f"Extracted {extracted_count} / {len(valid_df)} raw cases...")

    # Write case_metadata.csv
    meta_df = pd.DataFrame(metadata_records)
    meta_df.to_csv(METADATA_FILE, index=False)
    print(f"\nSaved {len(meta_df)} metadata records to: {METADATA_FILE}")

    print("\nExecuting normalization pipeline on ingested real cases...")
    run_dataset_pipeline()

    print("\n" + "=" * 60)
    print(f"REAL DATASET INGESTION COMPLETE: {extracted_count} cases processed.")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Ingest and Preprocess Real Legal Dataset CSV")
    parser.add_argument("--csv", type=str, default=CSV_DEFAULT_PATH, help="Path to case_files_total.csv")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cases to ingest (for fast testing/indexing)")
    args = parser.parse_args()

    ingest_real_dataset(csv_path=args.csv, limit=args.limit)


if __name__ == "__main__":
    main()
