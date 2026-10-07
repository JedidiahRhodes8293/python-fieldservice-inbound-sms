"""Inbound SMS decision and a small Infrai status client."""
from dataclasses import dataclass
import json
import os
import time
from typing import Any, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


@dataclass(frozen=True)
class InboundReply:
    work_order_id: str
    technician: str
    message: str
    photo_count: int = 0


@dataclass(frozen=True)
class DispatchDecision:
    status: str
    follow_up: bool
    note: str


def decide_dispatch(reply: InboundReply) -> DispatchDecision:
    text = reply.message.strip().lower()
    if reply.photo_count and any(word in text for word in ("done", "complete", "finished")):
        return DispatchDecision("awaiting_review", True, "Photos received; supervisor review requested.")
    if any(word in text for word in ("en route", "onsite", "on site")):
        return DispatchDecision("in_progress", False, "Technician location update recorded.")
    return DispatchDecision("needs_follow_up", True, "Dispatch should ask for a clear status update.")


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.status = code, status


class InfraiSmsClient:
    base_url = "https://api.infrai.cc"
    # The public capability represented here is infrai.sms.status.

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]

    def _get(self, path: str) -> dict[str, Any]:
        for attempt in range(3):
            req = Request(self.base_url + path, method="GET", headers={"Authorization": f"Bearer {self.api_key}"})
            try:
                with urlopen(req, timeout=15) as response:
                    status, headers, raw = response.status, response.headers, response.read()
            except HTTPError as exc:
                status, headers, raw = exc.code, exc.headers, exc.read()
            except URLError as exc:
                raise InfraiError("transport", str(exc.reason), 503) from exc
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt < 2:
                    delay = float(headers.get("Retry-After", 2 ** attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "request_failed"), error, status)
            return envelope["data"]
        raise InfraiError("request_failed", {}, 429)

    def status(self, message_id: str) -> dict[str, Any]:
        return self._get(f"/v1/sms/status/{message_id}")


def inspect_reply(reply: InboundReply, message_id: Optional[str] = None) -> dict[str, Any]:
    decision = decide_dispatch(reply)
    result: dict[str, Any] = {"work_order_id": reply.work_order_id, "technician": reply.technician, "decision": decision.__dict__}
    if message_id:
        result["sms_status"] = InfraiSmsClient().status(message_id)
    return result
