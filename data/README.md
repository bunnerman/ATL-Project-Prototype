# Legal Case Dataset Management & Pipeline

This directory contains the dataset structure and pipeline for managing legal case judgments in raw and processed stages.

## Directory Structure

```text
data/
│
├── raw_cases/
│   ├── civil/
│   ├── property/
│   ├── criminal/
│   ├── contracts/
│   ├── consumer/
│   ├── family/
│   ├── labour/
│   ├── taxation/
│   ├── commercial/
│   └── constitutional/
│
├── processed_cases/
│   ├── cleaned/
│   ├── normalized/
│   └── ready_for_embedding/
│
├── metadata/
│   └── case_metadata.csv
│
└── README.md
```

## Dataset Pipeline Workflow

```text
Raw Judgments (data/raw_cases/*/*.txt)
        │
        ▼
Cleaning & Preprocessing (data/processed_cases/cleaned/)
        │
        ▼
Normalization (data/processed_cases/normalized/)
(Removes extra whitespace, invalid chars, duplicate paragraphs, page numbers, headers, footers, OCR artifacts)
        │
        ▼
Final Documents Ready for Embedding (data/processed_cases/ready_for_embedding/)
        │
        ▼
DirectoryLoader (Strictly loads from ready_for_embedding/)
        │
        ▼
Text Chunking & Metadata Attachment
        │
        ▼
HuggingFace Embeddings
        │
        ▼
ChromaDB Persistence (chroma_db/)
```

## Metadata Schema (`data/metadata/case_metadata.csv`)

The metadata CSV maintains key attributes for each judgment file:

| Column Header | Description | Example |
|---|---|---|
| `Case ID` | Unique case identifier | `CIV-2023-101` |
| `Case Title` | Title of the case / Parties involved | `Ramesh Sharma v. State of Maharashtra` |
| `Court` | Forum or court issuing judgment | `Supreme Court of India` |
| `State` | Jurisdiction / State | `Maharashtra` |
| `Year` | Year of judgment | `2023` |
| `Case Type` | Broad legal category | `Civil` |
| `Citation` | Official law reporter citation | `2023 SCC 451` |
| `Source Dataset` | Originating archive / repository | `District Court Archives` |
| `File Name` | Corresponding file name | `civil_case_001.txt` |
| `Keywords` | Comma-separated domain keywords | `civil, land dispute, damages` |

## Adding New Datasets & Categories

1. Create a new subfolder under `data/raw_cases/<new_category>/` (e.g. `data/raw_cases/taxation/`).
2. Add raw `.txt` judgment files into the subfolder.
3. (Optional) Add metadata records into `data/metadata/case_metadata.csv` matching the file name.
4. Run `python vector_store.py --process` to execute the preprocessing and normalization pipeline automatically.
5. Run `python vector_store.py --index` to update the ChromaDB vector index.
