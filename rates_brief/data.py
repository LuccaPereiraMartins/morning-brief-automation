import csv
import hashlib
import re
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from rates_brief.models import (
    Book,
    Document,
    Limit,
    Market,
    Observation,
    Position,
    Research,
    Source,
)
from rates_brief.settings import Settings


class Data:
    def __init__(self, settings: Settings, user: str):
        self.settings = settings
        self.config = settings.conventions()
        users = yaml.safe_load((settings.data_dir / "entitlements.yaml").read_text())["users"]
        if user not in users:
            raise PermissionError("Unknown local user")
        self.identity = users[user]

    def authorize(self, book: str) -> None:
        if book not in self.identity["books"]:
            raise PermissionError("Book access denied")

    def source(self, path: Path, row: int, as_of: date | None = None) -> Source:
        return Source(
            path=path.relative_to(self.settings.data_dir).as_posix(),
            row=row,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            as_of=as_of,
        )

    def rows(self, relative: str, keys: list[str]) -> list[tuple[int, dict[str, str]]]:
        path = self.settings.data_dir / relative
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(enumerate(csv.DictReader(stream), start=2))
        seen: set[tuple[str, ...]] = set()
        for _, row in rows:
            key = tuple(row[k] for k in keys)
            if key in seen:
                raise ValueError(f"Duplicate input in {relative}: {key}")
            seen.add(key)
        return rows

    def book(self, book: str, as_of: date) -> Book:
        self.authorize(book)
        if book != "RATES_RV":
            raise ValueError("This adapter supports RATES_RV only")
        filename = f"positions/rates_rv_{as_of}.csv"
        positions, warnings, series = [], [], set()
        for line, row in self.rows(filename, ["position_id"]):
            if row["book"] != book or date.fromisoformat(row["as_of_date"]) != as_of:
                raise ValueError("Position book/date differs from requested snapshot")
            rules = [r for r in self.config.instruments if re.search(r.pattern, row["description"])]
            if len(rules) > 1:
                raise ValueError("Ambiguous instrument mapping")
            region = rules[0].region if rules else "Unsupported"
            if rules:
                series.update(rules[0].series)
            else:
                warnings.append(f"Unsupported research/market mapping: {row['instrument']}")
            positions.append(
                Position(
                    **{
                        k: row[k]
                        for k in (
                            "position_id",
                            "instrument",
                            "description",
                            "dv01_ccy",
                            "dv01_unit",
                            "curve_bucket",
                        )
                    },
                    dv01=Decimal(row["dv01"]),
                    region=region,
                    source=self.source(self.settings.data_dir / filename, line, as_of),
                )
            )
        limits = []
        for line, row in self.rows("positions/rates_limits.csv", ["book", "curve_bucket"]):
            if row["book"] != book:
                continue
            if row["limit_type"] != "abs_net_dv01" or row["limit_ccy"] != "USD":
                raise ValueError("Unsupported limit convention")
            limits.append(
                Limit(
                    bucket=row["curve_bucket"],
                    amount=Decimal(row["limit"]),
                    source=self.source(self.settings.data_dir / "positions/rates_limits.csv", line),
                )
            )
        if not positions:
            raise ValueError("Empty book snapshot")
        needed = {p.curve_bucket for p in positions} | {"TOTAL"}
        if not needed.issubset({v.bucket for v in limits}):
            raise ValueError("Missing limits")
        return Book(
            book=book,
            as_of=as_of,
            positions=positions,
            limits=limits,
            series=sorted(series),
            warnings=warnings,
        )

    def market(self, book: str, as_of: date, series: list[str]) -> Market:
        self.authorize(book)
        rows = self.rows("market_data/rates_eod.csv", ["date"])
        dates = sorted(date.fromisoformat(r["date"]) for _, r in rows)
        earlier = [d for d in dates if d < as_of]
        if as_of not in dates or not earlier:
            raise ValueError("Missing current or previous close")

        def observations(day: date) -> list[Observation]:
            line, row = next((n, r) for n, r in rows if r["date"] == day.isoformat())
            return [
                Observation(
                    series=s,
                    value=Decimal(row[s]),
                    source=self.source(
                        self.settings.data_dir / "market_data/rates_eod.csv", line, day
                    ),
                )
                for s in series
            ]

        fx = [
            Observation(
                series=r["pair"],
                value=Decimal(r["rate"]),
                source=self.source(
                    self.settings.data_dir / "market_data/fx_rates.csv",
                    line,
                    date.fromisoformat(r["date"]),
                ),
            )
            for line, r in self.rows("market_data/fx_rates.csv", ["date", "pair"])
        ]
        return Market(current=observations(as_of), previous=observations(earlier[-1]), fx=fx)

    def research(self, book: str, as_of: date, regions: list[str]) -> Research:
        self.authorize(book)
        documents = []
        for path in sorted((self.settings.data_dir / "research").glob("*.md")):
            # Read only front matter until identity and relevance checks pass.
            with path.open(encoding="utf-8") as stream:
                if stream.readline().strip() != "---":
                    raise ValueError("Missing research front matter")
                header = []
                for line in stream:
                    if line.strip() == "---":
                        break
                    header.append(line)
                meta: dict[str, Any] = yaml.safe_load("".join(header))
                if (
                    meta["source"] not in self.identity["research_licences"]
                    or str(meta["date"]) != str(as_of)
                    or meta["region"] not in regions
                ):
                    continue
                remaining = stream.read().splitlines()
                first_text = next((i for i, text in enumerate(remaining) if text.strip()), 0)
                body = "\n".join(remaining).strip()
            documents.append(
                Document(
                    document_id=path.stem,
                    title=meta["title"],
                    provider=meta["source"],
                    region=meta["region"],
                    body=body,
                    source=self.source(path, len(header) + 3 + first_text, as_of),
                )
            )
        return Research(documents=documents, licences=self.identity["research_licences"])
