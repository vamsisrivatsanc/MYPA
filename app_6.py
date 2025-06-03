import streamlit as st
import ollama
import html
from datetime import datetime

# ----------------------------
# App Configuration
# ----------------------------
st.set_page_config(page_title="Jarvis Chatbot", page_icon="🤖", layout="centered")
st.markdown("<h1 style='text-align: center;'>🤖 Jarvis</h1>", unsafe_allow_html=True)

# ----------------------------
# Session State Init
# ----------------------------
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'model' not in st.session_state:
    st.session_state.model = None

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# ----------------------------
# Helper: Get Local Models
# ----------------------------
def get_local_models():
    try:
        model_data = ollama.list()
        return [m.get("model", "Unnamed Model") for m in model_data.get("models", [])]
    except Exception as e:
        st.warning(f"⚠️ Could not fetch models: {e}")
        return []

# ----------------------------
# Helper: LLM Response
# ----------------------------
def get_response(messages, model):
    try:
        response = ollama.chat(model, messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"

# ----------------------------
# Sidebar: Controls
# ----------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    model_names = get_local_models()
    selected_model = st.selectbox("🧠 Choose a model", model_names, index=0 if model_names else None)
    st.session_state.model = selected_model

    if st.button("🧹 Reset Chat"):
        st.session_state.chat_history = []

    st.download_button(
        "💾 Download Transcript",
        data="\n".join([f"{r}: {t}" for r, t in st.session_state.chat_history]),
        file_name="chat_transcript.txt"
    )

# ----------------------------
# Main Chat Display
# ----------------------------
st.markdown("<div style='height:70vh; overflow-y:scroll; padding-right:10px;'>", unsafe_allow_html=True)
for role, message in st.session_state.chat_history:
    if role == "You":
        st.markdown(
            f"""
            <div style="margin-bottom:10px;">
                <div style="background:#f0f0f0;padding:10px;border-radius:10px;max-width:80%;margin-left:auto;">
                    <strong>🧑 You:</strong><br> {message}
                </div>
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="margin-bottom:10px;">
                <div style="background:#d1e7dd;padding:10px;border-radius:10px;max-width:80%;margin-right:auto;">
                    <strong>🤖 Jarvis:</strong><br> {message}
                </div>
            </div>
            """, unsafe_allow_html=True
        )
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Chat Input Box (Bottom Fixed Style)
# ----------------------------
with st.container():
    col1, col2 = st.columns([10, 2])
    with col1:
        user_text = st.text_area(
            "Type your message...",
            value=st.session_state.user_input,
            label_visibility="collapsed",
            height=80,
            key="chat_input"
        )

    with col2:
        if st.button("Send"):
            if user_text.strip() and st.session_state.model:
                st.session_state.chat_history.append(("You", user_text.strip()))
                messages = [{"role": "user", "content": user_text.strip()}]
                response = get_response(messages, st.session_state.model)
                st.session_state.chat_history.append(("Jarvis", html.escape(response)))
                st.session_state.user_input = ""  # Clear input
                st.experimental_rerun()

    # Upload button below the input
    uploaded_file = st.file_uploader("➕ Upload File", type=["txt", "pdf", "jpg", "png"], label_visibility="collapsed")
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
