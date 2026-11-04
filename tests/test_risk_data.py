from datetime import date, timedelta
from decimal import Decimal as D

import pytest

from rates_brief.data import Data
from rates_brief.risk import bucket, calculate
from rates_brief.settings import FXPair, Settings

DAY = date(2026, 10, 28)


def test_warning_boundaries_and_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    for net, expected in [
        ("89", "within limit"),
        ("90", "approaching limit"),
        ("100", "approaching limit"),
        ("101", "breached"),
        ("-90", "approaching limit"),
        ("-101", "breached"),
    ]:
        assert bucket("5Y", D(net), D(100), D("0.9")).status == expected
    monkeypatch.setenv("LIMIT_WARNING_UTILIZATION", "0.95")
    assert Settings.from_env().limit_warning_utilization == D("0.95")
    monkeypatch.setenv("LIMIT_WARNING_UTILIZATION", "1.1")
    with pytest.raises(ValueError):
        Settings.from_env()


@pytest.mark.parametrize("change", ["missing_fx", "stale_fx", "unknown_unit"])
def test_invalid_risk_input_fails(settings: Settings, change: str) -> None:
    data = Data(settings, "tom")
    book = data.book("RATES_RV", DAY)
    market = data.market(book.book, DAY, book.series)
    gbp = next(o for o in market.fx if o.series == "GBPUSD")
    if change == "missing_fx":
        market.fx.remove(gbp)
    elif change == "stale_fx":
        gbp.source.as_of = DAY - timedelta(days=1)
    else:
        book.positions[0].dv01_unit = "unknown"
    with pytest.raises(ValueError):
        calculate(book, market, data.config)


def test_inverse_fx(settings: Settings) -> None:
    data = Data(settings, "tom")
    book = data.book("RATES_RV", DAY)
    market = data.market(book.book, DAY, book.series)
    gbp = next(o for o in market.fx if o.series == "GBPUSD")
    gbp.series, gbp.value = "USDGBP", D("0.8")
    data.config.fx_pairs["GBP"] = FXPair(pair="USDGBP", inverse=True)
    converted = calculate(book, market, data.config).converted
    assert next(c for c in converted if c.position.position_id == "R-005").usd_dv01 == D(64750)


def test_duplicate_positions_fail(settings: Settings) -> None:
    path = settings.data_dir / "positions/rates_rv_2026-10-28.csv"
    path.write_text(path.read_text() + path.read_text().splitlines()[1] + "\n")
    with pytest.raises(ValueError, match="Duplicate"):
        Data(settings, "tom").book("RATES_RV", DAY)
