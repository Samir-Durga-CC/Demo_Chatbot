import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()                       # reads .env when running on your laptop

MODEL = "openai/gpt-oss-120b"   # if this 404s, check console.groq.com/docs/models


def get_api_key():
    """Laptop -> .env file.   Streamlit Cloud -> Secrets.   Same code, both places."""
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


st.title("Demo Chatbot")

api_key = get_api_key()
if not api_key:
    st.error("No GROQ_API_KEY found.  Local: put it in .env   |   Deployed: Settings > Secrets")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

if prompt := st.chat_input("Ask me anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("Thinking..."):
        try:
            reply = client.chat.completions.create(
                model=MODEL,
                messages=st.session_state.messages,
            ).choices[0].message.content
        except Exception as e:
            reply = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
