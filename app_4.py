import streamlit as st
import ollama
import html
import base64
from datetime import datetime

st.set_page_config(page_title="Jarvis", layout="centered")
st.title("🤖 Jarvis")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "model_name" not in st.session_state:
    st.session_state.model_name = None

# Get list of available models
# try:
#     model_data = ollama.list()
#     st.write("Available models and their details:")
#     for model in model_data.get("models", []):
#         st.write(model)  # Display the entire model dictionary
# except Exception as e:
#     st.error(f"⚠️ Could not fetch models: {e}")
#     model_names = []
try:
    model_data = ollama.list()
    model_names = [m.get("model", "") for m in model_data.get("models", [])]
except Exception as e:
    st.error(f"⚠️ Could not fetch models: {e}")
    model_names = []

# Model selection dropdown
if model_names:
    selected_model = st.selectbox("Choose your LLM:", model_names, index=0)
    st.session_state.model_name = selected_model
else:
    st.session_state.model_name = None

# Sidebar: Reset & Download buttons
with st.sidebar:
    if st.button("🔁 Reset Chat"):
        st.session_state.chat_history = []
        st.success("Chat reset!")

    if st.session_state.chat_history:
        chat_text = "\n".join([f"{role} {text}" for role, text in st.session_state.chat_history])
        b64 = base64.b64encode(chat_text.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="chat_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt">📥 Download Transcript</a>'
        st.markdown(href, unsafe_allow_html=True)

# Function to get response from model
def get_response(messages):
    try:
        response = ollama.chat(st.session_state.model_name, messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"

# Display chat history with avatars
for role, text in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="background-color: #f0f0f0; padding: 10px; border-radius: 12px; max-width: 80%;">
                <b>You:</b> {html.escape(text)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif role == "Jarvis":
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="background-color: #e6f7ff; padding: 10px; border-radius: 12px; max-width: 80%;">
                <b>🤖 Jarvis:</b><br>{text}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Chat input
with st.container():
    col1, col2 = st.columns([9, 1])
    with col1:
        user_input = st.text_input("Type your message", placeholder="Ask me anything...", label_visibility="collapsed")
    with col2:
        if st.button("+"):
            uploaded_file = st.file_uploader("Upload a document or image", type=["txt", "pdf", "jpg", "png"], label_visibility="collapsed")
            if uploaded_file:
                st.success(f"Uploaded: {uploaded_file.name}")
                # Optional: you could parse and display the content or send it to the model

# Send message
if user_input and st.session_state.model_name:
    messages = [{"role": "user", "content": user_input}]
    response = get_response(messages)

    # Append to chat history
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Jarvis", response))
    st.experimental_rerun()
