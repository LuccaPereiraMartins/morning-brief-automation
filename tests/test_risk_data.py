from datetime import date, timedelta
from decimal import Decimal as D

import pytest

from rates_brief.data import Data
from rates_brief.risk import bucket, calculate, scenario
from rates_brief.settings import FXPair, Settings

DAY = date(2026, 10, 28)


def test_supplied_risk_and_scenario(settings: Settings) -> None:
    data = Data(settings, "tom")
    book = data.book("RATES_RV", DAY)
    market = data.market(book.book, DAY, book.series)
    risk = calculate(book, market, data.config)
    assert {b.bucket: b.net for b in risk.buckets} == {
        "5Y": D("69500"),
        "10Y": D("48557.04"),
        "30Y": D("21150.08"),
        "TOTAL": D("139207.12"),
    }
    amounts = {c.position.position_id: c.usd_dv01 for c in risk.converted}
    assert amounts["R-002"] == D("73200")
    assert amounts["R-006"] == D("-52049.92")
    after = {b.bucket: b for b in scenario(risk, "10Y", D(20000))}
    assert after["TOTAL"].headroom == D("-9207.12")
    assert after["10Y"].status == "within limit"
    assert bucket("5Y", D(-110), D(100)).status == "breached"
    assert bucket("5Y", D(-100), D(100)).headroom == 0
    with pytest.raises(ValueError):
        scenario(risk, "TOTAL", D(1))


@pytest.mark.parametrize("change", ["missing", "stale", "future", "zero", "negative", "unit"])
def test_conversion_failures(settings: Settings, change: str) -> None:
    data = Data(settings, "tom")
    book = data.book("RATES_RV", DAY)
    market = data.market(book.book, DAY, book.series)
    gbp = next(o for o in market.fx if o.series == "GBPUSD")
    if change == "missing":
        market.fx.remove(gbp)
    elif change in ("stale", "future"):
        gbp.source.as_of = DAY + timedelta(days=1 if change == "future" else -1)
    elif change in ("zero", "negative"):
        gbp.value = D(0 if change == "zero" else -1)
    else:
        book.positions[0].dv01_unit = "unknown"
    with pytest.raises(ValueError):
        calculate(book, market, data.config)


def test_inverse_and_configurable_age(settings: Settings) -> None:
    data = Data(settings, "tom")
    book = data.book("RATES_RV", DAY)
    market = data.market(book.book, DAY, book.series)
    gbp = next(o for o in market.fx if o.series == "GBPUSD")
    gbp.series, gbp.value = "USDGBP", D("0.8")
    gbp.source.as_of = DAY - timedelta(days=1)
    data.config.fx_pairs["GBP"] = FXPair(pair="USDGBP", inverse=True)
    data.config.fx_max_age_days = 1
    converted = calculate(book, market, data.config).converted
    assert next(c for c in converted if c.position.position_id == "R-005").usd_dv01 == D(64750)


def test_research_and_access(settings: Settings) -> None:
    for user, expected in [
        ("tom", {"Bank A", "Bank B", "Bank C", "Internal"}),
        ("jim", {"Bank A", "Internal"}),
    ]:
        data = Data(settings, user)
        docs = data.research("RATES_RV", DAY, ["US", "UK", "Euro area", "Global"]).documents
        assert {d.provider for d in docs} == expected
        assert all(d.source.as_of == DAY for d in docs)
        assert not any("jgb" in d.document_id or "2026-10-21" in d.document_id for d in docs)
    with pytest.raises(PermissionError):
        Data(settings, "unknown")
    with pytest.raises(PermissionError):
        Data(settings, "sara").book("RATES_RV", DAY)


@pytest.mark.parametrize("change", ["duplicate", "missing_limit", "wrong_date"])
def test_bad_inputs(settings: Settings, change: str) -> None:
    path = settings.data_dir / "positions/rates_rv_2026-10-28.csv"
    if change == "duplicate":
        lines = path.read_text().splitlines()
        path.write_text("\n".join(lines + [lines[1]]) + "\n")
    elif change == "wrong_date":
        path.write_text(path.read_text().replace("2026-10-28", "2026-10-27"))
    else:
        path = settings.data_dir / "positions/rates_limits.csv"
        path.write_text("\n".join(path.read_text().splitlines()[:-1]) + "\n")
    with pytest.raises(ValueError):
        Data(settings, "tom").book("RATES_RV", DAY)


def test_new_position_identity_and_unsupported_mapping(settings: Settings) -> None:
    path = settings.data_dir / "positions/rates_rv_2026-10-28.csv"
    path.write_text(path.read_text().replace("R-001", "R-NEW").replace("08/15/31", "08/15/32"))
    book = Data(settings, "tom").book("RATES_RV", DAY)
    assert book.positions[0].region == "US"
    path.write_text(path.read_text().replace("US Treasury 5Y", "New instrument"))
    assert Data(settings, "tom").book("RATES_RV", DAY).warnings
