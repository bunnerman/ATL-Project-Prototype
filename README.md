## 🔴🔴 Deadline on Sunday 🔴🔴

The ATL Project given by them aims to be a AI legal evidence verifier/helper

- **Do majority of the work before Saturday**
- Test, debug and polish on the weekend
- Understand the code
- Prototype bare minimum should be just working ig?
- Make folders when required (empty folders won't commit)

**Other Stuff**
- `streamlit-app.py`: https://atl-project-prototype-nhrtbq5lkkmffezqjarzkf.streamlit.app
- `streamlit-testing.py`: https://atl-project-prototype-3imqmecugmwxpqzuug6v9s.streamlit.app

## Progress

_**Modify to ur liking as jobs did change abit after that AI msg**_

- **Parnil:**
  - [x] Streamlit Community Cloud
  - [ ] Gemini API Key + Secrets
  - [x] Dependencies
  - [x] Up and Running?
- **Neel:** 0%
  - [ ] Structuring Case Corpus
  - [ ] Configure HuggingFace models
  - [ ] Text Chunking
  - [ ] Vector Index
- **Adarsh:** 0%
  - [ ] File Uploading Component
  - [ ] Temporary File Storage
  - [ ] PyPDF Text Extraction
- **Sarthak:** 0%
  - [ ] Langchain
    - [ ] Gemini 1.5 Flash Setup
  - [ ] Prompt Templates
  - [ ] Timeline Extraction Module
- **Namya:** 0%
  - [ ] Connecting timeline output to NeonDB
  - [ ] Similiarity searches
  - [ ] Rendering Streamlit UI outputs

### Work Division Summary

_**Modify to be more accurate as jobs did change abit after that AI msg**_

- **Parnil**: Setting up the repository, handling dependency management, configuring secrets, and managing Streamlit Community Cloud hosting.
- **Neel**: Structuring the case corpus, configuring HuggingFace embedding models, chunking text, and building the vector index.
- **Adarsh**: Building the file uploader component, handling temporary file storage, and executing PyPDF text extraction.
- **Sarthak**: Initializing Gemini 1.5 Flash via LangChain, crafting prompt templates, and executing the timeline extraction chain.
- **Namya**: Connecting the timeline output to the NeonDB retriever, performing similarity searches, and rendering Streamlit UI outputs.

### Dependencies
1. streamlit
2. langchain
3. langchain-google-genai
4. langchain-huggingface
5. langchain-chroma
6 langchain-community
7. pypdf
8. chromadb
9. sentence-transformers

**For installation, use** 
`pip install streamlit fastapi uvicorn langchain langchain-groq langchain-huggingface langchain-chroma pypdf chromadb sentence-transformers python-multipart requests`
