import streamlit as st
import tempfile
import os
from pdf2image import convert_from_path
import pytesseract

# Import AI workflow
from sarthak_brain import ai_brain_app

# Page settings
st.set_page_config(
    page_title="ATL",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Page styling
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

html, body, [data-testid="stAppViewContainer"] {
    background-color: #f3f3f3;
}

[data-testid="stAppViewContainer"] {
    background: #f3f3f3;
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
    padding-top: 0rem;
    padding-bottom: 0rem;
}
</style>
""", unsafe_allow_html=True)

# Create chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show old messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):

        # Display message
        st.markdown(msg["content"])

        # Show uploaded files
        if msg.get("files"):
            for file in msg["files"]:
                st.write(file.name, file.size)

# Keep space for chat box
st.markdown("<div style='height:90vh'></div>", unsafe_allow_html=True)

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

# Chat input
user_input = st.chat_input(
    "Type something...",
    accept_file="multiple",
    file_type=["pdf", "docx"]
)

st.markdown("</div>", unsafe_allow_html=True)

# Run after sending message
if user_input:

    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input.text,
        "files": user_input.files,
    })

    # Process uploaded files
    if user_input.files:

        for file in user_input.files:

            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file.getvalue())
                pdf_path = temp_file.name

            # Convert PDF into images
            with st.spinner(f"Reading {file.name}..."):

                images = convert_from_path(pdf_path)
                extracted_text = ""

                # Read every page
                for image in images:
                    extracted_text += pytesseract.image_to_string(image)
                    extracted_text += "\n"

            # Remove temp file
            os.remove(pdf_path)

            # Send text to AI
            with st.spinner("Generating report..."):

                ai_result = ai_brain_app.invoke({
                    "pdf_text": extracted_text
                })

                final_report = ai_result["final_report"]

            # Save AI response
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_report,
                "files": []
            })

# Refresh page
    st.rerun()
