import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from jsonschema import ValidationError

from rates_brief.audit import Audit, AuditWriteError
from rates_brief.data import Data
from rates_brief.llm import ProviderGateway, eligible, payload, summarize, validate_summaries
from rates_brief.models import Book, Research, Summaries, Summary
from rates_brief.settings import Settings


def inputs(settings: Settings) -> tuple[Book, Research, Audit]:
    data = Data(settings, "tom")
    book = data.book("RATES_RV", date(2026, 10, 28))
    research = data.research(book.book, book.as_of, ["US", "UK", "Euro area", "Global"])
    audit = Audit(
        settings.audit_dir,
        settings.data_dir / "platform/audit_event.schema.json",
        "tom",
        str(uuid4()),
    )
    return book, research, audit


def valid(research: Research, book: Book) -> Summaries:
    return Summaries(
        items=[
            Summary(
                document_id=d.document_id,
                position_ids=eligible(d, book),
                view="The source expresses a curve preference.",
                relevance="The view concerns the listed positions.",
            )
            for d in research.documents
        ]
    )


@pytest.mark.parametrize("change", ["citation", "position", "number", "word", "consensus", "omit"])
def test_reject_invalid_model_output(settings: Settings, change: str) -> None:
    book, research, _ = inputs(settings)
    result = valid(research, book)
    if change == "citation":
        result.items[0].document_id = "not-retrieved"
    elif change == "position":
        result.items[0].position_ids = ["E-001"]
    elif change == "omit":
        result.items.pop()
    else:
        result.items[0].view = {
            "number": "Rates are 4.35%",
            "word": "Rates fall five points",
            "consensus": "This is the market consensus",
        }[change]
    with pytest.raises(ValueError):
        validate_summaries(result, research, book)


def test_live_path_with_controlled_gateway(settings: Settings) -> None:
    book, research, audit = inputs(settings)
    settings.llm_mode = "live"

    class FakeGateway:
        def generate(self, content: str, sink: Audit) -> Summaries:
            assert "present\nBank B's view" not in content
            assert "do not mention other brokers" not in content
            return valid(research, book)

    result = summarize(settings, research, book, audit, FakeGateway())
    assert result.mode == "live"
    assert len(result.summaries.items) == 4
    assert "market consensus" not in payload(research, book)


def test_model_failure_is_labeled(settings: Settings) -> None:
    book, research, audit = inputs(settings)
    settings.llm_mode = "live"

    class BrokenGateway:
        def generate(self, content: str, sink: Audit) -> Summaries:
            raise TimeoutError("private details")

    result = summarize(settings, research, book, audit, BrokenGateway())
    assert result.mode.startswith("degraded")
    assert result.warning
    assert "private details" not in audit.path.read_text()


def test_audit_failure_is_fatal(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    book, research, audit = inputs(settings)
    settings.llm_mode = "live"

    class AuditFailureGateway:
        def generate(self, content: str, sink: Audit) -> Summaries:
            raise AuditWriteError("disk full")

    with pytest.raises(AuditWriteError):
        summarize(settings, research, book, audit, AuditFailureGateway())
    original = audit.path.read_text()
    with pytest.raises(ValidationError):
        audit.emit("made_up_event", {})
    assert audit.path.read_text() == original

    def fail(*args: object, **kwargs: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(Path, "mkdir", fail)
    with pytest.raises(AuditWriteError):
        audit.emit("response", {"markdown": "text"})


def test_offline_is_explicit_and_audited(settings: Settings) -> None:
    book, research, audit = inputs(settings)
    result = summarize(settings, research, book, audit)
    assert result.mode == "offline stub"
    events = [json.loads(line) for line in audit.path.read_text().splitlines()]
    assert events[0]["detail"]["executed"] is False
    assert "<!--" not in result.summaries.items[1].view


def test_provider_adapter_contract(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    book, research, audit = inputs(settings)
    expected = valid(research, book)

    class Response:
        choices = [SimpleNamespace(message=SimpleNamespace(parsed=expected))]

        def model_dump(self, **kwargs: object) -> dict[str, object]:
            return {"id": "test-response", "usage": {"total_tokens": 100}}

    class Client:
        def __init__(self, **kwargs: object):
            self.chat = SimpleNamespace(completions=SimpleNamespace(parse=self.parse))

        def parse(self, **kwargs: object) -> Response:
            assert kwargs["model"] == "configured-model"
            assert kwargs["response_format"] is Summaries
            assert "tools" not in kwargs
            return Response()

        def __enter__(self) -> "Client":
            return self

        def __exit__(self, *args: object) -> None:
            pass

    monkeypatch.setattr("rates_brief.llm.OpenAI", Client)
    assert ProviderGateway("configured-model").generate(payload(research, book), audit) == expected
    assert "test-response" in audit.path.read_text()
