import argparse
import hashlib
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any, TypeVar
from uuid import uuid4

from rates_brief.audit import Audit
from rates_brief.data import Data
from rates_brief.llm import summarize
from rates_brief.mcp import SharedDataTools
from rates_brief.models import Record, Research
from rates_brief.report import render
from rates_brief.risk import calculate
from rates_brief.settings import Settings

T = TypeVar("T", bound=Record)


def retrieve(audit: Audit, name: str, arguments: dict[str, Any], call: Callable[[], T]) -> T:
    audit.emit("tool_call", {"tool": name, "arguments": arguments, "phase": "started"})
    result = call()
    if isinstance(result, Research):
        for document in result.documents:
            audit.emit("document_retrieved", document.model_dump(mode="json"))
    audit.emit(
        "tool_call", {"tool": name, "phase": "completed", "result": result.model_dump(mode="json")}
    )
    return result


def generate(user: str, as_of: date, output: Path, settings: Settings) -> str:
    """Local entry point; a scheduler can invoke the same per-user workflow."""
    request_id = str(uuid4())
    audit = Audit(
        settings.audit_dir, settings.data_dir / "platform/audit_event.schema.json", user, request_id
    )
    audit.emit(
        "user_request",
        {
            "as_of": str(as_of),
            "output": str(output),
            "settings": settings.model_dump(mode="json"),
            "source_config": settings.conventions().model_dump(mode="json"),
            "entitlements_sha256": hashlib.sha256(
                (settings.data_dir / "entitlements.yaml").read_bytes()
            ).hexdigest(),
        },
    )
    try:
        data: SharedDataTools = Data(settings, user)
        args = {"book": "RATES_RV", "as_of": str(as_of)}
        book = retrieve(audit, "book", args, lambda: data.book("RATES_RV", as_of))
        market = retrieve(
            audit,
            "market",
            {**args, "series": book.series},
            lambda: data.market(book.book, as_of, book.series),
        )
        regions = sorted({p.region for p in book.positions} | {"Global"})
        research = retrieve(
            audit,
            "research",
            {**args, "regions": regions},
            lambda: data.research(book.book, as_of, regions),
        )
        risk = calculate(book, market, settings.conventions(), settings.limit_warning_utilization)
        audit.emit("tool_call", {"tool": "calculate_risk", "result": risk.model_dump(mode="json")})
        model = summarize(settings, research, book, audit)
        report = render(user, request_id, book, market, research, risk, model)
        audit.emit("response", {"markdown": report, "model_mode": model.mode})
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        return request_id
    except Exception as exc:
        audit.emit("error", {"error": str(exc)})
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an authorized Rates morning brief")
    parser.add_argument("--user", required=True)
    parser.add_argument("--as-of", type=date.fromisoformat, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        request_id = generate(args.user, args.as_of, args.output, Settings.from_env())
    except Exception as exc:
        parser.exit(1, f"Brief failed: {exc}\n")
    print(f"Wrote {args.output} (request {request_id})")
