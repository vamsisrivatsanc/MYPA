import streamlit as st
import ollama
import html

# Streamlit app title
st.set_page_config(page_title="Jarvis", layout="centered")
st.title("💬 I am Jarvis your Assistant")

# Initialize chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to get a response from the model
def get_response(messages):
    try:
        response = ollama.chat("gemma3:4b", messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"❌ Error: {e}"

# Display chat history using Streamlit's chat interface
for message in st.session_state['chat_history']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input at the bottom
user_prompt = st.chat_input("Type your message...")

# If user sends a message
if user_prompt:
    # Add user's message to chat history
    st.session_state['chat_history'].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Prepare message list for model
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state['chat_history']]

    # Get model response
    response = get_response(messages)

    # Add model response to history
    st.session_state['chat_history'].append({"role": "assistant", "content": html.escape(response)})
    with st.chat_message("assistant"):
        st.markdown(response)
