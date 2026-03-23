# from fastapi import FastAPI, Query
# from fastapi.responses import JSONResponse
# from typing import List, Dict

# app = FastAPI()

# # In-memory storage, you can use any desired storage.
# messages: List[Dict] = []

# @app.get("/forward")
# async def forward_sms(
#     msg: str = Query(..., description="The SMS message content"),
#     time: str = Query(..., description="Time when the message was received"),
#     in_number: str = Query(..., alias="in-number", description="Sender's phone number"),
#     filter_name: str = Query(..., alias="filter-name", description="Name/identifier of the filter")
# ):
#     message = {
#         "message": msg, # content
#         "time": time, # real time of receiving the message
#         "from": in_number, # sender phone number, or name if its Govermenet.
#         "device": filter_name # its not really important, its a filter name.
#     }
#     messages.append(message)
#     return {"status": "saved", "count": len(messages)}

# @app.get("/messages")
# async def get_all_messages():
#     return {"messages": messages} # it will return all received sms message, it should be private!



from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
import aiosqlite
import os
from datetime import datetime

def parse_time(raw: str) -> str:
    raw = raw.strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",   # 2026-03-04 14:41:47
        "%m/%d/%y, %I:%M %p",  # 03/04/26, 2:41 PM
        "%m/%d/%y %I:%M %p",   # 03/04/26 2:41 PM
        "%m/%d/%y, %H:%M",     # 03/04/26, 14:41
        "%m/%d/%y %H:%M",      # 03/04/26 14:41
        "%Y-%m-%dT%H:%M:%S",   # ISO
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    # ── Handle "03/04, 2:41 PM" (no year) ──────────────────────
    try:
        year = datetime.now().year
        return datetime.strptime(f"{year}/{raw}", "%Y/%m/%d, %I:%M %p").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass

    return raw  # store as-is if nothing matched

DB_PATH = os.getenv("SMS_DB", "sms.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                message     TEXT    NOT NULL,
                time        TEXT    NOT NULL,
                sender      TEXT    NOT NULL,
                device      TEXT    NOT NULL,
                received_at TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
            )
        """)
        await db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="SMS Forwarder", lifespan=lifespan)

@app.get("/forward")
async def forward_sms(
    msg: str         = Query(...),
    time: str        = Query(...),
    in_number: str   = Query(..., alias="in-number"),
    filter_name: str = Query(..., alias="filter-name"),
):
    clean_time = parse_time(time)
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO messages (message, time, sender, device) VALUES (?, ?, ?, ?)",
            (msg, clean_time, in_number, filter_name),
        )
        await db.commit()
        row_id = cursor.lastrowid
        count = (await (await db.execute("SELECT COUNT(*) FROM messages")).fetchone())[0]
    return {"status": "saved", "id": row_id, "count": count}

@app.get("/messages")
async def get_messages(
    date:   Optional[str] = Query(None, description="YYYY-MM-DD"),
    limit:  int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if date:
            rows = await (await db.execute(
                "SELECT * FROM messages WHERE time LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?",
                (f"{date}%", limit, offset),
            )).fetchall()
        else:
            rows = await (await db.execute(
                "SELECT * FROM messages ORDER BY id DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )).fetchall()
    return {"messages": [dict(r) for r in rows]}

@app.get("/dates")
async def get_dates():
    async with aiosqlite.connect(DB_PATH) as db:
        rows = await (await db.execute(
            "SELECT DISTINCT substr(time,1,10) AS date FROM messages ORDER BY date DESC"
        )).fetchall()
    return {"dates": [r[0] for r in rows]}

@app.get("/", response_class=HTMLResponse)
async def serve_viewer():
    # file = open(filename, encoding="utf-8")
    p = Path(__file__).parent / "viewer.html"
    return HTMLResponse(p.read_text() if p.exists() else "<h2>viewer.html missing</h2>")
