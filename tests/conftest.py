import shutil
from pathlib import Path

import pytest

from rates_brief.settings import Settings


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    shutil.copytree("data", tmp_path / "data")
    return Settings(
        data_dir=tmp_path / "data",
        source_config=Path("config/sources.yaml").resolve(),
        audit_dir=tmp_path / "audit",
        llm_mode="offline",
        llm_model="",
    )
