## 🔴🔴 Deadline on Sunday 🔴🔴

The ATL Project given by them aims to be a AI legal evidence verifier/helper

- **Do majority of the work before Saturday**
- Test, debug and polish on the weekend
- Understand the code
- Prototype bare minimum should be just working ig?
- Make folders when required (empty folders won't commit)

## Progress

Put approx OR alternatively what's left and what's done

- **Parnil:** 0% 
- **Neel:** 0% 
- **Adarsh:** 0% 
- **Sarthak:** 0% 
- **Namya:** 0% 

**Other Stuff**
- Gemini Chat Link: https://gemini.google.com/share/4c74d3cd4131?skid=061fc2f4-a9ea-4146-90ab-2e81875cd3ce

### Work Division Summary

- **Parnil**: Setting up the repository, handling dependency management, configuring secrets, and managing Streamlit Community Cloud hosting.
- **Neel**: Structuring the case corpus, configuring HuggingFace embedding models, chunking text, and building the vector index.
- **Adarsh**: Building the file uploader component, handling temporary file storage, and executing PyPDF text extraction.
- **Sarthak**: Initializing Gemini 1.5 Flash via LangChain, crafting prompt templates, and executing the timeline extraction chain.
- **Namya**: Connecting the timeline output to the ChromaDB retriever, performing similarity searches, and rendering Streamlit UI outputs.

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
