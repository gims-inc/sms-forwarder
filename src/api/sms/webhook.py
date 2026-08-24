import logging
import os
from typing import Any

import httpx

logger = logging.getLogger("sms.webhook")


class WebhookService:
    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = endpoint or os.getenv("SMS_WEBHOOK_URL")
        self.max_retries = int(os.getenv("SMS_WEBHOOK_RETRIES", "3"))

    def build_payload(
        self,
        *,
        event: str,
        message: str,
        sender: str,
        device: str,
        time: str,
    ) -> dict[str, Any]:
        return {
            "event": event,
            "message": message,
            "sender": sender,
            "device": device,
            "time": time,
        }

    async def send(self, payload: dict[str, Any]) -> None:
        if self.endpoint is None:
            return

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        self.endpoint,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )
                    response.raise_for_status()
                logger.info("webhook delivered", extra={"event": payload.get("event")})
                return
            except httpx.HTTPError as error:
                if attempt == self.max_retries:
                    logger.exception(
                        "webhook delivery failed",
                        extra={"event": payload.get("event"), "attempt": attempt},
                    )
                    raise
                logger.warning(
                    "webhook retry",
                    extra={"event": payload.get("event"), "attempt": attempt},
                )
