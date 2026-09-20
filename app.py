import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()                       # reads .env when running on your laptop

MODEL = "openai/gpt-oss-120b"   # if this 404s, check console.groq.com/docs/models
SYSTEM_PROMPT = "You are a helpful assistant. Answer clearly and concisely."
MAX_TURNS = 10                      # how many user+assistant pairs to remember


def get_api_key():
    """Laptop -> .env file.   Streamlit Cloud -> Secrets.   Same code, both places."""
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


st.set_page_config(page_title="Demo Chatbot", page_icon="=�")

# --- right-align user messages -------------------------------------------
# Streamlit has no built-in option for this. We tag our own <span> inside the
# user's bubble and use :has() to flip that row. Depends on our marker class,
# NOT on Streamlit's generated class names, so it survives version bumps.
st.markdown(
    """
    <style>
    [data-testid="stChatMessage"]:has(.user-msg) {
        flex-direction: row-reverse;
        text-align: right;
        background-color: rgba(120, 140, 255, 0.10);
        border-radius: 12px;
    }
    .user-msg { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Demo Chatbot")

api_key = get_api_key()
if not api_key:
    st.error("No GROQ_API_KEY found.  Local: put it in .env   |   Deployed: Settings > Secrets")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []          # <-- THIS is the memory

with st.sidebar:
    st.subheader("Memory")
    st.caption(f"Remembering last {MAX_TURNS} exchanges")
    st.metric("Messages held", len(st.session_state.messages))
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


def show(role, text):
    with st.chat_message(role):
        if role == "user":
            st.markdown(f'<span class="user-msg"></span>{text}', unsafe_allow_html=True)
        else:
            st.markdown(text)


for m in st.session_state.messages:
    show(m["role"], m["content"])


if prompt := st.chat_input("Ask me anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    show("user", prompt)

    # What we DISPLAY and what we SEND are different things.
    # Sent = system prompt + only the most recent MAX_TURNS exchanges.
    payload = [{"role": "system", "content": SYSTEM_PROMPT}]
    payload += st.session_state.messages[-(MAX_TURNS * 2):]

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=payload,
                stream=True,                 # <-- the streaming effect
            )
            reply = st.write_stream(
                chunk.choices[0].delta.content or "" for chunk in stream
            )
        except Exception as e:
            reply = f"Error: {e}"
            st.error(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
