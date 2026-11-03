from collections import defaultdict
from decimal import Decimal

from rates_brief.models import Book, Bucket, Converted, Market, Risk
from rates_brief.settings import Conventions


def bucket(name: str, net: Decimal, limit: Decimal) -> Bucket:
    return Bucket(
        bucket=name,
        net=net,
        limit=limit,
        headroom=limit - abs(net),
        utilization=abs(net) / limit,
        status="breached" if abs(net) > limit else "within limit",
    )


def calculate(book: Book, market: Market, config: Conventions) -> Risk:
    converted = []
    nets: dict[str, Decimal] = defaultdict(Decimal)
    currencies: dict[str, Decimal] = defaultdict(Decimal)
    for position in book.positions:
        if position.dv01_unit not in config.unit_scales:
            raise ValueError(f"Unknown DV01 unit: {position.dv01_unit}")
        scale = config.unit_scales[position.dv01_unit]
        pair, rate, inverse, source = "USD/USD", Decimal(1), False, None
        if position.dv01_ccy != "USD":
            if position.dv01_ccy not in config.fx_pairs:
                raise ValueError("Missing currency mapping")
            mapping = config.fx_pairs[position.dv01_ccy]
            choices = [
                o
                for o in market.fx
                if o.series == mapping.pair
                and o.source.as_of is not None
                and o.source.as_of <= book.as_of
            ]
            if not choices:
                raise ValueError("Missing FX on or before snapshot date")
            observation = max(choices, key=lambda o: str(o.source.as_of))
            assert observation.source.as_of is not None
            if (book.as_of - observation.source.as_of).days > config.fx_max_age_days:
                raise ValueError("Stale FX")
            pair, rate, inverse, source = (
                mapping.pair,
                observation.value,
                mapping.inverse,
                observation.source,
            )
            if rate <= 0:
                raise ValueError("FX must be positive")
        factor = Decimal(1) / rate if inverse else rate
        usd = position.dv01 * scale * factor
        converted.append(
            Converted(
                position=position,
                scale=scale,
                fx_pair=pair,
                fx_rate=rate,
                inverse=inverse,
                usd_per_currency=factor,
                fx_source=source,
                usd_dv01=usd,
            )
        )
        nets[position.curve_bucket] += usd
        currencies[position.dv01_ccy] += usd
    nets["TOTAL"] = sum(nets.values(), Decimal(0))
    return Risk(
        converted=converted,
        by_currency=dict(currencies),
        buckets=[bucket(limit.bucket, nets[limit.bucket], limit.amount) for limit in book.limits],
    )


def scenario(risk: Risk, name: str, delta: Decimal) -> list[Bucket]:
    if name == "TOTAL" or name not in {b.bucket for b in risk.buckets}:
        raise ValueError("Scenario requires an existing maturity bucket")
    if not delta.is_finite():
        raise ValueError("Scenario DV01 must be finite")
    return [
        bucket(b.bucket, b.net + (delta if b.bucket in (name, "TOTAL") else 0), b.limit)
        for b in risk.buckets
    ]
