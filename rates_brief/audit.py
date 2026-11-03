import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from jsonschema import Draft202012Validator, FormatChecker

from rates_brief import __version__


class Audit:
    def __init__(self, directory: Path, schema: Path, user: str, request_id: str):
        UUID(request_id)
        self.path = directory / f"{request_id}.jsonl"
        self.user = user
        self.request_id = request_id
        self.validator = Draft202012Validator(
            json.loads(schema.read_text()), format_checker=FormatChecker()
        )

    def emit(self, event_type: str, detail: dict[str, Any]) -> None:
        event = {
            "event_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": self.user,
            "request_id": self.request_id,
            "event_type": event_type,
            "app": "rates-brief",
            "app_version": __version__,
            "detail": detail,
        }
        self.validator.validate(event)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # One request runs its client and server writes sequentially.
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
