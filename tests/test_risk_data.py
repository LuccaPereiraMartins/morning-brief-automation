from datetime import date, timedelta
from decimal import Decimal as D

import pytest

from rates_brief.data import Data
from rates_brief.risk import bucket, calculate
from rates_brief.settings import FXPair, Settings

DAY = date(2026, 10, 28)


@pytest.mark.parametrize(
    ("net", "expected"),
    [
        ("89", "within limit"),
        ("90", "approaching limit"),
        ("100", "approaching limit"),
        ("101", "breached"),
        ("-90", "approaching limit"),
        ("-101", "breached"),
    ],
)
def test_warning_and_breach_boundaries(net: str, expected: str) -> None:
    assert bucket("5Y", D(net), D(100), D("0.9")).status == expected


def test_warning_setting_validation(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIMIT_WARNING_UTILIZATION", "0.95")
    assert Settings.from_env().limit_warning_utilization == D("0.95")
    monkeypatch.setenv("LIMIT_WARNING_UTILIZATION", "1.1")
    with pytest.raises(ValueError):
        Settings.from_env()


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
        for doc in docs:
            lines = (settings.data_dir / doc.source.path).read_text().splitlines()
            assert lines[doc.source.row - 1] == doc.body.splitlines()[0]
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
