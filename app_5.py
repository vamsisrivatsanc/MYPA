import streamlit as st
import ollama
import html
from datetime import datetime
import base64
import os

# ----------------------------
# App Configuration
# ----------------------------
st.set_page_config(page_title="Jarvis Chatbot", page_icon="🤖")
st.markdown("<h1 style='text-align: center;'>🤖 Jarvis</h1>", unsafe_allow_html=True)

# ----------------------------
# Session State Init
# ----------------------------
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'model' not in st.session_state:
    st.session_state.model = None

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

    if st.download_button("💾 Download Transcript", data="\n".join([f"{r}: {t}" for r, t in st.session_state.chat_history]), file_name="chat_transcript.txt"):
        pass

# ----------------------------
# File Upload: Under Chat Box
# ----------------------------
with st.container():
    uploaded_file = None
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("➕"):
            uploaded_file = st.file_uploader("Upload File", type=["txt", "pdf", "jpg", "png"], label_visibility="collapsed")
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
        # Optional: You can parse the file and add to messages here.

# ----------------------------
# Chat Input Area
# ----------------------------
with st.container():
    user_input = st.text_input("You:", placeholder="Type your message here...")

    if st.button("Send") and user_input:
        # Add user message
        st.session_state.chat_history.append(("You", user_input))
        messages = [{"role": "user", "content": user_input}]
        response = get_response(messages, st.session_state.model)
        st.session_state.chat_history.append(("Jarvis", html.escape(response)))

# ----------------------------
# Display Chat History
# ----------------------------
for role, message in st.session_state.chat_history:
    if role == "You":
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;margin-bottom:10px;">
                <div style="background:#f0f0f0;padding:10px;border-radius:10px;margin-left:10px;">
                    <strong>🧑 You:</strong> {message}
                </div>
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;margin-bottom:10px;">
                <div style="background:#d1e7dd;padding:10px;border-radius:10px;margin-left:10px;">
                    <strong>🤖 Jarvis:</strong> {message}
                </div>
            </div>
            """, unsafe_allow_html=True
        )
