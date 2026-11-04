import html
from decimal import Decimal

from rates_brief.models import Book, Bucket, Market, ModelResult, Research, Risk, Source


def safe(text: str) -> str:
    return html.escape(text).replace("|", "\\|").replace("\n", " ")


def money(value: Decimal) -> str:
    return f"{value:,.2f}"


def source(ref: Source) -> str:
    return f"`{ref.path}:{ref.row}` (as of {ref.as_of or 'undated limit configuration'})"


def risk_table(buckets: list[Bucket]) -> list[str]:
    return [
        "| Bucket | Net USD DV01 | Limit | Utilization | Headroom | Status |",
        "|---|---:|---:|---:|---:|---|",
    ] + [
        f"| {b.bucket} | {money(b.net)} | {money(b.limit)} | "
        f"{b.utilization:.1%} | {money(b.headroom)} | {b.status} |"
        for b in buckets
    ]


def render(
    user: str,
    request_id: str,
    book: Book,
    market: Market,
    research: Research,
    risk: Risk,
    model: ModelResult,
) -> str:
    out = [
        f"# Rates morning brief — {safe(user)}",
        "",
        f"Book: **{book.book}** · Snapshot: **{book.as_of}** · Request: `{request_id}`",
        "",
        f"Research mode: **{model.mode}**. "
        + (
            "No model call was made; the research text below is quoted source material."
            if model.mode == "offline stub"
            else ""
        ),
        "",
        "Synthetic data; end-of-day snapshot, not an intraday risk monitor.",
        "",
    ]
    if model.warning:
        out.extend([f"**{model.warning}**", ""])
    out.extend(
        [
            "## Risk and limits",
            "",
            *risk_table(risk.buckets),
            "",
            f"Warning at {risk.warning_utilization:.1%} utilization "
            "(configurable demonstration assumption; confirm with the PM). "
            "This flag reflects the supplied snapshot; it does not send a notification.",
            "",
            "DV01 is USD profit/loss for a one-basis-point fall in yields. "
            "Limits apply to absolute net DV01. Total nets all signed position exposures.",
            "",
            "Limits: " + "; ".join(source(v.source) for v in book.limits),
            "",
            "### Currency contributions",
            "",
            "| Source currency | Net DV01 converted to USD |",
            "|---|---:|",
        ]
    )
    out += [f"| {c} | {money(v)} |" for c, v in sorted(risk.by_currency.items())]
    out += [
        "",
        "Cross-currency offsets follow the supplied limit definition; "
        "they do not establish protection against independent curve moves.",
        "",
    ]
    out += [
        "## Market closes",
        "",
        "Changes are close-to-close against the previous available observation.",
        "",
        "| Series | Latest (%) | Previous (%) | Change (bp) |",
        "|---|---:|---:|---:|",
    ]
    current = {v.series: v for v in market.current}
    previous = {v.series: v for v in market.previous}
    for name, obs in current.items():
        prev = previous[name]
        out.append(
            f"| {name} | {obs.value:.3f} | {prev.value:.3f} | "
            f"{(obs.value - prev.value) * 100:+.2f} |"
        )
    out += [
        "",
        "Sources: " + "; ".join(source(v.source) for v in [market.current[0], market.previous[0]])
        if market.current
        else "No mapped series.",
        "",
        "### Derived spreads",
        "",
        "| Spread | Latest (bp) | Change (bp) |",
        "|---|---:|---:|",
    ]
    for label, a, b in [
        ("US 2s10s", "UST_10Y", "UST_2Y"),
        ("US 5s30s", "UST_30Y", "UST_5Y"),
        ("US 10Y swap spread", "SOFR_SWAP_10Y", "UST_10Y"),
        ("UK 10Y swap spread", "SONIA_SWAP_10Y", "GILT_10Y"),
    ]:
        if a in current and b in current:
            value = (current[a].value - current[b].value) * 100
            old = (previous[a].value - previous[b].value) * 100
            out.append(f"| {label} ({a} − {b}) | {value:.2f} | {value - old:+.2f} |")
    out += [
        "",
        "Spreads use the same dated observations cited above.",
        "",
        "## Research for your positions",
        "",
        "Your licensed providers: " + ", ".join(research.licences) + ". "
        "Only same-date, relevant, licensed documents are included. "
        "Research quotes are source assertions and may differ from the market closes above.",
        "",
    ]
    summaries = {s.document_id: s for s in model.summaries.items}
    for index, doc in enumerate(research.documents, start=1):
        item = summaries[doc.document_id]
        out += [
            f"### [{index}] {safe(doc.title)}",
            "",
            f"**{safe(doc.provider)}** · {doc.source.as_of} · {source(doc.source)}",
            "",
            ("> " if model.mode != "live" else "") + safe(item.view),
            "",
            f"Positions: {', '.join(item.position_ids)}. {safe(item.relevance)}",
            "",
        ]
    if not research.documents:
        out += ["No authorized research matched the date and supported position regions.", ""]
    out += [
        "## DV01 conversion appendix",
        "",
        "USD DV01 = supplied DV01 × unit scale × USD per source currency. "
        "Inverse quotes use 1 / quoted FX rate. USD uses an identity conversion.",
        "",
        "| Position | Instrument | Raw DV01 | Currency / unit | Scale | FX quote | "
        "USD per currency | USD DV01 | Sources |",
        "|---|---|---:|---|---:|---|---:|---:|---|",
    ]
    for c in risk.converted:
        p = c.position
        refs = source(p.source) + ("; " + source(c.fx_source) if c.fx_source else "; USD identity")
        out.append(
            f"| {p.position_id} | {safe(p.instrument)} | {p.dv01} | "
            f"{p.dv01_ccy} / {p.dv01_unit} | {c.scale} | {c.fx_pair}={c.fx_rate}"
            f"{' (inverse)' if c.inverse else ''} | {c.usd_per_currency} | "
            f"{money(c.usd_dv01)} | {refs} |"
        )
    out += [
        "",
        "## Coverage and limitations",
        "",
        "- Position relevance uses configured instrument regions; it is not a hedge model.",
        "- Older research is excluded from this morning's view.",
        "- Limit files have no effective date; the supplied configuration is assumed applicable.",
        "- Source content hashes, calculations, and this exact response are retained in the audit.",
    ]
    out += [f"- {safe(w)}" for w in book.warnings]
    return "\n".join(out) + "\n"
