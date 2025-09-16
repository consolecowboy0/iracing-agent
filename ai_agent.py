# server.py
# pip install fastapi uvicorn httpx python-dotenv
import os, httpx, dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
PROMPT_ID = os.environ["PROMPT_ID"]          # e.g. prmpt_12345
MODEL = os.getenv("REALTIME_MODEL", "gpt-realtime")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/session")
async def create_session():
    # Create a Realtime session with built-in barge-in (server VAD) + your Playground prompt
    payload = {
        "model": MODEL,
        "instructions": f"prompt:{PROMPT_ID}",
        "modalities": ["audio","text"],
        "voice": "verse",
        "turn_detection": {
            "type": "server_vad",
            # tune these as needed:
            "threshold": 0.5,             # speech confidence gate
            "silence_duration_ms": 700,   # how long of silence ends a turn
            "prefix_padding_ms": 250      # audio kept before detected speech
        }
    }
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "realtime=v1"
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post("https://api.openai.com/v1/realtime/sessions",
                              headers=headers, json=payload)
        r.raise_for_status()
        return r.json()
