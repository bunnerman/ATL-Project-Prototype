from importlib.metadata import files
import streamlit as st

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

html, body, [data-testid="stAppViewContainer"] {
    background-color: #f3f3f3;
}

[data-testid="stAppViewContainer"] {
    background: #f3f3f3;
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
</style>
""", unsafe_allow_html=True)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["files"]:
            for file in message["files"]:
                st.write( file.name,file.size)

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
    st.session_state.messages.append({
        "role": "user",
        "content": user_input.text,
        "files": user_input.files,
    })

    # Force the page to redraw with the new message
    st.rerun()
