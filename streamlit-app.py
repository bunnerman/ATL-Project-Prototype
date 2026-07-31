import streamlit as st
import fitz
import io
from PIL import Image
import os
import pytesseract

tesseract_path = os.getenv("TESSERACT_PATH")

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

from sarthak_brain import ai_brain_app

# Page settings
st.set_page_config(
    page_title="ATL",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #f3f3f3 !important;
}

[data-testid="stAppViewContainer"] {
    background: #f3f3f3 !important;
}

[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 12px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

[data-testid="stChatMessage"] *,
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] li {
    color: #000000 !important;
}

.chat-container {
    position: fixed;
    bottom: 25px;
    left: 50%;
    transform: translateX(-50%);
    width: 75%;
    z-index: 999;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 140px !important;
}
</style>
""", unsafe_allow_html=True)

# Create chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

        # Show uploaded files
        if msg.get("files"):
            for uploaded_file in msg["files"]:
                st.write(uploaded_file.name, uploaded_file.size)

# Chat input area
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

# Input box
user_input = st.chat_input(
    "Type something...",
    accept_file="multiple",
    file_type=["pdf", "docx"]
)

st.markdown("</div>", unsafe_allow_html=True)

# Run when user sends message
if user_input:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input.text,
        "files": user_input.files,
    })

    # Check uploaded files
    if user_input.files:

        for uploaded_file in user_input.files:

            # Read PDF
            with st.spinner(f"Scanning {uploaded_file.name}..."):

                pdf = fitz.open(
                    stream=uploaded_file.getvalue(),
                    filetype="pdf"
                )

                text = ""

                # Read every page
                for page in pdf:

                    pixmap = page.get_pixmap(dpi=200)

                    image = Image.open(
                        io.BytesIO(pixmap.tobytes("png"))
                    )

                    text += pytesseract.image_to_string(image)
                    text += "\n"

                pdf.close()

            # Send text to AI
            with st.status("Thinking...", expanded=True) as status:

                st.write("Extracting legal facts and timeline...")
                st.write("Searching legal database for Supreme Court precedents...")

                result = ai_brain_app.invoke({
                    "pdf_text": text
                })

                report = result["final_report"]

                status.update(
                    label="Thinking complete!",
                    state="complete",
                    expanded=False
                )

            # Save AI reply
            st.session_state.messages.append({
                "role": "assistant",
                "content": report,
                "files": []
            })

    # Refresh page
    st.rerun()
