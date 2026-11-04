from datetime import date
from uuid import uuid4

import pytest

from rates_brief.audit import Audit, AuditWriteError
from rates_brief.data import Data
from rates_brief.llm import eligible, summarize, validate_summaries
from rates_brief.models import Book, Research, Summaries, Summary
from rates_brief.settings import Settings


def inputs(settings: Settings) -> tuple[Book, Research, Audit, Summaries]:
    data = Data(settings, "tom")
    book = data.book("RATES_RV", date(2026, 10, 28))
    research = data.research(book.book, book.as_of, ["US", "UK", "Euro area", "Global"])
    audit = Audit(
        settings.audit_dir,
        settings.data_dir / "platform/audit_event.schema.json",
        "tom",
        str(uuid4()),
    )
    summaries = Summaries(
        items=[
            Summary(
                document_id=d.document_id,
                position_ids=eligible(d, book),
                view="The source prefers steepeners.",
                relevance="The view concerns the listed positions.",
            )
            for d in research.documents
        ]
    )
    return book, research, audit, summaries


def test_model_references_and_numbers(settings: Settings) -> None:
    book, research, _, valid = inputs(settings)
    # Bank C explicitly discusses Bund/gilt relative value: both positions are in this book.
    eur = next(s for s in valid.items if "eur-swap-spreads" in s.document_id)
    eur.position_ids = ["R-005", "R-008"]
    valid.items[-1].view = "Book DV01 needs review."
    validate_summaries(valid, research, book)
    for change in [
        {"document_id": "unknown"},
        {"position_ids": ["E-001"]},
        {"view": "Rates are 4.35%"},
        {"view": "This is the market consensus"},
    ]:
        invalid = valid.model_copy(deep=True)
        invalid.items[0] = invalid.items[0].model_copy(update=change)
        with pytest.raises(ValueError):
            validate_summaries(invalid, research, book)


def test_live_gateway_receives_cleaned_research(settings: Settings) -> None:
    book, research, audit, valid = inputs(settings)
    settings.llm_mode = "live"

    class Gateway:
        def generate(self, content: str, sink: Audit) -> Summaries:
            assert "do not mention other brokers" not in content
            return valid

    assert summarize(settings, research, book, audit, Gateway()).mode == "live"


def test_model_failure_degrades_but_audit_failure_is_fatal(settings: Settings) -> None:
    book, research, audit, _ = inputs(settings)
    settings.llm_mode = "live"

    class Gateway:
        def __init__(self, error: Exception):
            self.error = error

        def generate(self, content: str, sink: Audit) -> Summaries:
            raise self.error

    result = summarize(settings, research, book, audit, Gateway(TimeoutError("private details")))
    assert result.warning and result.mode.startswith("degraded")
    assert "private details" not in audit.path.read_text()
    with pytest.raises(AuditWriteError):
        summarize(settings, research, book, audit, Gateway(AuditWriteError("disk full")))
