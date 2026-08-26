import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
from opentelemetry import trace

from api.sms.service import SmsMessageService
from api.sms.webhook import WebhookService

from utils.time_helpers import TimeHelpers
logger = logging.getLogger("sms.router")
tracer = trace.get_tracer(__name__)

router = APIRouter(prefix="", tags=["sms"])

DB_PATH = os.getenv("SMS_DB", "data/sms.db")
service = SmsMessageService(db_path=DB_PATH)
webhook_service = WebhookService()


async def init_db() -> None:
    await service.init_db()


@router.get("/forward")
async def forward_sms(
    msg: str = Query(...),
    time: str = Query(...),
    in_number: str = Query(..., alias="in-number"),
    filter_name: str = Query(..., alias="filter-name"),
):
    with tracer.start_as_current_span("sms.forward") as span:
        span.set_attribute("sms.sender", in_number)
        span.set_attribute("sms.device", filter_name)

        result = await service.save_message(
            message=msg,
            sender=in_number,
            device=filter_name,
            raw_time=time,
        )

        payload = webhook_service.build_payload(
            event="sms.saved",
            message=msg,
            sender=in_number,
            device=filter_name,
            time=TimeHelpers.parse_time(time),
        )
        await webhook_service.send(payload)

        logger.info(
            "sms saved",
            extra={
                "sender": in_number,
                "device": filter_name,
                "count": result["count"],
            },
        )
        return result


@router.get("/messages")
async def get_messages(
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    messages = await service.list_messages(date=date, limit=limit, offset=offset)
    logger.info("messages retrieved", extra={"count": len(messages), "date": date})
    return {"messages": messages}


@router.get("/dates")
async def get_dates():
    dates = await service.list_dates()
    logger.info("dates retrieved", extra={"count": len(dates)})
    return {"dates": dates}


@router.get("/", response_class=HTMLResponse)
async def serve_viewer():
    p = Path(__file__).parent / "viewer.html"
    return HTMLResponse(p.read_text() if p.exists() else "<h2>viewer.html missing</h2>")
