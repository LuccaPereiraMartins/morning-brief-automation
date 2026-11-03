import asyncio
import json
from datetime import date
from pathlib import Path

import pytest

from rates_brief.audit import AuditWriteError
from rates_brief.cli import generate
from rates_brief.evaluate import run_case
from rates_brief.settings import Settings


def test_mcp_and_audit_for_both_users(settings: Settings) -> None:
    cases = json.loads(Path("evals/cases.json").read_text())
    for case in cases[:2]:
        result = asyncio.run(run_case(case, settings))
        assert result["passed"]


def test_audit_failure_prevents_report(settings: Settings, tmp_path: Path) -> None:
    settings.audit_dir.write_text("This is a file, not a directory")
    output = tmp_path / "report.md"
    with pytest.raises(AuditWriteError):
        asyncio.run(generate("tom", date(2026, 10, 28), output, settings))
    assert not output.exists()
