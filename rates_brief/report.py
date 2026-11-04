import html
import re
from decimal import Decimal

from rates_brief.models import Book, Market, ModelResult, Research, Risk, Source


def safe(text: str) -> str:
    return html.escape(text).replace("|", "\\|").replace("\n", " ")


def money(value: Decimal) -> str:
    return f"{value:,.2f}"


def source(ref: Source) -> str:
    return f"`{ref.path}:{ref.row}` ({ref.as_of or 'undated'})"


def excerpt(text: str) -> str:
    # The offline path quotes a short opening; it does not pretend to summarize.
    sentence = re.split(r"(?<=[.!?])\s+", text.strip())[0]
    return sentence if len(sentence) <= 260 else sentence[:257].rsplit(" ", 1)[0] + "…"


def render(
    user: str,
    request_id: str,
    book: Book,
    market: Market,
    research: Research,
    risk: Risk,
    model: ModelResult,
) -> str:
    out = [f"# Rates — {book.as_of} — {safe(user)}", "", f"{book.book} · EOD · {model.mode}", ""]
    for b in risk.buckets:
        if b.bucket == "TOTAL" or b.status != "within limit":
            out += [
                f"**{b.bucket}: {b.status} — {b.utilization:.1%} used; "
                f"USD {money(b.headroom)}/bp headroom.**",
                "",
            ]
    if model.warning:
        out += [f"**{model.warning}**", ""]
    out += ["## Research", ""]
    summaries = {s.document_id: s for s in model.summaries.items}
    for i, doc in enumerate(research.documents, start=1):
        item = summaries[doc.document_id]
        view = item.view if model.mode == "live" else "“" + excerpt(item.view) + "”"
        relevance = " " + safe(item.relevance) if model.mode == "live" else ""
        out.append(
            f"- **{safe(doc.provider)} / {safe(doc.region)}:** {safe(view)}"
            f"{relevance} ({', '.join(item.position_ids)}; [{i}])"
        )
    if not research.documents:
        out.append("No matching licensed research.")
    out += ["", "## DV01 — USD/bp", "", "| Bucket | Net | Limit | Used |", "|---|---:|---:|---:|"]
    out += [
        f"| {b.bucket} | {money(b.net)} | {money(b.limit)} | {b.utilization:.1%} |"
        for b in risk.buckets
    ]
    out += ["", f"Warning ≥{risk.warning_utilization:.1%} (demo policy); breach >100%."]
    out += [f"- {safe(w)}" for w in book.warnings]
    out += [
        "",
        "<details>",
        "<summary>Market closes and sources</summary>",
        "",
        "Levels in %, changes in bp versus the previous close.",
        "",
        "| Series | Close | Δ bp |",
        "|---|---:|---:|",
    ]
    previous = {v.series: v for v in market.previous}
    current = {v.series: v for v in market.current}
    for name, obs in current.items():
        change = (obs.value - previous[name].value) * 100
        out.append(f"| {name} | {obs.value:.3f} | {change:+.2f} |")
    out.append("")
    for label, long, short in [
        ("US 2s10s", "UST_10Y", "UST_2Y"),
        ("US 5s30s", "UST_30Y", "UST_5Y"),
    ]:
        if long in current and short in current:
            out.append(f"{label}: {(current[long].value - current[short].value) * 100:.2f}bp.")
    if market.current:
        out += [
            "",
            "Market: "
            + source(market.current[0].source)
            + "; previous: "
            + source(market.previous[0].source),
        ]
    out += ["", "Research references (quotes are broker views, not official closes):"]
    out += [
        f"- [{i}] {safe(d.title)} — {source(d.source)}"
        for i, d in enumerate(research.documents, start=1)
    ]
    out += [
        "",
        "</details>",
        "",
        "<details>",
        "<summary>DV01 conversions and audit</summary>",
        "",
        "USD DV01 = raw DV01 × unit scale × USD per currency; signs are preserved.",
        "",
        "| Position | Raw / currency / unit | FX quote | USD DV01 | Sources |",
        "|---|---|---|---:|---|",
    ]
    for c in risk.converted:
        p = c.position
        refs = source(p.source) + ("; " + source(c.fx_source) if c.fx_source else "; USD identity")
        out.append(
            f"| {p.position_id} | {p.dv01} / {p.dv01_ccy} / {p.dv01_unit} | "
            f"{c.fx_pair}={c.fx_rate}{' (inverse)' if c.inverse else ''} | "
            f"{money(c.usd_dv01)} | {refs} |"
        )
    out += [
        "",
        "Currency contributions (USD/bp): "
        + "; ".join(
            f"{currency}: {money(value)}" for currency, value in sorted(risk.by_currency.items())
        ),
        "",
        "Limits (absolute signed net; total nets across currencies/curves): "
        + "; ".join(source(v.source) for v in book.limits),
        "",
        f"Audit request: `{request_id}`. Local synthetic snapshot; no intraday notifications.",
        "",
        "</details>",
    ]
    return "\n".join(out) + "\n"
