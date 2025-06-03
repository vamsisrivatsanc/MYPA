import streamlit as st
import ollama
import html
import time
import re

# ---------- Page Config ----------
st.set_page_config(page_title="Jarvis Chatbot", page_icon="🤖", layout="wide")
st.markdown("<h1 style='text-align: center;'>🤖 Jarvis</h1>", unsafe_allow_html=True)

# ---------- Session State ----------
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'model' not in st.session_state:
    st.session_state.model = "gemma3:4b"

if 'show_upload_options' not in st.session_state:
    st.session_state.show_upload_options = False

# ---------- Load Local Models ----------
def get_local_models():
    try:
        model_data = ollama.list()
        return [m.get("model", "Unnamed") for m in model_data.get("models", [])]
    except Exception as e:
        st.warning(f"⚠️ Could not fetch models: {e}")
        return []

# ---------- Stream Response ----------
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

# ---------- Format Code Snippets ----------
def format_message(msg):
    # msg = html.escape(msg)
    # msg = re.sub(r"```(.*?)```", r"<pre><code>\1</code></pre>", msg, flags=re.DOTALL)
    # return msg.replace("\n", "<br>")
    code_blocks = re.findall(r"```(.*?)```", msg, re.DOTALL)
    
    # Replace code blocks with a placeholder
    for i, code in enumerate(code_blocks):
        msg = msg.replace(f"```{code}```", f"__CODEBLOCK_{i}__")

    # Escape everything else
    msg = html.escape(msg).replace("\n", "<br>")

    # Replace placeholders with formatted HTML
    for i, code in enumerate(code_blocks):
        safe_code = html.escape(code)
        code_html = f"<pre style='background:#2d2d2d;color:white;padding:10px;border-radius:5px;overflow-x:auto;'><code>{safe_code}</code></pre>"
        msg = msg.replace(f"__CODEBLOCK_{i}__", code_html)

    return msg

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    models = get_local_models()
    selected_model = st.selectbox("Choose Model", models, index=0 if models else None)
    st.session_state.model = selected_model

    if st.button("Reset Chat"):
        st.session_state.chat_history = []

    transcript_text = "\n".join([f"{r}: {m}" for r, m in st.session_state.chat_history])
    st.download_button("Download Transcript", data=transcript_text, file_name="chat_transcript.txt")

# ---------- Uploads Toggle ----------
plus_col = st.columns([11, 1])[1]
if plus_col.button("➕", key="plus_button"):
    st.session_state.show_upload_options = not st.session_state.show_upload_options

if st.session_state.show_upload_options:
    uploaded_file = st.file_uploader("Upload File", type=["txt", "pdf", "jpg", "png"])
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
        # TODO: Handle file parsing if needed

# ---------- JavaScript: Enter to Send, Shift+Enter for newline ----------
st.markdown("""
<script>
document.addEventListener("DOMContentLoaded", function() {
  let textArea = window.parent.document.querySelector("textarea");
  if (textArea) {
    textArea.addEventListener("keydown", function(e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        window.parent.document.querySelector('button[kind="primary"]').click();
      }
    });
  }
});
</script>
""", unsafe_allow_html=True)

# ---------- Input Form ----------
with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([10, 1])
    user_input = cols[0].text_area("", key="chat_input", height=70, placeholder="Type your message here...")
    send_btn = cols[1].form_submit_button(label="➤", help="Send message")

# ---------- Save User Message ----------
if send_btn and user_input.strip():
    st.session_state.chat_history.append(("You", html.escape(user_input.strip())))

# ---------- Chat History ----------
chat_container = st.container()
with chat_container:
    for role, message in st.session_state.chat_history:
        alignment = "flex-end" if role == "You" else "flex-start"
        bubble_color = "#f0f0f0" if role == "You" else "#d1e7dd"
        icon = "🧑" if role == "You" else "🤖"
        formatted_msg = format_message(message)

        st.markdown(f"""
            <div style="display:flex; margin-bottom:10px; justify-content: {alignment};">
                <div style="font-size: 30px; margin-right:10px;">{icon}</div>
                <div style="background:{bubble_color}; padding:10px; border-radius:15px; max-width: 70%; word-wrap: break-word;">
                    <strong>{icon} {role}:</strong><br>{formatted_msg}
                </div>
            </div>
        """, unsafe_allow_html=True)

# ---------- LLM Response Streaming ----------
if send_btn and user_input.strip():
    bot_response_placeholder = chat_container.empty()
    thinking_anim = "🧠 Jarvis is thinking"
    dots = ""
    for i in range(3):
        dots += "."
        bot_response_placeholder.markdown(f"""
            <div style='font-size: 18px; color: gray;'>
                {thinking_anim}{dots}
            </div>
        """, unsafe_allow_html=True)
        time.sleep(0.3)

    full_response = ""
    for partial in get_response_streaming(
        [{"role": "user", "content": user_input.strip()}],
        st.session_state.model
    ):
        full_response = partial
        bot_response_placeholder.markdown(f"""
            <div style="display:flex; margin-bottom:10px; justify-content: flex-start;">
                <div style="font-size: 30px; margin-right:10px;">🤖</div>
                <div style="background:#d1e7dd; padding:10px; border-radius:15px; max-width: 70%; word-wrap: break-word;">
                    <strong>🤖 Jarvis:</strong><br>{format_message(full_response)}
                </div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(0.05)

    st.session_state.chat_history.append(("Jarvis", full_response))
