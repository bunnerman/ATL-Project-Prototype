# The main page for the UI
import streamlit as st

st.set_page_config(
    page_title="ATL",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hiding Streamlit default elements
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

# Empty space
st.markdown("<div style='height:90vh'></div>", unsafe_allow_html=True)

# Bottom textbox
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

user_input = st.chat_input(
    "Type something..."
)

st.markdown("</div>", unsafe_allow_html=True)

# For testing
if user_input:
    st.write(user_input)
