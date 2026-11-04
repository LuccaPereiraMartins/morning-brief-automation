import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from rates_brief.audit import AuditWriteError
from rates_brief.cli import generate
from rates_brief.settings import Settings


def test_both_briefs_and_audit(settings: Settings, tmp_path: Path) -> None:
    schema = json.loads((settings.data_dir / "platform/audit_event.schema.json").read_text())
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    risks = []
    for user, providers in [
        ("tom", {"Bank A", "Bank B", "Bank C", "Internal"}),
        ("jim", {"Bank A", "Internal"}),
    ]:
        output = tmp_path / f"{user}.md"
        request_id = generate(user, date(2026, 10, 28), output, settings)
        events = [
            json.loads(line)
            for line in (settings.audit_dir / f"{request_id}.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        for event in events:
            validator.validate(event)
            assert event["user_id"] == user and event["request_id"] == request_id
        report = output.read_text(encoding="utf-8")
        assert events[-1]["detail"]["markdown"] == report
        assert len(report.split("<details>")[0].splitlines()) < 30
        assert "DV01 conversions and audit" in report
        assert any(e["detail"].get("executed") is False for e in events)
        assert {
            e["detail"]["provider"] for e in events if e["event_type"] == "document_retrieved"
        } == providers
        result = next(
            e["detail"]["result"] for e in events if e["detail"].get("tool") == "calculate_risk"
        )
        risks.append(result)
        assert {b["bucket"]: Decimal(b["net"]) for b in result["buckets"]} == {
            "5Y": Decimal("69500"),
            "10Y": Decimal("48557.04"),
            "30Y": Decimal("21150.08"),
            "TOTAL": Decimal("139207.12"),
        }
        assert result["buckets"][-1]["status"] == "approaching limit"
        if user == "jim":
            assert "Bank B" not in json.dumps(events) and "Bank C" not in json.dumps(events)
    assert risks[0] == risks[1]


def test_audit_failure_prevents_report(settings: Settings, tmp_path: Path) -> None:
    settings.audit_dir.write_text("This is a file, not a directory")
    output = tmp_path / "report.md"
    with pytest.raises(AuditWriteError):
        generate("tom", date(2026, 10, 28), output, settings)
    assert not output.exists()


def test_denied_users_receive_no_report(settings: Settings, tmp_path: Path) -> None:
    for user in ("unknown", "sara"):
        output = tmp_path / f"{user}.md"
        with pytest.raises(PermissionError):
            generate(user, date(2026, 10, 28), output, settings)
        assert not output.exists()
