"""Candidate shared tools: book risk inputs, market data, and licensed research.

These typed interfaces outline a future MCP service; no MCP transport runs here.
A hosted adapter would bind authenticated identity and record calls before delegating
to the same Data methods. Keeping permission checks in Data makes them reusable
by both scheduled briefs and an approved interactive agent.
"""

from datetime import date
from typing import Protocol

from rates_brief.models import Book, Market, Research


class SharedDataTools(Protocol):
    def book(self, book: str, as_of: date) -> Book: ...
    def market(self, book: str, as_of: date, series: list[str]) -> Market: ...
    def research(self, book: str, as_of: date, regions: list[str]) -> Research: ...
