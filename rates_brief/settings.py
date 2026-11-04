import os
from decimal import Decimal
from pathlib import Path

import yaml
from pydantic import Field

from rates_brief.models import Record

DEFAULT_WARNING_UTILIZATION = Decimal("0.90")


class FXPair(Record):
    pair: str
    inverse: bool


class InstrumentRule(Record):
    pattern: str
    region: str
    series: list[str]


class Conventions(Record):
    unit_scales: dict[str, Decimal]
    fx_max_age_days: int = Field(ge=0)
    fx_pairs: dict[str, FXPair]
    instruments: list[InstrumentRule]


class Settings(Record):
    data_dir: Path
    source_config: Path
    audit_dir: Path
    llm_mode: str
    llm_model: str
    limit_warning_utilization: Decimal = Field(default=DEFAULT_WARNING_UTILIZATION, gt=0, le=1)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            data_dir=Path(os.getenv("DATA_DIR", "data")).resolve(),
            source_config=Path(os.getenv("SOURCE_CONFIG", "config/sources.yaml")).resolve(),
            audit_dir=Path(os.getenv("AUDIT_DIR", "audit")).resolve(),
            llm_mode=os.getenv("LLM_MODE", "live" if os.getenv("OPENAI_API_KEY") else "offline"),
            llm_model=os.getenv("LLM_MODEL", ""),
            limit_warning_utilization=Decimal(
                os.getenv("LIMIT_WARNING_UTILIZATION", str(DEFAULT_WARNING_UTILIZATION))
            ),
        )

    def conventions(self) -> Conventions:
        config = Conventions.model_validate(yaml.safe_load(self.source_config.read_text()))
        if any(v <= 0 or not v.is_finite() for v in config.unit_scales.values()):
            raise ValueError("Unit scales must be positive finite numbers")
        return config
