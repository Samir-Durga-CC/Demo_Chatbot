# Demo Chatbot

Streamlit + Groq. Minimal on purpose - the point is the deployment, not the bot.

## Run locally
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    streamlit run app.py

Put your real key in `.env` first.

## Deploy
1. Push to GitHub (`.env` is gitignored - it must NOT be in the repo)
2. share.streamlit.io -> Create app -> pick this repo -> main file `app.py`
3. Advanced settings -> Secrets -> paste:  GROQ_API_KEY = "gsk_..."
4. Deploy. You get a public URL.

Every `git push` to main redeploys automatically.
