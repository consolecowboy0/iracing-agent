# server.py
# pip install fastapi uvicorn httpx python-dotenv
import os, json, time, uuid, httpx, dotenv, asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("REALTIME_MODEL", "gpt-realtime")
HISTORY_PATH = Path(os.getenv("HISTORY_PATH", "history.json"))

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_lock = asyncio.Lock()

# ---------- Prompt ----------
RACE_ENGINEER_PROMPT = """You're the driver's snarky spotter and race engineer. Keep it brief, direct, and occasionally sarcastic. Your job is to:
- Give real-time race commentary and strategic advice
- Call out track conditions, other drivers, and opportunities
- Be supportive but don't sugarcoat bad driving
- Use racing terminology naturally
- Keep responses under 2 sentences unless it's critical info
- Stay in character as someone who's seen it all on the track
Examples:
"Nice line through turn 3... finally."
"Gap to the leader is 2.5 seconds and growing - time to stop admiring the scenery."
"Caution out, this is your chance to make up positions if you don't mess it up."
"""

# ---------- Models ----------
class MessageIn(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    session_id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class HistoryExportParams(BaseModel):
    # how many most-recent turns to keep verbatim (pairs of user/assistant; system kept)
    last_turns: int = 6

# ---------- History helpers ----------
def _now_ms() -> int:
    return int(time.time() * 1000)

def _ensure_file():
    if not HISTORY_PATH.exists():
        HISTORY_PATH.write_text(json.dumps({"sessions": [], "messages": []}, ensure_ascii=False, indent=2), encoding="utf-8")

async def _read() -> Dict[str, Any]:
    _ensure_file()
    async with _lock:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))

async def _write(data: Dict[str, Any]) -> None:
    async with _lock:
        HISTORY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

async def log_session(sess: Dict[str, Any]):
    data = await _read()
    data["sessions"].append(sess)
    await _write(data)

async def log_message(msg: MessageIn):
    data = await _read()
    data["messages"].append({
        "id": uuid.uuid4().hex[:12],
        "ts": _now_ms(),
        "role": msg.role,
        "content": msg.content,
        "session_id": msg.session_id,
        "meta": msg.meta or {}
    })
    await _write(data)

# ---------- Lifecycle ----------
@app.on_event("startup")
async def startup():
    _ensure_file()

# ---------- Realtime session (offline-first) ----------
@app.get("/session")
async def create_session(online: bool = Query(False, description="Set ?online=1 to actually call OpenAI")):
    """
    If online=false (default): returns a local stub and logs it.
    If online=true: calls OpenAI /v1/realtime/sessions and logs the real session.
    """
    sess_id = f"local_{uuid.uuid4().hex[:8]}"
    payload = {
        "model": MODEL,
        "instructions": RACE_ENGINEER_PROMPT,
        "modalities": ["audio", "text"],
        "voice": "ballad",
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "silence_duration_ms": 700,
            "prefix_padding_ms": 250
        }
    }

    if online and OPENAI_API_KEY:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "realtime=v1"
        }
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post("https://api.openai.com/v1/realtime/sessions",
                                  headers=headers, json=payload)
            r.raise_for_status()
            session = r.json()
    else:
        # stub “session” so you can proceed entirely offline
        session = {
            "id": sess_id,
            "model": MODEL,
            "voice": payload["voice"],
            "modalities": payload["modalities"],
            "turn_detection": payload["turn_detection"],
            "instructions": RACE_ENGINEER_PROMPT
        }

    await log_session({
        "ts": _now_ms(),
        "id": session.get("id", sess_id),
        "model": session.get("model", MODEL),
        "voice": session.get("voice", "ballad"),
        "modalities": session.get("modalities", ["audio", "text"]),
        "online": bool(online and OPENAI_API_KEY)
    })
    return session

# ---------- History endpoints ----------
@app.get("/history")
async def get_history():
    return await _read()

@app.post("/history")
async def add_history(msg: MessageIn):
    await log_message(msg)
    return {"ok": True}

@app.delete("/history")
async def reset_history():
    await _write({"sessions": [], "messages": []})
    return {"ok": True}

# ---------- Rotate (optional) ----------
@app.post("/history/rotate")
async def rotate_history(max_bytes: int = 5_242_880):  # ~5MB
    if HISTORY_PATH.exists() and HISTORY_PATH.stat().st_size > max_bytes:
        rotated = HISTORY_PATH.with_suffix(f".{int(time.time())}.json")
        async with _lock:
            HISTORY_PATH.replace(rotated)
        _ensure_file()
        return {"rotated_to": rotated.name}
    return {"rotated": False}

# ---------- Export for Realtime (rehydration) ----------
@app.get("/history/as-realtime-items")
async def history_as_realtime_items(last_turns: int = 6):
    """
    Returns a list of events you can send over WebRTC datachannel:
      - conversation.item.create (system/user/assistant)
    Only last_turns of recent user/assistant pairs are kept verbatim.
    """
    data = await _read()
    msgs = data.get("messages", [])

    # Keep all system messages (usually short) + last N user/assistant turns.
    systems = [m for m in msgs if m["role"] == "system"]
    dialog = [m for m in msgs if m["role"] in ("user", "assistant")]

    # Take last N*2 dialog messages
    keep = dialog[-(last_turns * 2):] if last_turns > 0 else []

    def to_event(m):
        role = m["role"]
        content_type = "input_text" if role in ("user", "system") else "output_text"
        return {
            "type": "conversation.item.create",
            "item": {
                "id": m.get("id", uuid.uuid4().hex[:12]),
                "type": "message",
                "role": role,
                "content": [{ "type": content_type, "text": m["content"] }]
            }
        }

    events = [to_event(m) for m in systems] + [to_event(m) for m in keep]
    return {"events": events, "count": len(events)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
