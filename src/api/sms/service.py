import os
from datetime import datetime

import aiosqlite

DB_PATH = os.getenv("SMS_DB", "sms.db")


class utils:
    @staticmethod
    def parse_time(raw: str) -> str:
        raw = raw.strip()
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%y, %I:%M %p",
            "%m/%d/%y %I:%M %p",
            "%m/%d/%y, %H:%M",
            "%m/%d/%y %H:%M",
            "%Y-%m-%dT%H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

        try:
            year = datetime.now().year
            return datetime.strptime(f"{year}/{raw}", "%Y/%m/%d, %I:%M %p").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            pass

        return raw


class SmsMessageService:
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path

    async def init_db(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    message     TEXT    NOT NULL,
                    time        TEXT    NOT NULL,
                    sender      TEXT    NOT NULL,
                    device      TEXT    NOT NULL,
                    received_at TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
                )
                """
            )
            await db.commit()

    async def save_message(
        self,
        *,
        message: str,
        sender: str,
        device: str,
        raw_time: str,
    ) -> dict[str, int | str]:
        clean_time = parse_time(raw_time)

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO messages (message, time, sender, device) VALUES (?, ?, ?, ?)",
                (message, clean_time, sender, device),
            )
            await db.commit()
            row_id = cursor.lastrowid
            count = (
                await (await db.execute("SELECT COUNT(*) FROM messages")).fetchone()
            )[0]

        return {"status": "saved", "id": row_id, "count": count}

    async def list_messages(
        self,
        *,
        date: str | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> list[dict[str, str | int]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if date:
                rows = await (
                    await db.execute(
                        "SELECT * FROM messages WHERE time LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?",
                        (f"{date}%", limit, offset),
                    )
                ).fetchall()
            else:
                rows = await (
                    await db.execute(
                        "SELECT * FROM messages ORDER BY id DESC LIMIT ? OFFSET ?",
                        (limit, offset),
                    )
                ).fetchall()

        return [dict(row) for row in rows]

    async def list_dates(self) -> list[str]:
        async with aiosqlite.connect(self.db_path) as db:
            rows = await (
                await db.execute(
                    "SELECT DISTINCT substr(time,1,10) AS date FROM messages ORDER BY date DESC"
                )
            ).fetchall()

        return [row[0] for row in rows]
