import streamlit as st
import ollama
import html
import PyPDF2
import docx
from PIL import Image
import pytesseract

# App setup
st.set_page_config(page_title="Gemma3:4b Chatbot", layout="centered")
st.title("💬 Gemma3:4b Chatbot with File Upload")

# Session state initialization
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'uploaded_context' not in st.session_state:
    st.session_state['uploaded_context'] = ""

# Function to get response from LLM
def get_response(messages):
    try:
        response = ollama.chat("gemma3:4b", messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"❌ Error: {e}"

# File upload
uploaded_files = st.file_uploader("Upload documents or images to provide context", type=["pdf", "txt", "docx", "png", "jpg", "jpeg"], accept_multiple_files=True)

# Extract text from uploaded files
def extract_text(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.type.startswith("image/"):
        image = Image.open(file)
        return pytesseract.image_to_string(image)
    return ""

# Process uploads
if uploaded_files:
    context = ""
    for file in uploaded_files:
        extracted = extract_text(file)
        context += f"\n[File: {file.name}]\n{extracted}\n"
    st.session_state['uploaded_context'] = context
    st.success("📎 Context from files has been loaded and will be used in the conversation.")

# Display uploaded context (optional)
with st.expander("🔍 View Uploaded Context"):
    st.text_area("File Context", st.session_state['uploaded_context'], height=200)

# Display chat history
for message in st.session_state['chat_history']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_prompt = st.chat_input("Type your message...")

# On send
if user_prompt:
    # Build complete message including uploaded context
    context_prefix = f"Here is some relevant context from uploaded files:\n{st.session_state['uploaded_context']}\n\n" if st.session_state['uploaded_context'] else ""
    full_prompt = context_prefix + user_prompt

    # Show user message
    st.session_state['chat_history'].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Get model response
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state['chat_history']]
    messages[-1]["content"] = full_prompt  # Only add context to the current message
    response = get_response(messages)

    # Show and save model response
    st.session_state['chat_history'].append({"role": "assistant", "content": html.escape(response)})
    with st.chat_message("assistant"):
        st.markdown(response)
