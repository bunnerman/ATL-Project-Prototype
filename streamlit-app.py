import io
import zipfile
from xml.etree import ElementTree as ET

import streamlit as st
from pypdf import PdfReader


def get_backend_result(user_text: str):
    try:
        from sarthak_brain import ai_brain_app
    except Exception as exc:
        return {
            "status": "ERROR",
            "final_report": "",
            "retry_count": 0,
            "error_message": f"Backend could not start: {exc}",
        }

    response = ai_brain_app.invoke({"pdf_text": user_text})
    return {
        "status": response.get("status", "ERROR"),
        "final_report": response.get("final_report", ""),
        "retry_count": response.get("retry_count", 0),
        "error_message": response.get("error_message", ""),
    }


def extract_pdf_text(uploaded_file) -> str:
    reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
    pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(page_text.strip())

    return "\n\n".join(pages).strip()


def extract_docx_text(uploaded_file) -> str:
    with zipfile.ZipFile(io.BytesIO(uploaded_file.getvalue())) as docx_zip:
        with docx_zip.open("word/document.xml") as document_xml:
            root = ET.fromstring(document_xml.read())

    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []

    for paragraph in root.findall(".//w:p", namespace):
        texts = [node.text for node in paragraph.findall(".//w:t", namespace) if node.text]
        paragraph_text = "".join(texts).strip()
        if paragraph_text:
            paragraphs.append(paragraph_text)

    return "\n\n".join(paragraphs).strip()


def build_backend_input(user_text: str, uploaded_files) -> str:
    chunks = []

    if user_text.strip():
        chunks.append(user_text.strip())

    for uploaded_file in uploaded_files or []:
        file_name = uploaded_file.name.lower()

        try:
            if file_name.endswith(".pdf"):
                extracted_text = extract_pdf_text(uploaded_file)
            elif file_name.endswith(".docx"):
                extracted_text = extract_docx_text(uploaded_file)
            else:
                extracted_text = ""
        except Exception as exc:
            extracted_text = f"[Could not extract text from {uploaded_file.name}: {exc}]"

        if extracted_text.strip():
            chunks.append(f"FILE: {uploaded_file.name}\n{extracted_text.strip()}")

    return "\n\n---\n\n".join(chunks).strip()


def render_message(message):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        files = message.get("files", [])
        if files:
            st.caption("Uploaded files")
            for file in files:
                st.write(f"{file.name} ({file.size} bytes)")


def render_backend_result(result: dict):
    status = result.get("status", "ERROR")
    final_report = result.get("final_report", "")
    retry_count = result.get("retry_count", 0)
    error_message = result.get("error_message", "")

    st.markdown("### Backend Response")
    st.caption(f"Status: {status} | Retries: {retry_count}")

    if final_report:
        st.markdown(final_report)
    elif error_message:
        st.error(error_message)
    else:
        st.warning("No response was returned from the backend.")
st.set_page_config(
    page_title="ATL",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hiding Streamlit normal elements
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #000000;
    color: #f5f5f5;
}

[data-testid="stAppViewContainer"] {
    background: #000000;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #f5f5f5;
}

/* Bottom input container */
.chat-container {
    position: fixed;
    bottom: 25px;
    left: 50%;
    transform: translateX(-50%);
    width: 75%;
    z-index: 999;
}

/* Remove default spacing */
.block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
}

.stAlert {
    background-color: #111111;
    color: #f5f5f5;
}

.stCaption {
    color: #cccccc;
}

.stButton button {
    background-color: #1f1f1f;
    color: #f5f5f5;
    border: 1px solid #444444;
}

.stButton button:hover {
    background-color: #2a2a2a;
    color: #ffffff;
    border: 1px solid #666666;
}

.stChatInput textarea {
    background-color: #111111 !important;
    color: #f5f5f5 !important;
    border: 1px solid #444444 !important;
}

.stChatInput textarea::placeholder {
    color: #aaaaaa !important;
}

.stFileUploader {
    background-color: #111111;
    color: #f5f5f5;
    border: 1px solid #444444;
    border-radius: 8px;
    padding: 0.5rem;
}

.stFileUploader label,
.stFileUploader small,
.stFileUploader p {
    color: #f5f5f5 !important;
}
</style>
""", unsafe_allow_html=True)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

st.title("ATL Legal Assistant")
st.write("Type a legal question or upload a document. The app will send it to Sarthak's backend and show the result below.")

if not st.session_state.messages:
    st.info("Ask a question or upload a file to begin. The app will extract text and pass it to the backend.")

# Display previous messages
for message in st.session_state.messages:
    render_message(message)

if st.session_state.last_result:
    with st.container(border=True):
        render_backend_result(st.session_state.last_result)

st.markdown("---")

# Spacer so messages don't hide behind the input box
st.markdown("<div style='height:90vh'></div>", unsafe_allow_html=True)

# User input TextBox

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

user_input = st.chat_input(
    "Type something...",
    accept_file="multiple",
    file_type=["pdf", "docx"]
)

st.markdown("</div>", unsafe_allow_html=True)

# Save new user message
if user_input:
    backend_input = build_backend_input(user_input.text, user_input.files)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input.text,
        "files": user_input.files,
    })

    with st.spinner("Sending text to Sarthak's backend..."):
        result = get_backend_result(backend_input)

    st.session_state.last_result = result
    assistant_text = result.get("final_report") or result.get("error_message") or "No response returned."

    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_text,
        "files": [],
    })

    # Force the page to redraw with the new message
    st.rerun()
