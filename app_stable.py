import streamlit as st
import ollama
import html
import time

st.set_page_config(page_title="Jarvis Chatbot", page_icon="🤖", layout="wide")
st.markdown("<h1 style='text-align: center;'>🤖 Jarvis</h1>", unsafe_allow_html=True)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'model' not in st.session_state:
    st.session_state.model = "gemma3:4b"

if 'show_upload_options' not in st.session_state:
    st.session_state.show_upload_options = False

def get_local_models():
    try:
        model_data = ollama.list()
        return [m.get("model", "Unnamed") for m in model_data.get("models", [])]
    except Exception as e:
        st.warning(f"⚠️ Could not fetch models: {e}")
        return []

def get_response_streaming(messages, model):
    try:
        response_stream = ollama.chat(model, messages=messages, stream=True)
        full_response = ""
        for chunk in response_stream:
            part = chunk.get("message", {}).get("content", "")
            full_response += part
            yield full_response
    except Exception as e:
        yield f"Error: {e}"

with st.sidebar:
    st.header("⚙️ Settings")
    models = get_local_models()
    selected_model = st.selectbox("Choose Model", models, index=0 if models else None)
    st.session_state.model = selected_model

    if st.button("Reset Chat"):
        st.session_state.chat_history = []

    transcript_text = "\n".join([f"{r}: {m}" for r, m in st.session_state.chat_history])
    st.download_button("Download Transcript", data=transcript_text, file_name="chat_transcript.txt")

# ➕ upload toggle outside form
plus_col = st.columns([11, 1])[1]
if plus_col.button("➕", key="plus_button"):
    st.session_state.show_upload_options = not st.session_state.show_upload_options

if st.session_state.show_upload_options:
    uploaded_file = st.file_uploader("Upload File", type=["txt", "pdf", "jpg", "png"])
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
        # TODO: parse the file, extract text if needed, append to messages

# --- Chat input form ---
with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([10, 1])
    user_input = cols[0].text_area(
        "", key="chat_input", height=70, placeholder="Type your message here..."
    )
    send_btn = cols[1].form_submit_button(label="➤", help="Send message")

# Append user message BEFORE rendering chat history
if send_btn and user_input.strip():
    st.session_state.chat_history.append(("You", html.escape(user_input.strip())))

# --- Display chat history ---
chat_container = st.container()
with chat_container:
    for role, message in st.session_state.chat_history:
        if role == "You":
            st.markdown(f"""
                <div style="display:flex; margin-bottom:10px; justify-content: flex-end;">
                    <div style="background:#f0f0f0; padding:10px; border-radius:15px; max-width: 70%; word-wrap: break-word;">
                        <strong>🧑 You:</strong><br>{message}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="display:flex; margin-bottom:10px; justify-content: flex-start; align-items: center;">
                    <div style="font-size:30px; margin-right:10px;">🤖</div>
                    <div style="background:#d1e7dd; padding:10px; border-radius:15px; max-width: 70%; word-wrap: break-word;">
                        <strong>🤖 Jarvis:</strong><br>{message}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- Stream and display the assistant response ---
if send_btn and user_input.strip():
    # Placeholder for assistant response streaming
    bot_response_placeholder = chat_container.empty()

    full_response = ""
    for partial_response in get_response_streaming(
        [{"role": "user", "content": user_input.strip()}], st.session_state.model
    ):
        full_response = partial_response
        bot_response_placeholder.markdown(f"""
            <div style="display:flex; margin-bottom:10px; justify-content: flex-start; align-items: center;">
                <div style="font-size:30px; margin-right:10px;">🤖</div>
                <div style="background:#d1e7dd; padding:10px; border-radius:15px; max-width: 70%; word-wrap: break-word;">
                    <strong>🤖 Jarvis:</strong><br>{html.escape(full_response)}
                </div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(0.05)

    # Save final assistant response to chat history
    st.session_state.chat_history.append(("Jarvis", html.escape(full_response)))
