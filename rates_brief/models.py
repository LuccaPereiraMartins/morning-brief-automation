from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Source(Record):
    path: str
    row: int
    sha256: str
    as_of: date | None = None


class Position(Record):
    position_id: str
    instrument: str
    description: str
    dv01: Decimal
    dv01_ccy: str
    dv01_unit: str
    curve_bucket: str
    region: str
    source: Source


class Limit(Record):
    bucket: str
    amount: Decimal = Field(gt=0)
    source: Source


class Book(Record):
    book: str
    as_of: date
    positions: list[Position]
    limits: list[Limit]
    series: list[str]
    warnings: list[str]


class Observation(Record):
    series: str
    value: Decimal
    source: Source


class Market(Record):
    current: list[Observation]
    previous: list[Observation]
    fx: list[Observation]


class Document(Record):
    document_id: str
    title: str
    provider: str
    region: str
    body: str
    source: Source


class Research(Record):
    documents: list[Document]
    licences: list[str]


class Converted(Record):
    position: Position
    scale: Decimal
    fx_pair: str
    fx_rate: Decimal
    inverse: bool
    usd_per_currency: Decimal
    fx_source: Source | None
    usd_dv01: Decimal


class Bucket(Record):
    bucket: str
    net: Decimal
    limit: Decimal
    headroom: Decimal
    utilization: Decimal
    status: Literal["within limit", "breached"]


class Risk(Record):
    converted: list[Converted]
    buckets: list[Bucket]
    by_currency: dict[str, Decimal]


class Summary(Record):
    document_id: str
    position_ids: list[str]
    view: str
    relevance: str


class Summaries(Record):
    items: list[Summary]


class ModelResult(Record):
    mode: str
    summaries: Summaries
    warning: str | None = None
