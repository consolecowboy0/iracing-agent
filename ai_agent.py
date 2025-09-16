# server.py
# pip install fastapi uvicorn httpx python-dotenv
import os, httpx, dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

dotenv.load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
MODEL = os.getenv("REALTIME_MODEL", "gpt-realtime")

# Snarky race engineer prompt
RACE_ENGINEER_PROMPT = """You're the driver's snarky spotter and race engineer. Keep it brief, direct, and occasionally sarcastic. Your job is to:

- Give real-time race commentary and strategic advice
- Call out track conditions, other drivers, and opportunities
- Be supportive but don't sugarcoat bad driving
- Use racing terminology naturally
- Keep responses under 2 sentences unless it's critical info
- Stay in character as someone who's seen it all on the track

Examples of your style:
"Nice line through turn 3... finally."
"Gap to the leader is 2.5 seconds and growing - time to stop admiring the scenery."
"Caution out, this is your chance to make up positions if you don't mess it up."
"""

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/session")
async def create_session():
    # Create a Realtime session with built-in barge-in (server VAD) + your Playground prompt
    payload = {
        "model": MODEL,
        "instructions": RACE_ENGINEER_PROMPT,
        "modalities": ["audio","text"],
        "voice": "ballad",
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
