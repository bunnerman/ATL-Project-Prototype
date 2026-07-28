# 🔴🔴 Deadline on Sunday 🔴🔴
- Do majority of the work on/before Friday
- Test, debug and polish on the weekend
- Prototype should be functional

- Gemini Link: https://gemini.google.com/share/4c74d3cd4131?skid=061fc2f4-a9ea-4146-90ab-2e81875cd3ce
- 

### Work Division Summary

Parnil: Setting up the repository, handling dependency management, configuring secrets, and managing Streamlit Community Cloud hosting.
Neel: Structuring the case corpus, configuring HuggingFace embedding models, chunking text, and building the vector index.
Adarsh: Building the file uploader component, handling temporary file storage, and executing PyPDF text extraction.
Sarthak: Initializing Gemini 1.5 Flash via LangChain, crafting prompt templates, and executing the timeline extraction chain.
Namya: Connecting the timeline output to the ChromaDB retriever, performing similarity searches, and rendering Streamlit UI outputs.


### Dependencies
streamlit
langchain
langchain-google-genai
langchain-huggingface
langchain-chroma
langchain-community
pypdf
chromadb
sentence-transformers

**For installation, use** 
`pip install streamlit fastapi uvicorn langchain langchain-groq langchain-huggingface langchain-chroma pypdf chromadb sentence-transformers python-multipart requests`



