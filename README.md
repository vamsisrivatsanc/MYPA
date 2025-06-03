# Jarvis Chatbot

🤖 A Streamlit-based chatbot interface powered by Ollama models.

---

## Features

- Select from locally available Ollama models.
- Interactive chat with streaming response display.
- Syntax-highlighted code snippets in chat responses.
- Enter key sends messages; Shift+Enter inserts a newline.
- Upload files (txt, pdf, jpg, png) — placeholder for future parsing.
- Download chat transcript.
- Reset chat history.
- Thinking animation while the assistant is generating a response.

---

## Installation

1. Clone the repository or download the files.

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```
---

## Pre-requisites

Ensure Ollama is installed and running locally, and that you have models downloaded.

## Usage

Run the Streamlit app with:
```bash
streamlit run app.py
```
Open the displayed local URL in your browser.

## Notes

This app uses the Ollama Python SDK to interact with locally hosted language models.

Code snippets returned by the model are rendered with syntax highlighting.

The Enter key sends messages, while Shift+Enter adds a new line.

File upload support is present but parsing is yet to be implemented.

## License

MIT License

## Acknowledgements

Built with Streamlit

Powered by Ollama
