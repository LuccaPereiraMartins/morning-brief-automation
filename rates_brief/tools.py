import os
from collections.abc import Callable
from datetime import date
from typing import Any, TypeVar

from mcp.server.fastmcp import FastMCP

from rates_brief.audit import Audit
from rates_brief.data import Data
from rates_brief.models import Book, Market, Record, Research
from rates_brief.settings import Settings

T = TypeVar("T", bound=Record)


def create_server(settings: Settings, user: str, request_id: str) -> FastMCP:
    data = Data(settings, user)
    audit = Audit(
        settings.audit_dir, settings.data_dir / "platform/audit_event.schema.json", user, request_id
    )
    server = FastMCP("rates-data", log_level="ERROR")

    def call(name: str, arguments: dict[str, Any], function: Callable[[], T]) -> T:
        audit.emit("tool_call", {"tool": name, "arguments": arguments, "phase": "started"})
        try:
            result = function()
            if isinstance(result, Research):
                for document in result.documents:
                    audit.emit("document_retrieved", document.model_dump(mode="json"))
            audit.emit(
                "tool_call",
                {
                    "tool": name,
                    "arguments": arguments,
                    "phase": "completed",
                    "result": result.model_dump(mode="json"),
                },
            )
            return result
        except Exception as exc:
            audit.emit("error", {"tool": name, "error": str(exc)})
            raise

    @server.tool()
    def get_book_snapshot(book: str, as_of: date) -> Book:
        """Get positions and USD DV01 limits for the session's authorized book."""
        return call(
            "get_book_snapshot", {"book": book, "as_of": str(as_of)}, lambda: data.book(book, as_of)
        )

    @server.tool()
    def get_market_snapshot(book: str, as_of: date, series: list[str]) -> Market:
        """Get close-to-close observations and sourced FX for an authorized book."""
        return call(
            "get_market_snapshot",
            {"book": book, "as_of": str(as_of), "series": series},
            lambda: data.market(book, as_of, series),
        )

    @server.tool()
    def get_research(book: str, as_of: date, regions: list[str]) -> Research:
        """Retrieve same-date research after checking the bound user's licences."""
        return call(
            "get_research",
            {"book": book, "as_of": str(as_of), "regions": regions},
            lambda: data.research(book, as_of, regions),
        )

    return server


if __name__ == "__main__":
    create_server(
        Settings.from_env(), os.environ["BRIEF_USER"], os.environ["BRIEF_REQUEST_ID"]
    ).run(transport="stdio")
