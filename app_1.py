import streamlit as st
import ollama
import html

# Streamlit app title
st.title("Gemma3:4b Chatbot (Ollama)")

# Check if Ollama is running locally
# if not ollama.is_running():
#     st.error("Ollama is not running locally. Please start Ollama before running this app.")
#     st.stop()

# Initialize chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to get a response from the model
def get_response(messages):
    try:
        response = ollama.chat(
            "gemma3:4b",
            messages=messages
        )
        return response
    except Exception as e:
        return f"Error: {e}"


# Streamlit UI elements
user_input = st.text_input("You:", "What is the capital of France?")

if st.button("Send"):
    prompt = user_input
    if prompt:
        messages = [
            {"role": "user", "content": prompt}
        ]
        response = get_response(messages)
        st.session_state['chat_history'].append(("You:", prompt))
        st.session_state['chat_history'].append(("Model:", html.escape(response['message']['content'])))  
        #Access response.text

# Display chat history
st.write("Chat History:")
for turn in st.session_state['chat_history']:
    role, text = turn
    if role == "You:":
        st.markdown(f"<div style='background-color:#f0f0f0; padding:5px;margin:5px;'>{text}</div>", unsafe_allow_html=True)
        #st.markdown(f"<div style='background-color:#f0f0f0; padding:5px;
# margin:5px;'>{text}</div>", unsafe_allow_html=True)
    elif role == "Model:":
        st.write(text)