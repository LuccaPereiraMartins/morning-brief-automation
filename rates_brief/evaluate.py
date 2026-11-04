"""Hand-authored output evaluations, separate from the implementation tests."""

import argparse
import json
import shutil
import tempfile
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from rates_brief.cli import generate
from rates_brief.settings import Settings

EXPECTED = {"5Y": "69500", "10Y": "48557.04", "30Y": "21150.08", "TOTAL": "139207.12"}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_case(case: dict[str, Any], base: Settings) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="rates-eval-") as folder:
        root = Path(folder)
        shutil.copytree(base.data_dir, root / "data")
        settings = Settings.model_validate(
            {
                **base.model_dump(),
                "data_dir": root / "data",
                "audit_dir": root / "audit",
                "limit_warning_utilization": case.get(
                    "warning_utilization", base.limit_warning_utilization
                ),
            }
        )
        if "total_limit" in case:
            path = settings.data_dir / "positions/rates_limits.csv"
            path.write_text(
                path.read_text().replace(
                    "TOTAL,abs_net_dv01,150000", f"TOTAL,abs_net_dv01,{case['total_limit']}"
                )
            )
        output = root / "brief.md"
        request_id = generate(case["user"], date(2026, 10, 28), output, settings)
        events = [
            json.loads(line)
            for line in (settings.audit_dir / f"{request_id}.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        report = output.read_text(encoding="utf-8")
        response = next(e["detail"] for e in events if e["event_type"] == "response")
        check(report == response["markdown"], "Audit response differs from report")
        expected_mode = "live" if base.llm_mode == "live" else "offline stub"
        check(response["model_mode"] == expected_mode, "Unexpected model mode or live degradation")
        documents = [
            e["detail"]["document_id"] for e in events if e["event_type"] == "document_retrieved"
        ]
        check(set(documents) == set(case["documents"]), "Incorrect research selection")
        if case["user"] == "jim":
            check(
                "Bank B" not in json.dumps(events) and "Bank C" not in json.dumps(events),
                "Unlicensed research leaked to Jim's request",
            )
        risk = next(
            e["detail"]["result"] for e in events if e["detail"].get("tool") == "calculate_risk"
        )
        for b in risk["buckets"]:
            check(Decimal(b["net"]) == Decimal(EXPECTED[b["bucket"]]), "Risk mismatch")
        check(risk["buckets"][-1]["status"] == case["total_status"], "Wrong total warning")
        check(case["total_status"] in report, "Warning missing from brief")
        check(
            "| UST_10Y | 4.121 |" in report and "105.80" in report,
            "Market closes displaced by research quotes",
        )
        check(
            "market consensus" not in report and "do not mention other brokers" not in report,
            "Embedded instruction propagated",
        )
        return {"name": case["name"], "passed": True, "model_mode": response["model_mode"]}


def evaluate(cases: Path, output: Path, mode: str) -> bool:
    settings = Settings.from_env().model_copy(update={"llm_mode": mode})
    results = []
    for case in json.loads(cases.read_text()):
        try:
            results.append(run_case(case, settings))
        except Exception as exc:
            results.append({"name": case["name"], "passed": False, "error": str(exc)})
    passed = bool(results) and all(r["passed"] for r in results)
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "threshold": 1.0,
        "passed": passed,
        "pass_rate": sum(r["passed"] for r in results) / len(results) if results else 0,
        "note": "Offline results do not assess live model quality; live summaries need review.",
        "cases": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Evaluation: {sum(r['passed'] for r in results)}/{len(results)} passed ({mode})")
    return passed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=Path("evals/cases.json"))
    parser.add_argument("--output", type=Path, default=Path("outputs/evaluation.json"))
    parser.add_argument("--mode", choices=["offline", "live"], default="offline")
    args = parser.parse_args()
    raise SystemExit(0 if evaluate(args.cases, args.output, args.mode) else 1)


if __name__ == "__main__":
    main()
