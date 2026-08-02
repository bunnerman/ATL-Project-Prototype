import io
import zipfile
import tempfile
import os
from xml.etree import ElementTree as ET

import streamlit as st
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract

# Talk to the AI backend and get the results
def get_backend_result(user_text: str):
    try:
        from sarthak_brain import ai_brain_app
    except Exception as e:
        return {
            "status": "Error",
            "final_report": "",
            "retry_count": 0,
            "error_message": f"Could not load AI: {e}",
        }

    response = ai_brain_app.invoke({"pdf_text": user_text})
    return {
        "status": response.get("status", "Error"),
        "final_report": response.get("final_report", ""),
        "retry_count": response.get("retry_count", 0),
        "error_message": response.get("error_message", ""),
    }

# Read PDF directly first and fallback to OCR if it is a scanned image
def extract_pdf_text(uploaded_file) -> str:
    try:
        reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
        pages = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text.strip())

        standard_text = "\n\n".join(pages).strip()

        if len(standard_text) > 50:
            return standard_text
    except Exception:
        pass 

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.getvalue())
        pdf_path = temp_pdf.name

    try:
        images = convert_from_path(pdf_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
        return text.strip()
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

# Unzip the Word document and pull out all the paragraph text
def extract_docx_text(uploaded_file) -> str:
    with zipfile.ZipFile(io.BytesIO(uploaded_file.getvalue())) as docx:
        with docx.open("word/document.xml") as xml_file:
            root = ET.fromstring(xml_file.read())

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []

    for p in root.findall(".//w:p", ns):
        texts = [node.text for node in p.findall(".//w:t", ns) if node.text]
        if texts:
            paragraphs.append("".join(texts).strip())

    return "\n\n".join(paragraphs).strip()

# Combine the user chat message with the text from their uploaded files
def build_backend_input(user_text: str, uploaded_files) -> str:
    chunks = []

    if user_text.strip():
        chunks.append(f"User Query: {user_text.strip()}")

    for file in uploaded_files or []:
        name = file.name.lower()
        try:
            if name.endswith(".pdf"):
                text = extract_pdf_text(file)
            elif name.endswith(".docx"):
                text = extract_docx_text(file)
            else:
                text = ""
        except Exception as e:
            text = f"Failed to read {file.name}: {e}"

        if text.strip():
            chunks.append(f"Document ({file.name}):\n{text.strip()}")

    return "\n\n---\n\n".join(chunks).strip()

# Draw a chat bubble on the screen
def render_message(message):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("files"):
            st.caption("Attached Files:")
            for file in message["files"]:
                st.write(f"{file.name} ({file.size} bytes)")

# Show the final AI report or error on the screen
def render_backend_result(result: dict):
    if result.get("final_report"):
        st.markdown(result["final_report"])
    elif result.get("error_message"):
        st.error(result["error_message"])
    else:
        st.warning("No response from the backend.")

# App layout and settings
st.set_page_config(
    page_title="ATL Legal Assistant",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Set up memory to remember the chat and the last AI response
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# Main page header
st.title("ATL Legal Assistant")
st.write("Submit a legal query or upload a document for analysis.")

if not st.session_state.messages:
    st.info("Awaiting input. The system will extract text and route it to the backend.")

# Display all past messages
for message in st.session_state.messages:
    render_message(message)

# Create an empty placeholder space right above the divider for the loading animation
loading_placeholder = st.empty()

st.divider()

# Create space so messages do not hide behind the input box
st.markdown("<div></div>", unsafe_allow_html=True)

# The chat input box at the bottom of the screen
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

user_input = st.chat_input(
    "Enter text...",
    accept_file="multiple",
    file_type=["pdf", "docx"]
)

st.markdown("</div>", unsafe_allow_html=True)

# When the user hits send
if user_input:
    # Save the user message to the chat memory
    st.session_state.messages.append({
        "role": "user",
        "content": user_input.text,
        "files": user_input.files,
    })

    # Put the loading animation inside the empty placeholder we created earlier
    with loading_placeholder:
        with st.spinner("Processing documents and analyzing legal data..."):
            backend_input = build_backend_input(user_input.text, user_input.files)
            result = get_backend_result(backend_input)

    st.session_state.last_result = result
    assistant_text = result.get("final_report") or result.get("error_message") or "No response returned."

    # Save the AI response to the chat memory
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_text,
        "files": [],
    })

    # Reload the page to show the new messages
    st.rerun()
