import argparse
import asyncio
import hashlib
import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, TypeVar
from uuid import uuid4

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from rates_brief.audit import Audit
from rates_brief.data import Data
from rates_brief.llm import summarize
from rates_brief.models import Book, Market, Record, Research
from rates_brief.report import render
from rates_brief.risk import calculate, scenario
from rates_brief.settings import Settings

T = TypeVar("T", bound=Record)


async def invoke(session: ClientSession, name: str, arguments: dict[str, Any], model: type[T]) -> T:
    response = await session.call_tool(name, arguments)
    if response.isError:
        raise ValueError(f"MCP tool {name} failed: {response.content}")
    if response.structuredContent is None:
        raise ValueError("MCP tool returned no structured content")
    return model.model_validate(response.structuredContent)


async def generate(
    user: str,
    as_of: date,
    output: Path,
    settings: Settings,
    scenario_bucket: str | None = None,
    delta: Decimal | None = None,
) -> str:
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
            "scenario_bucket": scenario_bucket,
            "scenario_delta": str(delta) if delta is not None else None,
        },
    )
    try:
        Data(settings, user).authorize("RATES_RV")
        if (scenario_bucket is None) != (delta is None):
            raise ValueError("Provide both scenario bucket and DV01 change")
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        env.update(
            DATA_DIR=str(settings.data_dir),
            SOURCE_CONFIG=str(settings.source_config),
            AUDIT_DIR=str(settings.audit_dir),
            BRIEF_USER=user,
            BRIEF_REQUEST_ID=request_id,
        )
        params = StdioServerParameters(
            command=sys.executable, args=["-m", "rates_brief.tools"], env=env
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                args = {"book": "RATES_RV", "as_of": str(as_of)}
                book = await invoke(session, "get_book_snapshot", args, Book)
                market = await invoke(
                    session, "get_market_snapshot", {**args, "series": book.series}, Market
                )
                research = await invoke(
                    session,
                    "get_research",
                    {
                        **args,
                        "regions": sorted({p.region for p in book.positions} | {"Global"}),
                    },
                    Research,
                )
        risk = calculate(book, market, settings.conventions())
        hypothetical = (
            scenario(risk, scenario_bucket, delta)
            if scenario_bucket is not None and delta is not None
            else None
        )
        audit.emit(
            "tool_call",
            {
                "tool": "calculate_risk",
                "result": risk.model_dump(mode="json"),
                "scenario": [b.model_dump(mode="json") for b in hypothetical]
                if hypothetical is not None
                else None,
            },
        )
        model = summarize(settings, research, book, audit)
        report = render(
            user,
            request_id,
            book,
            market,
            research,
            risk,
            model,
            hypothetical,
            scenario_bucket,
            delta,
        )
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
    parser.add_argument("--scenario-bucket")
    parser.add_argument("--scenario-dv01-usd", type=Decimal)
    args = parser.parse_args()
    try:
        request_id = asyncio.run(
            generate(
                args.user,
                args.as_of,
                args.output,
                Settings.from_env(),
                args.scenario_bucket,
                args.scenario_dv01_usd,
            )
        )
    except Exception as exc:
        parser.exit(1, f"Brief failed: {exc}\n")
    print(f"Wrote {args.output} (request {request_id})")
